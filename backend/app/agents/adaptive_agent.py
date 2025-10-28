from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from loguru import logger

from app.core.config import settings
from app.rag.retriever import GTMRetriever
from app.services.memory_service import AdaptiveMemoryService


class AdaptiveAgent:
    """Base class for adaptive AI agents that learn and improve over time"""
    
    def __init__(
        self,
        agent_type: str,
        model_provider: str = "openai",
        temperature: float = 0.7,
        enable_memory: bool = True
    ):
        self.agent_type = agent_type
        self.model_provider = model_provider
        self.temperature = temperature
        self.enable_memory = enable_memory
        
        self.llm = self._initialize_llm()
        self.memory = AdaptiveMemoryService() if enable_memory else None
        self.retriever = GTMRetriever()
        self.tools = self._initialize_tools()
        
    def _initialize_llm(self):
        if self.model_provider == "openai":
            return ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=self.temperature,
                api_key=settings.OPENAI_API_KEY
            )
        elif self.model_provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=self.temperature,
                api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools available to the agent"""
        return [
            Tool(
                name="search_gtm_knowledge",
                func=self.retriever.search,
                description="Search GTM knowledge base for relevant information about sales, outreach, and customer interactions"
            ),
            Tool(
                name="analyze_conversation",
                func=self._analyze_conversation,
                description="Analyze past conversations to extract insights and patterns"
            ),
        ]
    
    async def _analyze_conversation(self, query: str) -> str:
        """Analyze conversation patterns from memory"""
        if self.memory:
            insights = await self.memory.get_insights(query)
            return insights
        return "Memory service not enabled"
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute agent task with adaptive learning"""
        logger.info(f"Executing {self.agent_type} agent task: {task}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an adaptive AI agent specialized in {self.agent_type}. Learn from every interaction and continuously improve."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )
        
        result = await agent_executor.ainvoke({
            "input": task,
            "chat_history": []
        })
        
        if self.memory:
            await self.memory.store_interaction(task, result, self.agent_type)
        
        return result


class SalesAgent(AdaptiveAgent):
    """Specialized agent for sales conversations"""
    
    def __init__(self):
        super().__init__(agent_type="sales", model_provider="openai")
        
    def _initialize_tools(self) -> List[Tool]:
        tools = super()._initialize_tools()
        tools.extend([
            Tool(
                name="get_customer_profile",
                func=self._get_customer_profile,
                description="Retrieve customer profile and interaction history"
            ),
            Tool(
                name="suggest_next_action",
                func=self._suggest_next_action,
                description="Suggest next best action based on conversation context"
            ),
        ])
        return tools
    
    async def _get_customer_profile(self, customer_id: str) -> str:
        return f"Customer profile for {customer_id}"
    
    async def _suggest_next_action(self, context: str) -> str:
        return "Suggested next action based on context"


class OutboundEmailAgent(AdaptiveAgent):
    """Specialized agent for outbound email campaigns"""
    
    def __init__(self):
        super().__init__(agent_type="outbound_email", model_provider="anthropic")
        
    async def generate_email(self, prospect_info: Dict[str, Any]) -> str:
        """Generate personalized outbound email"""
        task = f"Generate personalized outbound email for: {prospect_info}"
        result = await self.execute(task)
        return result.get("output", "")
