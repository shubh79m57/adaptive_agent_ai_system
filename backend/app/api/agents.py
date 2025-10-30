from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.agents.local_ai_agents import LocalSalesAgent, LocalEmailAgent, LocalAutoAgent

# Import simple email sender
try:
    from app.agents.simple_email_sender import SimpleEmailSender
    EMAIL_SENDING_AVAILABLE = True
except ImportError:
    EMAIL_SENDING_AVAILABLE = False

# Import advanced email agent if available
try:
    from app.agents.advanced_email_agent import AdvancedEmailAgent
    ADVANCED_EMAIL_AVAILABLE = True
except ImportError:
    ADVANCED_EMAIL_AVAILABLE = False
    print("Advanced email agent not available - email sending disabled")

router = APIRouter()

# Initialize local AI agents (no API keys required!)
sales_agent = LocalSalesAgent()
email_agent = LocalEmailAgent()
auto_agent = LocalAutoAgent()


class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    agent_type: Optional[str] = None


class EmailGenerationRequest(BaseModel):
    prospect_name: str
    prospect_company: str
    prospect_role: str
    context: Optional[str] = None


class BulkEmailRequest(BaseModel):
    prospects: List[Dict[str, str]]  # List of prospect dictionaries
    email_config: Optional[Dict[str, str]] = None
    campaign_type: Optional[str] = "outreach"
    delay_seconds: Optional[int] = 30


class EmailSendRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    email_config: Dict[str, str]  # Contains email and password


class EmailCampaignSetup(BaseModel):
    csv_file_path: Optional[str] = None
    email_config: Dict[str, str]
    campaign_name: Optional[str] = "Default Campaign"
    send_delay: Optional[int] = 60  # seconds between emails


