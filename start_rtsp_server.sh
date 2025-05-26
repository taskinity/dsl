#!/bin/bash

echo "🚀 Pulling and running RTSP test server..."
docker run --rm -it --network=host -e RTSP_PROTOCOLS=tcp aler9/rtsp-simple-server
