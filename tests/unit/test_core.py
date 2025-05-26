"""Unit tests for core functionality."""
import pytest
from pathlib import Path

# Test basic imports
def test_imports():
    """Test that core modules can be imported."""
    # This will raise ImportError if imports fail
    from taskinity.core import Configuration_Schema, Core_Classes, Processors
    assert True  # If we get here, imports worked

# Test configuration loading
def test_config_loading(sample_config):
    """Test configuration loading and validation."""
    from taskinity.core import Configuration_Schema
    
    # Test valid config
    config = Configuration_Schema(**sample_config)
    assert config.version == "1.0"
    assert len(config.routes) == 1
    assert config.routes[0].id == "test_route"

# Test route processing
class TestRouteProcessing:
    """Test route processing functionality."""
    
    def test_route_creation(self, sample_config):
        """Test creating a route from config."""
        from taskinity.core import Core_Classes
        
        route_config = sample_config["routes"][0]
        route = Core_Classes.Route(**route_config)
        
        assert route.id == "test_route"
        assert route.from_ == "test_source"
        assert route.to == ["test_destination"]
        assert route.processors == ["test_processor"]
