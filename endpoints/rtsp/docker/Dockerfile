FROM aler9/rtsp-simple-server:latest

# Install FFmpeg for test stream generation
USER root
RUN apk add --no-cache ffmpeg

# Create a test video
RUN ffmpeg -f lavfi -i testsrc=size=640x480:rate=30 -t 10 -c:v libx264 -pix_fmt yuv420p /test_stream.mp4

# Copy custom RTSP server config
COPY rtsp-simple-server.yml /rtsp-simple-server.yml

# Start script that will run both RTSP server and FFmpeg stream
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8554 1935 8888

ENTRYPOINT ["/start.sh"]
