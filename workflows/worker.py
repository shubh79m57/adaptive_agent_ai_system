import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflows.temporal_workflows import (
    OutboundCampaignWorkflow,
    SalesCallWorkflow,
    ContinuousLearningWorkflow,
    send_email_activity,
    make_sales_call_activity,
    analyze_interaction_activity
)
from app.core.config import settings


async def main():
    """Start Temporal worker"""
    client = await Client.connect(
        f"{settings.TEMPORAL_HOST}:{settings.TEMPORAL_PORT}",
        namespace=settings.TEMPORAL_NAMESPACE
    )
    
    worker = Worker(
        client,
        task_queue="adaptive-ai-agents",
        workflows=[
            OutboundCampaignWorkflow,
            SalesCallWorkflow,
            ContinuousLearningWorkflow
        ],
        activities=[
            send_email_activity,
            make_sales_call_activity,
            analyze_interaction_activity
        ]
    )
    
    print("Starting Temporal worker...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
