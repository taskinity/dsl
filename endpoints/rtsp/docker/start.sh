#!/bin/sh

# Start RTSP server in the background
/rtsp-simple-server /rtsp-simple-server.yml &

# Wait for RTSP server to start
sleep 2

# Start streaming the test video in a loop
echo "Starting RTSP test stream on rtsp://localhost:8554/stream"
ffmpeg -re -stream_loop -1 -i /test_stream.mp4 -c:v copy -f rtsp -rtsp_transport tcp rtsp://localhost:8554/stream &

# Keep container running
wait
