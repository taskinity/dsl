"""
Unit tests for processor classes.
"""
import pytest
import asyncio
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock, ANY
import json
from datetime import datetime

# Add this at the top of the file to avoid import errors
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

# Test the base Processor class
def test_processor_abstract_class():
    """Test that Processor is an abstract base class."""
    from camel_router.processors import Processor
    
    # Test that we can't instantiate the abstract class
    with pytest.raises(TypeError):
        Processor()
    
    # Test that the abstract method is required
    class TestProcessor(Processor):
        async def process(self, message):
            return message
    
    # Should be able to instantiate a concrete implementation
    processor = TestProcessor()
    assert processor is not None

# Test ExternalProcessor
class TestExternalProcessor:
    """Test cases for ExternalProcessor."""
    
    @pytest.fixture
    def processor_config(self):
        return {
            'command': 'python3 -m my_processor',
            'input_format': 'json',
            'output_format': 'json',
            'async': False,
            'timeout': 10,
            'config': {}  # Add default empty config
        }
    
    @pytest.fixture
    def processor(self, processor_config):
        from camel_router.processors import ExternalProcessor
        return ExternalProcessor(processor_config)
    
    @pytest.mark.asyncio
    async def test_process_success(self, processor, tmp_path):
        """Test successful external command execution."""
        test_input = {"test": "data"}
        expected_output = {"result": "processed"}
        
        with patch('subprocess.run') as mock_run, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            # Mock the temporary file
            mock_file = MagicMock()
            mock_file.name = "/tmp/tempfile123"
            mock_temp_file.return_value.__enter__.return_value = mock_file
            
            # Mock subprocess run result
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps(expected_output).encode()
            mock_run.return_value = mock_result
            
            # Call the method
            result = await processor.process(test_input)
            
            # Assert the result
            assert result == expected_output
            mock_run.assert_called_once()
            # Check that write was called with the correct data
            mock_file.write.assert_called_once()
            # Get the actual call arguments
            args, _ = mock_file.write.call_args
            # The first argument should be the JSON-encoded input
            assert json.loads(args[0].decode()) == test_input
    
    @pytest.mark.asyncio
    async def test_process_error(self, processor):
        """Test error handling in external command execution."""
        with patch('subprocess.run') as mock_run, \
             patch('tempfile.NamedTemporaryFile'):
            mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
            
            result = await processor.process({"test": "data"})
            assert result is None

# Test FilterProcessor
class TestFilterProcessor:
    """Test cases for FilterProcessor."""
    
    @pytest.fixture
    def processor(self):
        from camel_router.processors import FilterProcessor
        return FilterProcessor({
            'condition': 'value > 10 and name == "test"',
            'config': {}  # Add default empty config
        })
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,should_pass", [
        ({"value": 15, "name": "test"}, True),
        ({"value": 5, "name": "test"}, False),
        ({"value": 15, "name": "other"}, False),
    ])
    async def test_filter_conditions(self, processor, message, should_pass):
        """Test various filter conditions."""
        result = await processor.process(message)
        if should_pass:
            assert result == message  # Message passes filter
        else:
            assert result is None  # Message is filtered out

# Test TransformProcessor
class TestTransformProcessor:
    """Test cases for TransformProcessor."""
    
    @pytest.fixture
    def processor(self):
        from camel_router.processors import TransformProcessor
        return TransformProcessor({
            'template': 'Processed: {{name}} with value {{value}}',
            'output_field': 'transformed',
            'config': {}  # Add default empty config
        })
    
    @pytest.mark.asyncio
    async def test_transform(self, processor):
        """Test message transformation."""
        message = {"name": "test", "value": 42}
        expected = {
            "name": "test", 
            "value": 42,
            "transformed": "Processed: test with value 42"
        }
        
        result = await processor.process(message)
        assert result == expected

# Test AggregateProcessor
class TestAggregateProcessor:
    """Test cases for AggregateProcessor."""
    
    @pytest.fixture
    def processor(self, event_loop):
        from camel_router.processors import AggregateProcessor
        return AggregateProcessor({
            'strategy': 'collect',
            'timeout': '1s',
            'max_size': 3,
            'config': {}  # Add default empty config
        })
        
    @pytest.fixture
    def event_loop(self):
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    @pytest.mark.asyncio
    async def test_aggregate_collect(self, processor):
        """Test message aggregation with collect strategy."""
        # First message - should be buffered
        result1 = await processor.process({"id": 1, "value": 10})
        assert result1 is None
    
        # Second message - still buffered
        result2 = await processor.process({"id": 2, "value": 20})
        assert result2 is None
    
        # Third message - triggers aggregation (max_size=3)
        with patch('time.time', return_value=1000.0):
            result3 = await processor.process({"id": 3, "value": 30})
            assert result3 is not None
            # Check the structure of the aggregated result
            assert isinstance(result3, dict)
            assert "events" in result3
            assert len(result3["events"]) == 3
            assert result3["count"] == 3
            assert result3["first_id"] == 1
            assert result3["last_id"] == 3
    
    @pytest.mark.asyncio
    async def test_aggregate_timeout(self, processor):
        """Test aggregation timeout."""
        # Add one message
        result1 = await processor.process({"id": 1, "value": 10})
        assert result1 is None  # Should be buffered
        
        # Fast forward time to trigger timeout
        with patch('time.time', return_value=1000.0):  # More than 1s timeout
            # This should trigger the timeout and return the buffered messages
            result2 = await processor.process({"id": 2, "value": 20})
            assert result2 is not None
            # Check the structure of the timed out result
            assert isinstance(result2, dict)
            assert "events" in result2
            assert len(result2["events"]) == 1  # Only the first message
            assert result2["count"] == 1
            assert result2["first_id"] == 1
            assert result2["last_id"] == 1

# Test DebugProcessor
class TestDebugProcessor:
    """Test cases for DebugProcessor."""
    
    @pytest.fixture
    def processor(self):
        from camel_router.processors import DebugProcessor
        return DebugProcessor({
            'prefix': 'TEST_DEBUG',
            'config': {}  # Add default empty config
        })
    
    @pytest.mark.asyncio
    async def test_debug_logging(self, processor, capsys):
        """Test debug message logging."""
        test_message = {"test": "data"}
        result = await processor.process(test_message)
        
        # Should return the message unchanged
        assert result == test_message
        
        # Check if debug message was printed
        captured = capsys.readouterr()
        assert "TEST_DEBUG" in captured.out
        assert "test" in captured.out
