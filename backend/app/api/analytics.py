from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.analytics_service import AnalyticsService

router = APIRouter()

analytics = AnalyticsService()


class PerformanceQuery(BaseModel):
    agent_type: str
    days: int = 7


@router.on_event("startup")
async def startup():
    """Initialize analytics service"""
    analytics.connect()
    analytics.create_tables()


@router.get("/performance/{agent_type}")
async def get_agent_performance(agent_type: str, days: int = 7):
    """Get agent performance metrics"""
    try:
        metrics = await analytics.get_agent_performance(agent_type, days)
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice-calls")
async def get_voice_call_analytics(days: int = 7):
    """Get voice call analytics"""
    try:
        metrics = await analytics.get_voice_call_analytics(days)
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        sales_performance = await analytics.get_agent_performance("sales", 7)
        email_performance = await analytics.get_agent_performance("outbound_email", 7)
        voice_analytics = await analytics.get_voice_call_analytics(7)
        
        return {
            "success": True,
            "dashboard": {
                "sales_agent": sales_performance,
                "email_agent": email_performance,
                "voice_calls": voice_analytics
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
