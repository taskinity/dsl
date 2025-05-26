"""
Test configuration and fixtures
"""
import pytest
import asyncio
from unittest.mock import AsyncMock

# This makes event loop available in test functions
@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

# Common test fixtures
@pytest.fixture
def mock_config():
    """Sample configuration for testing"""
    return {
        'routes': [
            {
                'name': 'test_route',
                'from': 'timer://5s',
                'processors': [
                    {
                        'type': 'log',
                        'message': 'Processing message'
                    }
                ]
            }
        ]
    }
