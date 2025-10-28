from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from app.agents.adaptive_agent import SalesAgent, OutboundEmailAgent

router = APIRouter()

orchestrator = MultiAgentOrchestrator()
sales_agent = SalesAgent()
email_agent = OutboundEmailAgent()


class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    agent_type: Optional[str] = None


class EmailGenerationRequest(BaseModel):
    prospect_name: str
    prospect_company: str
    prospect_role: str
    context: Optional[str] = None


@router.post("/execute")
async def execute_agent_task(request: TaskRequest):
    """Execute agent task with multi-agent orchestration"""
    try:
        if request.agent_type == "sales":
            result = await sales_agent.execute(request.task, request.context)
        elif request.agent_type == "email":
            result = await email_agent.execute(request.task, request.context)
        else:
            result = await orchestrator.execute_workflow(request.task, request.context)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-email")
async def generate_outbound_email(request: EmailGenerationRequest):
    """Generate personalized outbound email"""
    try:
        prospect_info = {
            "name": request.prospect_name,
            "company": request.prospect_company,
            "role": request.prospect_role,
            "context": request.context
        }
        
        email = await email_agent.generate_email(prospect_info)
        
        return {
            "success": True,
            "email": email,
            "prospect": prospect_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status():
    """Get status of all agents"""
    return {
        "sales_agent": "active",
        "email_agent": "active",
        "orchestrator": "active"
    }
