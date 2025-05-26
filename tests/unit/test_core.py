"""
Unit tests for core functionality.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from camel_router.engine import CamelRouterEngine
from camel_router.processors import Processor, ExternalProcessor, FilterProcessor, TransformProcessor, AggregateProcessor, DebugProcessor
from camel_router.connectors import Source, Destination


def test_imports():
    """Test that core modules can be imported."""
    # These imports should not raise ImportError
    assert CamelRouterEngine is not None
    assert Processor is not None
    assert Source is not None
    assert Destination is not None


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "version": "1.0",
        "routes": [
            {
                "name": "test_route",  
                "from": "timer:1s",
                "to": ["log:test"],
                "processors": ["transform_processor"]
            }
        ]
    }


class TestCoreFunctionality:
    """Test cases for core functionality."""
    
    def test_config_loading(self, sample_config):
        """Test configuration loading and validation."""
        # Just test that we can create a CamelRouterEngine with the sample config
        engine = CamelRouterEngine(sample_config)
        assert engine is not None
        assert engine.config == sample_config
        assert len(engine.routes) == 1


class TestCamelRouterEngine:
    """Test cases for CamelRouterEngine."""
    
    @pytest.fixture
    def engine(self, sample_config):
        """Create a CamelRouterEngine instance for testing."""
        return CamelRouterEngine(sample_config)
    
    def test_initialization(self, engine, sample_config):
        """Test that the engine initializes with the correct config."""
        assert engine.config == sample_config
        assert len(engine.routes) == 1
    
    @pytest.mark.asyncio
    async def test_run_all_routes(self, engine):
        """Test running all routes."""
        # Mock the run_route_config method
        with patch.object(engine, 'run_route_config', new_callable=AsyncMock) as mock_run:
            await engine.run_all_routes()
            mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_route(self, engine):
        """Test running a specific route by name."""
        # Mock the run_route_config method to avoid actual processing
        with patch.object(engine, 'run_route_config', new_callable=AsyncMock) as mock_run:
            # Set up the mock to return None (success)
            mock_run.return_value = None
            
            # Call the method with the route name that exists in our test config
            await engine.run_route('test_route')
            
            # Verify the method was called with the correct route config
            assert mock_run.called
            assert mock_run.call_count == 1
            
            # Get the route config that was passed to run_route_config
            called_route_config = mock_run.call_args[0][0]
            assert called_route_config["name"] == "test_route"
            mock_run.assert_called_once()
    
    def test_route_not_found(self, engine):
        """Test that a non-existent route raises an error."""
        with pytest.raises(ValueError, match="Route 'nonexistent' not found"):
            asyncio.run(engine.run_route('nonexistent'))
