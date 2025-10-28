"""Tests for adaptive agents"""
import pytest
from app.agents.adaptive_agent import AdaptiveAgent, SalesAgent, OutboundEmailAgent


@pytest.mark.asyncio
async def test_adaptive_agent_initialization():
    """Test basic agent initialization"""
    agent = AdaptiveAgent(agent_type="test")
    assert agent.agent_type == "test"
    assert agent.llm is not None
    assert len(agent.tools) > 0


@pytest.mark.asyncio
async def test_sales_agent():
    """Test sales agent"""
    agent = SalesAgent()
    assert agent.agent_type == "sales"
    assert agent.model_provider == "openai"


@pytest.mark.asyncio
async def test_email_agent():
    """Test email agent"""
    agent = OutboundEmailAgent()
    assert agent.agent_type == "outbound_email"
    assert agent.model_provider == "anthropic"


# Add more tests as needed