@router.post("/send-email")
async def send_actual_email(request: EmailSendRequest):
    """Actually send an email using SMTP"""
    try:
        if not EMAIL_SENDING_AVAILABLE:
            raise HTTPException(status_code=400, detail="Email sending not available")
        
        # Validate email config
        if not request.email_config.get("email") or not request.email_config.get("password"):
            raise HTTPException(status_code=400, detail="Email configuration incomplete")
        
        # Create email sender
        sender = SimpleEmailSender(request.email_config)
        
        # Send email
        result = sender.send_email(
            recipient=request.recipient,
            subject=request.subject,
            body=request.body
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Email sent successfully to {request.recipient}",
                "recipient": request.recipient,
                "delivery_status": "sent"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-email/test")
async def test_email_config(email_config: Dict[str, str]):
    """Test email configuration without sending to external recipients"""
    try:
        if not EMAIL_SENDING_AVAILABLE:
            return {"success": False, "message": "Email sending not available"}
        
        if not email_config.get("email") or not email_config.get("password"):
            return {"success": False, "message": "Email and password required"}
        
        # Send test email to the configured email address (self-test)
        sender = SimpleEmailSender(email_config)
        
        result = sender.send_email(
            recipient=email_config["email"],  # Send to self
            subject="AI Agent Email Test",
            body="""This is a test email from your AI Agent system.

If you received this email, your email configuration is working correctly!

You can now:
- Send emails automatically through the AI agent
- Run bulk email campaigns
- Handle responses automatically

Best regards,
Your AI Sales Agent"""
        )
        
        return {
            "success": result["success"],
            "message": result["message"] if result["success"] else result["error"],
            "test_recipient": email_config["email"]
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/execute")
async def execute_agent_task(request: TaskRequest):
    """Execute agent task with AI-powered agents"""
    try:
        if request.agent_type == "sales":
            result = await sales_agent.process_task(request.task, request.context)
        elif request.agent_type == "email":
            result = await email_agent.process_task(request.task, request.context)
        else:
            # Use auto agent for intelligent routing
            result = await auto_agent.route_and_process(request.task)
        
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
            "prospect_name": request.prospect_name,
            "prospect_company": request.prospect_company,
            "prospect_role": request.prospect_role,
            "context": request.context
        }
        
        result = await email_agent.generate_email(prospect_info)
        
        return {
            "success": True,
            "email": result.get("response", ""),
            "prospect": prospect_info,
            "agent_info": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status():
    """Get status of all agents"""
    return {
        "sales_agent": "active",
        "email_agent": "active",
        "orchestrator": "active",
        "advanced_email_available": ADVANCED_EMAIL_AVAILABLE,
        "simple_email_sending": EMAIL_SENDING_AVAILABLE,
        "features": {
            "email_generation": True,
            "email_sending": EMAIL_SENDING_AVAILABLE,
            "bulk_campaigns": EMAIL_SENDING_AVAILABLE,
            "response_monitoring": ADVANCED_EMAIL_AVAILABLE
        }
    }


@router.post("/bulk-email/preview")
async def preview_bulk_email_campaign(request: BulkEmailRequest):
    """Preview what a bulk email campaign would look like"""
    try:
        if not request.prospects:
            raise HTTPException(status_code=400, detail="No prospects provided")
        
        # Generate preview for first few prospects
        previews = []
        for i, prospect in enumerate(request.prospects[:3]):  # Preview first 3
            prospect_info = {
                "prospect_name": prospect.get("name", "Prospect"),
                "prospect_company": prospect.get("company", "Company"),
                "prospect_role": prospect.get("role", "Decision Maker"),
                "context": prospect.get("context", request.campaign_type)
            }
            
            email_result = await email_agent.generate_email(prospect_info)
            previews.append({
                "prospect": prospect,
                "subject": email_result.get("subject_line", ""),
                "body": email_result.get("email_body", ""),
                "preview_number": i + 1
            })
        
        campaign_summary = {
            "total_prospects": len(request.prospects),
            "previewed": len(previews),
            "estimated_send_time": f"{len(request.prospects) * request.delay_seconds / 60:.1f} minutes",
            "campaign_type": request.campaign_type
        }
        
        return {
            "success": True,
            "campaign_summary": campaign_summary,
            "email_previews": previews,
            "ready_to_send": ADVANCED_EMAIL_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-email/send")
async def send_bulk_email_campaign(request: EmailCampaignSetup):
    """Send bulk email campaign using advanced email agent"""
    try:
        if not ADVANCED_EMAIL_AVAILABLE:
            return {
                "success": False,
                "message": "Advanced email agent not available. Please check the advanced_email_agent.py file.",
                "setup_required": True
            }
        
        if not request.email_config:
            raise HTTPException(status_code=400, detail="Email configuration required")
        
        # Initialize advanced email agent
        advanced_agent = AdvancedEmailAgent(request.email_config)
        
        # Load prospects from CSV if path provided, otherwise use default
        csv_path = request.csv_file_path or "prospects.csv"
        prospects = advanced_agent.load_prospect_list(csv_path)
        
        if not prospects:
            raise HTTPException(status_code=400, detail=f"No prospects found in {csv_path}")
        
        # Start bulk email campaign
        campaign_result = advanced_agent.send_bulk_emails(prospects, request.send_delay)
        
        return {
            "success": True,
            "campaign_name": request.campaign_name,
            "prospects_processed": len(prospects),
            "message": "Email campaign started successfully",
            "next_steps": [
                "Monitor your email for responses",
                "Use /bulk-email/monitor to check for replies",
                "Use /bulk-email/stats to see campaign performance"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-email/monitor")
async def monitor_email_responses(email_config: Dict[str, str]):
    """Monitor email responses and handle them automatically"""
    try:
        if not ADVANCED_EMAIL_AVAILABLE:
            return {
                "success": False,
                "message": "Advanced email agent not available"
            }
        
        advanced_agent = AdvancedEmailAgent(email_config)
        
        # Monitor inbox for replies
        advanced_agent.monitor_inbox_for_replies()
        
        # Get campaign statistics
        stats = advanced_agent.get_campaign_stats()
        
        return {
            "success": True,
            "monitoring_complete": True,
            "campaign_stats": stats,
            "message": "Inbox monitored and responses processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk-email/setup-guide")
async def get_bulk_email_setup_guide():
    """Get setup guide for bulk email functionality"""
    return {
        "setup_guide": {
            "requirements": [
                "Email account with app password (Gmail recommended)",
                "CSV file with prospect data",
                "Configured email authentication (SPF, DKIM)"
            ],
            "csv_format": {
                "required_columns": ["email", "name", "company", "role"],
                "optional_columns": ["context"],
                "example_row": {
                    "email": "john@company.com",
                    "name": "John Smith", 
                    "company": "TechCorp",
                    "role": "CEO",
                    "context": "product demo"
                }
            },
            "email_config_format": {
                "email": "your-sales@company.com",
                "password": "your-app-password",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "imap_server": "imap.gmail.com"
            },
            "best_practices": [
                "Start with small batches (10-20 prospects)",
                "Use app passwords instead of regular passwords",
                "Respect rate limits (30-60 seconds between emails)",
                "Monitor sender reputation and deliverability",
                "Always include unsubscribe options",
                "Personalize emails for better response rates"
            ],
            "features": [
                "Automatic personalization based on role/company",
                "Response monitoring and categorization",
                "Automated follow-up email generation",
                "Campaign performance analytics",
                "Thread management for conversations",
                "Lead scoring based on engagement"
            ]
        },
        "advanced_features_available": ADVANCED_EMAIL_AVAILABLE,
        "sample_csv_location": "backend/prospects.csv"
    }
