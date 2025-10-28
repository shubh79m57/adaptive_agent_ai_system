from temporalio import workflow, activity
from datetime import timedelta
from typing import Dict, Any
from loguru import logger


@activity.defn
async def send_email_activity(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to send email"""
    logger.info(f"Sending email to {email_data.get('recipient')}")
    # Email sending logic here
    return {"status": "sent", "email_id": "email_123"}


@activity.defn
async def make_sales_call_activity(call_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to initiate sales call"""
    logger.info(f"Initiating call to {call_data.get('contact')}")
    # Call initiation logic here
    return {"status": "completed", "call_id": "call_123"}


@activity.defn
async def analyze_interaction_activity(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to analyze interaction and learn"""
    logger.info("Analyzing interaction for learning")
    # Analysis logic here
    return {"insights": "Customer interested in product", "next_action": "follow_up"}


@workflow.defn
class OutboundCampaignWorkflow:
    """Workflow for automated outbound campaigns"""
    
    @workflow.run
    async def run(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute outbound campaign workflow"""
        
        # Send initial email
        email_result = await workflow.execute_activity(
            send_email_activity,
            campaign_data.get("email_data"),
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Wait for response or timeout
        await workflow.sleep(timedelta(hours=24))
        
        # If no response, schedule follow-up
        followup_result = await workflow.execute_activity(
            send_email_activity,
            campaign_data.get("followup_data"),
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Analyze campaign performance
        analysis = await workflow.execute_activity(
            analyze_interaction_activity,
            {"email_result": email_result, "followup_result": followup_result},
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        return {
            "campaign_id": campaign_data.get("campaign_id"),
            "email_result": email_result,
            "followup_result": followup_result,
            "analysis": analysis
        }


@workflow.defn
class SalesCallWorkflow:
    """Workflow for sales call orchestration"""
    
    @workflow.run
    async def run(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sales call workflow"""
        
        # Initiate call
        call_result = await workflow.execute_activity(
            make_sales_call_activity,
            call_data,
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        # Analyze call
        analysis = await workflow.execute_activity(
            analyze_interaction_activity,
            {"call_result": call_result},
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # Schedule follow-up based on analysis
        if analysis.get("next_action") == "follow_up":
            await workflow.sleep(timedelta(days=2))
            
            followup = await workflow.execute_activity(
                send_email_activity,
                {"recipient": call_data.get("contact"), "type": "follow_up"},
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            return {
                "call_result": call_result,
                "analysis": analysis,
                "followup": followup
            }
        
        return {
            "call_result": call_result,
            "analysis": analysis
        }


@workflow.defn
class ContinuousLearningWorkflow:
    """Workflow for continuous agent learning"""
    
    @workflow.run
    async def run(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute continuous learning workflow"""
        
        results = []
        
        # Analyze interactions periodically
        for _ in range(learning_data.get("iterations", 10)):
            analysis = await workflow.execute_activity(
                analyze_interaction_activity,
                learning_data,
                start_to_close_timeout=timedelta(minutes=10)
            )
            
            results.append(analysis)
            
            # Wait before next iteration
            await workflow.sleep(timedelta(hours=6))
        
        return {
            "learning_results": results,
            "total_iterations": len(results)
        }
