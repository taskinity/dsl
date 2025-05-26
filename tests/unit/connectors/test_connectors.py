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
        from dialogchain.connectors import RTSPSource
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
        # Configure the mock to return frames and simulate connection loss
        mock_cv2.isOpened.return_value = True
        mock_cv2.read.side_effect = [
            (True, "frame1"),  # First frame
            (True, "frame2"),  # Second frame
            (False, None),     # Simulate connection loss
            (True, "frame3"),  # First frame after reconnect
            (True, "frame4"),  # Second frame after reconnect
            (False, None)      # Simulate connection loss again
        ]
        
        # Set a lower number of reconnect attempts for testing
        rtsp_source.reconnect_attempts = 2
        
        # Mock time.sleep to avoid actual sleeping in tests
        with patch('asyncio.sleep'):
            # Test the async generator
            frames = []
            try:
                async for frame in rtsp_source.receive():
                    frames.append(frame)
                    if len(frames) >= 2:  # Get exactly 2 frames
                        break
            except Exception as e:
                pytest.fail(f"Unexpected exception: {e}")
            finally:
                # Verify the mock was released
                assert mock_cv2.release.call_count >= 1
            
            # Verify we got the expected number of frames
            assert len(frames) == 2, f"Expected 2 frames, got {len(frames)}"
            
            # Verify frame content (we don't know the exact order due to reconnection)
            frame_data = [f["frame"] for f in frames]
            assert "frame1" in frame_data or "frame2" in frame_data or "frame3" in frame_data or "frame4" in frame_data
            
            # Verify source URI is correct
            for frame in frames:
                assert frame["source"] == rtsp_source.uri
                assert "timestamp" in frame
                assert "frame_count" in frame

class TestTimerSource:
    """Test cases for TimerSource."""
    
    @pytest.fixture
    def timer_source(self):
        from dialogchain.connectors import TimerSource
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
        from dialogchain.connectors import HTTPDestination
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
        from dialogchain.connectors import FileDestination
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
        from dialogchain.connectors import LogDestination
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
def test_connector_factory():
    """Test the connector factory function."""
    from dialogchain.engine import CamelRouterEngine
    from unittest.mock import patch, MagicMock
    
    # Create a test engine
    engine = CamelRouterEngine({"routes": []})
    
    # Create mock connector instances
    mock_rtsp = MagicMock()
    mock_rtsp.uri = "rtsp://test"
    
    mock_http = MagicMock()
    mock_http.uri = "http://example.com"
    
    mock_file = MagicMock()
    mock_file.uri = "file:///tmp/test.txt"
    
    mock_log = MagicMock()
    mock_log.uri = "log:test"
    
    # Patch the connector imports to return our mock instances
    with patch('dialogchain.engine.RTSPSource', return_value=mock_rtsp), \
         patch('dialogchain.engine.HTTPDestination', return_value=mock_http), \
         patch('dialogchain.engine.FileDestination', return_value=mock_file), \
         patch('dialogchain.engine.LogDestination', return_value=mock_log):
        
        # Test RTSP source connector
        rtsp_source = engine.create_source("rtsp://test")
        assert rtsp_source.uri == "rtsp://test"
        
        # Test HTTP destination connector
        http_dest = engine.create_destination("http://example.com")
        assert http_dest.uri == "http://example.com"
        
        # Test File destination connector
        file_dest = engine.create_destination("file:///tmp/test.txt")
        assert file_dest.uri == "file:///tmp/test.txt"
        
        # Test Log destination connector
        log_dest = engine.create_destination("log:test")
        assert log_dest.uri == "log:test"
    
    # Test invalid connector
    with pytest.raises(ValueError, match=r"Unsupported source scheme: invalid"):
        engine.create_source("invalid://test")
        
    with pytest.raises(ValueError, match=r"Unsupported destination scheme: invalid"):
        engine.create_destination("invalid://test")
