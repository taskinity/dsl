"""
Tests for dialog chain processors
"""
import pytest
from unittest.mock import Mock, patch
from dialogchain.processors import Processor, LogProcessor, TransformProcessor, FilterProcessor
from dialogchain.exceptions import ProcessorError

class TestProcessors:
    
    def test_base_processor_abstract(self):
        """Test that the base Processor class is abstract"""
        with pytest.raises(TypeError):
            Processor()
    
    @pytest.mark.asyncio
    async def test_log_processor(self):
        """Test the log processor"""
        processor = LogProcessor({'message': 'Test message'})
        result = await processor.process('test message')
        assert result == 'test message'  # Should return the message unchanged
    
    @pytest.mark.asyncio
    async def test_transform_processor(self):
        """Test the transform processor"""
        config = {
            'expression': 'message.upper()',
            'context': {'message': 'test'}
        }
        processor = TransformProcessor(config)
        result = await processor.process('test')
        assert result == 'TEST'
