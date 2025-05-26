"""
Unit tests for the core engine functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Test the CamelRouterEngine class
class TestCamelRouterEngine:
    """Test cases for the CamelRouterEngine class."""

    @pytest.fixture
    def sample_config(self):
        """Return a sample configuration for testing."""
        return {
            'routes': [
                {
                    'name': 'test_route',
                    'from': 'timer://5s',
                    'processors': [
                        {
                            'type': 'transform',
                            'template': 'Hello {{message}}'
                        }
                    ],
                    'to': 'log://test.log'
                }
            ]
        }

    @pytest.fixture
    def engine(self, sample_config):
        """Create a CamelRouterEngine instance with sample config."""
        from camel_router.engine import CamelRouterEngine
        return CamelRouterEngine(sample_config, verbose=True)

    def test_initialization(self, engine, sample_config):
        """Test that the engine initializes with the correct config."""
        assert engine.config == sample_config
        assert len(engine.routes) == 1
        assert engine.verbose is True

    def test_run_all_routes(self, engine):
        """Test running all routes."""
        with patch('asyncio.gather') as mock_gather:
            asyncio.run(engine.run_all_routes())
            mock_gather.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_route(self, engine):
        """Test running a specific route by name."""
        with patch('camel_router.engine.CamelRouterEngine.run_route_config') as mock_run:
            await engine.run_route('test_route')
            mock_run.assert_called_once()

    def test_route_not_found(self, engine):
        """Test that a non-existent route raises an error."""
        with pytest.raises(ValueError, match="Route 'nonexistent' not found"):
            asyncio.run(engine.run_route('nonexistent'))

    @pytest.mark.parametrize("uri,expected", [
        ("timer://5s", ("timer", {"host": "5s"})),
        ("http://example.com/path?param=value", ("http", {"host": "example.com", "path": "/path", "param": ["value"]})),
    ])
    def test_parse_uri(self, engine, uri, expected):
        """Test URI parsing functionality."""
        result = engine.parse_uri(uri)
        assert result[0] == expected[0]  # scheme
        assert result[1] == expected[1]  # params

    def test_resolve_variables(self, engine):
        """Test environment variable resolution."""
        test_vars = {"TEST_VAR": "test_value"}
        with patch.dict('os.environ', test_vars):
            result = engine.resolve_variables('{{TEST_VAR}}')
            assert result == 'test_value'

    @pytest.mark.asyncio
    async def test_route_execution_flow(self, engine, sample_config):
        """Test the complete route execution flow with mocks."""
        # Mock the processor
        mock_processor = AsyncMock()
        mock_processor.process.return_value = {"message": "processed"}
        
        # Mock the processor factory
        with patch('camel_router.engine.get_processor', return_value=mock_processor) as mock_factory:
            # Mock the connector
            mock_connector = AsyncMock()
            mock_connector.receive.return_value = [{"test": "data"}]
            mock_connector.send.return_value = True
            
            with patch('camel_router.engine.get_connector', return_value=mock_connector) as mock_conn_factory:
                # Run the route
                await engine.run_route_config(sample_config['routes'][0])
                
                # Verify the processor was created and called
                mock_factory.assert_called_once()
                mock_processor.process.assert_called_once()
                
                # Verify the connector was used for sending
                mock_connector.send.assert_called_once()
