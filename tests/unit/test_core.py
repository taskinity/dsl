"""
Unit tests for core functionality.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from camel_router.engine import CamelRouterEngine
from camel_router.processors import Processor, ExternalProcessor, FilterProcessor, TransformProcessor, AggregateProcessor, DebugProcessor
from camel_router.connectors import Source, Destination
from taskinity.core import Core_Classes
from camel_router.schema import Configuration_Schema


def test_imports():
    """Test that core modules can be imported."""
    # These imports should not raise ImportError
    assert CamelRouterEngine is not None
    assert Processor is not None
    assert Source is not None
    assert Destination is not None


@pytest.fixture
def sample_config():
    """Return a sample configuration for testing."""
    return {
        'version': '1.0',
        'routes': [
            {
                'id': 'test_route',
                'from': 'test_source',
                'to': ['test_destination'],
                'processors': ['test_processor']
            }
        ]
    }


class TestCoreFunctionality:
    """Test cases for core functionality."""
    
    def test_config_loading(self, sample_config):
        """Test configuration loading and validation."""
        
        # Test valid config
        config = Configuration_Schema(**sample_config)
        assert config.version == "1.0"
        assert len(config.routes) == 1
        assert config.routes[0].id == "test_route"

    def test_route_creation(self, sample_config):
        """Test creating a route from config."""
        route_config = sample_config["routes"][0]
        route = Core_Classes.Route(**route_config)
        
        assert route.id == "test_route"
        assert route.from_ == "test_source"
        assert route.to == ["test_destination"]
        assert route.processors == ["test_processor"]


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
        with patch.object(engine, 'run_route_config', new_callable=AsyncMock) as mock_run:
            await engine.run_route('test_route')
            mock_run.assert_called_once()
    
    def test_route_not_found(self, engine):
        """Test that a non-existent route raises an error."""
        with pytest.raises(ValueError, match="Route 'nonexistent' not found"):
            asyncio.run(engine.run_route('nonexistent'))
