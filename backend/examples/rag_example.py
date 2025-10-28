"""Example: RAG (Retrieval-Augmented Generation)"""
import asyncio
from app.rag.retriever import GTMRetriever, HybridRetriever


async def main():
    retriever = GTMRetriever(use_pinecone=False)  # Use pgvector
    
    # Example 1: Add documents to knowledge base
    print("=== Example 1: Adding Documents ===")
    documents = [
        "Our AI platform helps sales teams automate outreach and improve conversion rates by 40%.",
        "Key features include: real-time voice AI, adaptive learning, and multi-channel orchestration.",
        "Pricing starts at $999/month for up to 10 users.",
        "Case study: TechCorp increased their pipeline by 3x in 6 months using our platform."
    ]
    
    metadatas = [
        {"type": "product_info", "category": "overview"},
        {"type": "product_info", "category": "features"},
        {"type": "pricing", "category": "plans"},
        {"type": "case_study", "category": "success_stories"}
    ]
    
    await retriever.add_documents(documents, metadatas)
    print("Documents added successfully!")
    
    # Example 2: Search knowledge base
    print("\n=== Example 2: Searching Knowledge Base ===")
    query = "What are the key features of the platform?"
    results = await retriever.search(query)
    print(f"Query: {query}")
    print(f"Results:\n{results}")
    
    # Example 3: Semantic search with scores
    print("\n=== Example 3: Semantic Search with Scores ===")
    semantic_results = await retriever.semantic_search(
        "customer success stories",
        k=3
    )
    for idx, result in enumerate(semantic_results, 1):
        print(f"\n{idx}. Score: {result['score']:.4f}")
        print(f"Content: {result['content'][:100]}...")
        print(f"Metadata: {result['metadata']}")
    
    # Example 4: Hybrid retrieval with filters
    print("\n=== Example 4: Hybrid Retrieval with Filters ===")
    hybrid_retriever = HybridRetriever()
    filtered_results = await hybrid_retriever.retrieve(
        "pricing information",
        filters={"type": "pricing"}
    )
    for result in filtered_results:
        print(f"Content: {result['content']}")


if __name__ == "__main__":
    asyncio.run(main())
