"""Example: Multi-Agent Orchestration"""
import asyncio
from app.agents.multi_agent_orchestrator import MultiAgentOrchestrator


async def main():
    orchestrator = MultiAgentOrchestrator()
    
    # Example 1: Auto-routing based on task
    print("=== Example 1: Auto-Routing ===")
    result = await orchestrator.execute_workflow(
        "Generate an outbound email for a SaaS prospect and suggest follow-up call strategy"
    )
    print("Result:", result.get('output', ''))
    
    # Example 2: Complex multi-step workflow
    print("\n=== Example 2: Multi-Step Workflow ===")
    context = {
        "prospect": {
            "name": "Jane Smith",
            "company": "Tech Innovations Inc",
            "role": "CTO",
            "pain_points": ["scalability", "automation"]
        },
        "campaign_type": "product_launch"
    }
    
    result = await orchestrator.execute_workflow(
        "Create a complete outreach strategy including email, call script, and follow-up plan",
        context=context
    )
    print("Strategy:", result.get('output', ''))
    print("Agents Used:", [msg['agent'] for msg in result.get('agent_messages', [])])


if __name__ == "__main__":
    asyncio.run(main())
