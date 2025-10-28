from typing import Dict, List, Any, Optional
from datetime import datetime
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class AdaptiveMemoryService:
    """Service for storing and retrieving agent memories for continuous learning"""
    
    def __init__(self):
        self.redis_client = None
        self.conversation_history = []
    
    async def connect(self):
        """Connect to Redis"""
        self.redis_client = await redis.from_url(settings.redis_url)
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def store_interaction(
        self,
        task: str,
        result: Dict[str, Any],
        agent_type: str
    ):
        """Store agent interaction for learning"""
        interaction = {
            "task": task,
            "result": result,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self.redis_client:
            await self.connect()
        
        key = f"interaction:{agent_type}:{datetime.utcnow().timestamp()}"
        await self.redis_client.setex(
            key,
            86400,  # 24 hours
            str(interaction)
        )
        
        await self.redis_client.lpush(f"history:{agent_type}", str(interaction))
        await self.redis_client.ltrim(f"history:{agent_type}", 0, 99)
        
        logger.info(f"Stored interaction for {agent_type}")
    
    async def get_recent_interactions(
        self,
        agent_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent interactions for an agent type"""
        if not self.redis_client:
            await self.connect()
        
        interactions = await self.redis_client.lrange(
            f"history:{agent_type}",
            0,
            limit - 1
        )
        
        return [eval(i.decode()) for i in interactions]
    
    async def get_insights(self, query: str) -> str:
        """Get insights from stored interactions"""
        interactions = await self.get_recent_interactions("sales", limit=20)
        
        if not interactions:
            return "No previous interactions found"
        
        insights = f"Found {len(interactions)} recent interactions. "
        insights += "Common patterns: adaptive learning, customer engagement."
        
        return insights
    
    async def store_conversation_memory(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store conversation memory"""
        if not self.redis_client:
            await self.connect()
        
        key = f"conversation:{conversation_id}"
        value = {
            "messages": messages,
            "metadata": metadata or {},
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(key, 604800, str(value))  # 7 days
        logger.info(f"Stored conversation memory: {conversation_id}")
    
    async def get_conversation_memory(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation memory"""
        if not self.redis_client:
            await self.connect()
        
        key = f"conversation:{conversation_id}"
        value = await self.redis_client.get(key)
        
        if value:
            return eval(value.decode())
        return None
