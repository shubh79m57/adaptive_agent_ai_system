"""Example: Using the Sales Agent"""
import asyncio
from app.agents.adaptive_agent import SalesAgent
from app.core.config import settings


async def main():
    # Initialize sales agent
    agent = SalesAgent()
    
    # Example 1: Analyze a sales conversation
    print("=== Example 1: Analyze Sales Conversation ===")
    conversation = """
    Rep: Hi John, this is Sarah from TechCo. How are you today?
    Prospect: I'm good, thanks. What's this about?
    Rep: We help companies like yours improve their sales processes with AI.
    Prospect: That sounds interesting. Tell me more.
    Rep: We've helped companies increase conversion rates by 40% on average.
    Prospect: Impressive. What's involved in getting started?
    """
    
    result = await agent.execute(
        f"Analyze this sales conversation and provide insights: {conversation}"
    )
    print("Analysis:", result.get('output', ''))
    
    # Example 2: Get customer profile
    print("\n=== Example 2: Suggest Next Action ===")
    context = {
        "customer_name": "Acme Corp",
        "industry": "SaaS",
        "previous_interactions": 3,
        "interest_level": "high"
    }
    
    result = await agent.execute(
        "What should be my next action with this customer?",
        context=context
    )
    print("Suggested Action:", result.get('output', ''))


if __name__ == "__main__":
    asyncio.run(main())
