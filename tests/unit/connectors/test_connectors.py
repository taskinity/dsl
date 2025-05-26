"""
Unit tests for connector classes.
"""
import pytest
import asyncio
import json
import os
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from pathlib import Path

# Add this at the top of the file to avoid import errors
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

# Test Sources
class TestRTSPSource:
    """Test cases for RTSPSource."""
    
    @pytest.fixture
    def rtsp_source(self):
        from camel_router.connectors import RTSPSource
        return RTSPSource("rtsp://test:554/stream")
    
    @pytest.fixture
    def mock_cv2(self):
        with patch('cv2.VideoCapture') as mock_video_capture:
            mock_cap = MagicMock()
            mock_video_capture.return_value = mock_cap
            yield mock_cap
    
    @pytest.mark.asyncio
    async def test_receive_frames(self, rtsp_source, mock_cv2):
        """Test receiving frames from RTSP source."""
        # Configure the mock
        mock_cv2.isOpened.return_value = True
        mock_cv2.read.side_effect = [
            (True, "frame1"),
            (True, "frame2"),
            (False, None)  # Simulate end of stream
        ]
        
        # Mock time.sleep to avoid actual sleeping in tests
        with patch('time.sleep'), patch('asyncio.sleep'):
            # Test the async generator
            frames = []
            try:
                async for frame in rtsp_source.receive():
                    frames.append(frame)
                    if len(frames) >= 2:  # Prevent infinite loop in test
                        break
            except Exception as e:
                pytest.fail(f"Unexpected exception: {e}")
            
            # Verify the results
            assert len(frames) == 2
            assert frames[0]["frame"] == "frame1"
            assert frames[1]["frame"] == "frame2"

class TestTimerSource:
    """Test cases for TimerSource."""
    
    @pytest.fixture
    def timer_source(self):
        from camel_router.connectors import TimerSource
        return TimerSource("1s")
    
    @pytest.mark.asyncio
    async def test_timer_events(self, timer_source):
        """Test timer events generation."""
        events = []
        
        # Mock asyncio.sleep to return immediately after first iteration
        with patch('asyncio.sleep', side_effect=[None, asyncio.CancelledError()]):
            try:
                async for event in timer_source.receive():
                    events.append(event)
                    if len(events) >= 1:
                        raise asyncio.CancelledError()
            except asyncio.CancelledError:
                pass
        
        assert len(events) == 1
        assert "timestamp" in events[0]

# Test Destinations
class TestHTTPDestination:
    """Test cases for HTTPDestination."""
    
    @pytest.fixture
    def http_destination(self):
        from camel_router.connectors import HTTPDestination
        return HTTPDestination("http://example.com/api")
    
    @pytest.mark.asyncio
    async def test_send_http_request(self, http_destination):
        """Test sending HTTP request."""
        mock_response = MagicMock()
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            test_data = {"key": "value"}
            await http_destination.send(test_data)
            
            # Verify the POST request was made with correct data
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert kwargs['json'] == test_data

class TestFileDestination:
    """Test cases for FileDestination."""
    
    @pytest.fixture
    def file_destination(self, tmp_path):
        from camel_router.connectors import FileDestination
        test_file = tmp_path / "test_output.txt"
        return FileDestination(f"file://{test_file}")
    
    @pytest.mark.asyncio
    async def test_write_to_file(self, file_destination, tmp_path):
        """Test writing to a file."""
        test_data = {"test": "data"}
        await file_destination.send(test_data)
        
        # Verify file was created and contains the data
        path = tmp_path / "test_output.txt"
        assert path.exists()
        with open(path) as f:
            content = f.read()
            assert json.dumps(test_data) in content

class TestLogDestination:
    """Test cases for LogDestination."""
    
    @pytest.fixture
    def log_destination(self, tmp_path):
        from camel_router.connectors import LogDestination
        log_file = tmp_path / "test.log"
        return LogDestination(f"log://{log_file}")
    
    @pytest.mark.asyncio
    async def test_log_to_file(self, log_destination, tmp_path, capsys):
        """Test logging to a file."""
        test_data = {"message": "test log"}
        await log_destination.send(test_data)
        
        # Check console output
        captured = capsys.readouterr()
        assert "test log" in captured.out

# Test Connector Factory
def test_get_connector():
    """Test the connector factory function."""
    # Import inside the test to avoid import errors
    from camel_router.connectors import get_connector, RTSPSource, HTTPDestination, FileDestination, LogDestination
    
    # Test source connectors
    rtsp_source = get_connector("rtsp://test")
    assert isinstance(rtsp_source, RTSPSource)
    
    # Test destination connectors
    http_dest = get_connector("http://example.com")
    assert isinstance(http_dest, HTTPDestination)
    
    file_dest = get_connector("file:///tmp/test.txt")
    assert file_dest.__class__.__name__ == "FileDestination"
    
    # Test invalid connector
    with pytest.raises(ValueError, match="Unsupported connector type"):
        get_connector("invalid://test")
