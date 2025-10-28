from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import PGVector, Pinecone as LangchainPinecone
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from loguru import logger

from app.core.config import settings


class GTMRetriever:
    """Custom retrieval system for GTM (Go-To-Market) data with hybrid search"""
    
    def __init__(self, use_pinecone: bool = True):
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.use_pinecone = use_pinecone
        
        if use_pinecone:
            self.vectorstore = self._init_pinecone()
        else:
            self.vectorstore = self._init_pgvector()
        
        self.base_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20}
        )
        
        self.compressor = LLMChainExtractor.from_llm(
            ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        )
        
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor,
            base_retriever=self.base_retriever
        )
    
    def _init_pinecone(self):
        """Initialize Pinecone vector store"""
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        index_name = "gtm-knowledge"
        
        return LangchainPinecone.from_existing_index(
            index_name=index_name,
            embedding=self.embeddings
        )
    
    def _init_pgvector(self):
        """Initialize PGVector store"""
        return PGVector(
            connection_string=settings.database_url,
            embedding_function=self.embeddings,
            collection_name="gtm_documents"
        )
    
    async def search(self, query: str, use_compression: bool = True) -> str:
        """Search GTM knowledge base"""
        logger.info(f"Searching GTM knowledge: {query}")
        
        retriever = self.compression_retriever if use_compression else self.base_retriever
        docs = await retriever.aget_relevant_documents(query)
        
        results = "\n\n".join([doc.page_content for doc in docs])
        return results
    
    async def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add new documents to knowledge base"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        splits = text_splitter.create_documents(documents, metadatas=metadatas)
        
        await self.vectorstore.aadd_documents(splits)
        logger.info(f"Added {len(splits)} document chunks to knowledge base")
    
    async def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search with scores"""
        results = await self.vectorstore.asimilarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]


class HybridRetriever:
    """Hybrid retrieval combining vector search with keyword search"""
    
    def __init__(self):
        self.gtm_retriever = GTMRetriever()
    
    async def retrieve(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Hybrid retrieval with filtering"""
        semantic_results = await self.gtm_retriever.semantic_search(query)
        
        if filters:
            semantic_results = [
                r for r in semantic_results
                if all(r['metadata'].get(k) == v for k, v in filters.items())
            ]
        
        return semantic_results
