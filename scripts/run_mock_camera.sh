#!/bin/bash

# Make the test script executable
chmod +x test_rtsp_stream.py

# Install required Python packages if needed
pip install opencv-python-headless

# Start the RTSP server in the background
echo "🚀 Starting RTSP server with test video..."
docker-compose -f docker-compose.test.yml up -d

# Wait for the service to start
echo "⏳ Waiting for RTSP server to be ready..."
sleep 10

# Test the RTSP stream
echo "🔍 Testing RTSP stream..."
python test_rtsp_stream.py rtsp://localhost:8554/mystream

if [ $? -eq 0 ]; then
    echo -e "\n✅ Mock camera is running successfully!"
    echo "RTSP Stream URL: rtsp://localhost:8554/mystream"
    echo -e "\nYou can now use this RTSP URL in your application."
    echo -e "To stop the mock camera, run: docker-compose -f docker-compose.test.yml down\n"
else
    echo -e "\n❌ Failed to start mock camera. Check the logs with:"
    echo "docker-compose -f docker-compose.test.yml logs"
    exit 1
fi
