#!/bin/bash

# Create a test pattern RTSP stream
echo "🚀 Starting RTSP test pattern stream on rtsp://localhost:8554/stream"
ffmpeg -re -f lavfi -i testsrc=size=640x480:rate=30 -vcodec libx264 -preset ultrafast -tune zerolatency -f rtsp -rtsp_transport tcp rtsp://localhost:8554/stream

# Install required packages
echo "📦 Installing required packages..."
sudo apt-get update
sudo apt-get install -y ffmpeg vlc

# Create a test video if it doesn't exist
if [ ! -f "test_video.mp4" ]; then
    echo "🎬 Creating test video..."
    ffmpeg -f lavfi -i testsrc=duration=60:size=640x480:rate=30 -c:v libx264 -pix_fmt yuv420p test_video.mp4
fi

# Start RTSP server using FFmpeg
echo "🚀 Starting RTSP server on rtsp://localhost:8554/stream"
echo "📺 Open rtsp://localhost:8554/stream in VLC or another RTSP client"

echo "🔴 Streaming test_video.mp4 in a loop..."
ffmpeg -re -stream_loop -1 -i test_video.mp4 -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp -rtsp_transport tcp rtsp://localhost:8554/stream
