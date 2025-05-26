#!/usr/bin/env python3
import cv2
import time
import sys

def test_rtsp_stream(rtsp_url, max_attempts=5, delay=2):
    """Test RTSP stream connection and display first frame."""
    print(f"Testing RTSP stream at: {rtsp_url}")
    
    cap = cv2.VideoCapture(rtsp_url)
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}...")
        ret, frame = cap.read()
        
        if ret:
            print("✅ Successfully connected to RTSP stream!")
            print(f"Frame dimensions: {frame.shape}")
            
            # Save a test frame
            cv2.imwrite('test_frame.jpg', frame)
            print("Saved test frame to 'test_frame.jpg'")
            
            # Display frame (if possible)
            try:
                cv2.imshow('Test Frame', frame)
                cv2.waitKey(2000)  # Display for 2 seconds
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"Could not display frame: {e}")
            
            cap.release()
            return True
        
        print(f"❌ Failed to read frame, retrying in {delay} seconds...")
        time.sleep(delay)
    
    print("❌ Failed to connect to RTSP stream after multiple attempts")
    cap.release()
    return False

if __name__ == "__main__":
    rtsp_url = sys.argv[1] if len(sys.argv) > 1 else "rtsp://localhost:8554/mystream"
    test_rtsp_stream(rtsp_url)
