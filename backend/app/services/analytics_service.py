import clickhouse_connect
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.core.config import settings


class AnalyticsService:
    """ClickHouse-based analytics for tracking agent performance and learning"""
    
    def __init__(self):
        self.client = None
    
    def connect(self):
        """Connect to ClickHouse"""
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DB
        )
        logger.info("Connected to ClickHouse")
    
    def create_tables(self):
        """Create analytics tables"""
        if not self.client:
            self.connect()
        
        # Agent interactions table
        self.client.command("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id String,
                agent_type String,
                task String,
                result String,
                duration_ms UInt32,
                success Boolean,
                timestamp DateTime,
                metadata String
            ) ENGINE = MergeTree()
            ORDER BY (agent_type, timestamp)
        """)
        
        # Voice calls table
        self.client.command("""
            CREATE TABLE IF NOT EXISTS voice_calls (
                call_id String,
                room_name String,
                participant_id String,
                duration_seconds UInt32,
                transcript String,
                sentiment_score Float32,
                outcome String,
                timestamp DateTime,
                metadata String
            ) ENGINE = MergeTree()
            ORDER BY (timestamp, call_id)
        """)
        
        # Email campaigns table
        self.client.command("""
            CREATE TABLE IF NOT EXISTS email_campaigns (
                campaign_id String,
                email_id String,
                recipient String,
                subject String,
                sent_at DateTime,
                opened Boolean,
                clicked Boolean,
                replied Boolean,
                response_text String,
                metadata String
            ) ENGINE = MergeTree()
            ORDER BY (campaign_id, sent_at)
        """)
        
        logger.info("Created analytics tables")
    
    async def log_agent_interaction(
        self,
        agent_type: str,
        task: str,
        result: str,
        duration_ms: int,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log agent interaction"""
        if not self.client:
            self.connect()
        
        import uuid
        interaction_id = str(uuid.uuid4())
        
        self.client.insert(
            'agent_interactions',
            [[
                interaction_id,
                agent_type,
                task,
                result,
                duration_ms,
                success,
                datetime.utcnow(),
                str(metadata or {})
            ]]
        )
        
        logger.info(f"Logged interaction for {agent_type}")
    
    async def log_voice_call(
        self,
        call_id: str,
        room_name: str,
        participant_id: str,
        duration_seconds: int,
        transcript: str,
        sentiment_score: float,
        outcome: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log voice call"""
        if not self.client:
            self.connect()
        
        self.client.insert(
            'voice_calls',
            [[
                call_id,
                room_name,
                participant_id,
                duration_seconds,
                transcript,
                sentiment_score,
                outcome,
                datetime.utcnow(),
                str(metadata or {})
            ]]
        )
        
        logger.info(f"Logged voice call: {call_id}")
    
    async def get_agent_performance(self, agent_type: str, days: int = 7) -> Dict[str, Any]:
        """Get agent performance metrics"""
        if not self.client:
            self.connect()
        
        query = f"""
            SELECT
                count() as total_interactions,
                countIf(success) as successful_interactions,
                avg(duration_ms) as avg_duration_ms,
                countIf(success) / count() as success_rate
            FROM agent_interactions
            WHERE agent_type = '{agent_type}'
            AND timestamp >= now() - INTERVAL {days} DAY
        """
        
        result = self.client.query(query)
        
        return {
            "agent_type": agent_type,
            "total_interactions": result.result_rows[0][0],
            "successful_interactions": result.result_rows[0][1],
            "avg_duration_ms": result.result_rows[0][2],
            "success_rate": result.result_rows[0][3]
        }
    
    async def get_voice_call_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get voice call analytics"""
        if not self.client:
            self.connect()
        
        query = f"""
            SELECT
                count() as total_calls,
                avg(duration_seconds) as avg_duration,
                avg(sentiment_score) as avg_sentiment,
                countIf(outcome = 'successful') / count() as success_rate
            FROM voice_calls
            WHERE timestamp >= now() - INTERVAL {days} DAY
        """
        
        result = self.client.query(query)
        
        return {
            "total_calls": result.result_rows[0][0],
            "avg_duration_seconds": result.result_rows[0][1],
            "avg_sentiment": result.result_rows[0][2],
            "success_rate": result.result_rows[0][3]
        }
