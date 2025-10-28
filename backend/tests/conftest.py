"""Test configuration and fixtures"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_conversation():
    """Sample sales conversation for testing"""
    return """
    Rep: Hi, this is Sarah from TechCo.
    Prospect: Hello Sarah, what can I do for you?
    Rep: I wanted to discuss how we can help improve your sales process.
    Prospect: That sounds interesting. Tell me more.
    """


@pytest.fixture
def sample_prospect_data():
    """Sample prospect data for testing"""
    return {
        "name": "John Doe",
        "company": "Acme Corp",
        "role": "VP of Sales",
        "industry": "SaaS",
        "pain_points": ["lead generation", "conversion rate"]
    }
