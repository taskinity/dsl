"""
Unit tests for CamelRouterEngine.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json

# Add this at the top of the file to avoid import errors
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from pathlib import Path

# Test the CamelRouterEngine class
class TestCamelRouterEngine:
    """Test cases for the CamelRouterEngine class."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "version": "1.0",
            "routes": [
                {
                    "name": "test_route",
                    "from": "timer:5s",
                    "to": ["log:test"],
                    "processors": ["transform_processor"]
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

    @pytest.fixture
    def event_loop(self):
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_run_all_routes(self, engine):
        """Test running all routes."""
        # Mock the run_route_config method
        with patch.object(engine, 'run_route_config', new_callable=AsyncMock) as mock_run:
            # Mock the route processing to avoid actual async operations
            async def mock_route_processor(*args, **kwargs):
                return None
                
            mock_run.side_effect = mock_route_processor
            
            # Run the test
            await engine.run_all_routes()
            
            # Verify the method was called
            assert mock_run.call_count == 1

    def test_route_not_found(self, engine):
        """Test that a non-existent route raises an error."""
        with pytest.raises(ValueError, match="Route 'nonexistent' not found"):
            asyncio.run(engine.run_route('nonexistent'))

    @pytest.mark.parametrize("uri,expected", [
        ("timer:5s", ("timer", "5s")),
        ("http://example.com/path?param=value", ("http", "//example.com/path?param=value")),
    ])
    def test_parse_uri(self, engine, uri, expected):
        """Test URI parsing."""
        from camel_router.engine import parse_uri
        assert parse_uri(uri) == expected

    def test_resolve_variables(self, engine):
        """Test environment variable resolution."""
        test_vars = {"TEST_VAR": "test_value"}
        with patch.dict('os.environ', test_vars):
            result = engine.resolve_variables('{{TEST_VAR}}')
            assert result == 'test_value'

    @pytest.mark.asyncio
    async def test_route_execution_flow(self, engine, monkeypatch):
        """Test the complete route execution flow."""
        # Create a test route config
        route_config = {
            "name": "test_flow",
            "from": "timer:1s",
            "to": ["log:test"],
            "processors": ["transform"]
        }
        
        # Mock the components
        mock_source = AsyncMock()
        mock_source.receive.return_value = [{"test": "data"}]
        
        mock_processor = AsyncMock()
        mock_processor.process.return_value = {"processed": True}
        
        mock_destination = AsyncMock()
        
        # Patch the creation methods
        with patch('camel_router.engine.parse_uri') as mock_parse_uri, \
             patch('camel_router.engine.TimerSource', return_value=mock_source), \
             patch('camel_router.engine.TransformProcessor', return_value=mock_processor), \
             patch('camel_router.engine.LogDestination', return_value=mock_destination):
            
            # Mock the URI parsing
            mock_parse_uri.side_effect = [
                ("timer", "1s"),
                ("log", "test")
            ]
            
            # Run the route
            await engine.run_route_config(route_config)
            
            # Verify the flow
            mock_source.receive.assert_called_once()
            mock_processor.process.assert_called_once_with({"test": "data"})
            mock_destination.send.assert_called_once_with({"processed": True})
