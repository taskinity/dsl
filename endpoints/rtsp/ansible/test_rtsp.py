#!/usr/bin/env python3
import cv2
import sys

def test_rtsp_stream(rtsp_url="rtsp://localhost:8554/stream", max_attempts=3, timeout=5):
    print(f"Testing RTSP stream at: {rtsp_url}")
    
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}...")
        ret, frame = cap.read()
        
        if ret and frame is not None:
            print(f"✅ Success! Frame dimensions: {frame.shape}")
            cap.release()
            return True
        
        print(f"❌ Failed to read frame, retrying...")
    
    print("❌ Failed to connect to RTSP stream after multiple attempts")
    cap.release()
    return False

if __name__ == "__main__":
    rtsp_url = sys.argv[1] if len(sys.argv) > 1 else "rtsp://localhost:8554/stream"
    success = test_rtsp_stream(rtsp_url)
    sys.exit(0 if success else 1)
