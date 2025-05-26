#!/usr/bin/env python3
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_webrtc():
    print("Starting WebRTC test...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Enable WebRTC logging
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    
    # Allow camera and microphone in headless mode
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    driver = None
    
    try:
        # Initialize the Chrome driver
        print("Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Open the test page
        test_url = "http://localhost:3000"
        print(f"Opening {test_url}...")
        driver.get(test_url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "startButton"))
        )
        print("Test page loaded successfully")
        
        # Test basic functionality
        start_button = driver.find_element(By.ID, "startButton")
        call_button = driver.find_element(By.ID, "callButton")
        hangup_button = driver.find_element(By.ID, "hangupButton")
        
        # Click start button
        print("Starting camera...")
        start_button.click()
        time.sleep(2)  # Wait for camera to initialize
        
        # Verify call button is enabled
        if call_button.is_enabled():
            print("✅ Camera started successfully")
        else:
            print("❌ Failed to start camera")
            return False
        
        # Click call button
        print("Starting WebRTC call...")
        call_button.click()
        time.sleep(3)  # Wait for connection
        
        # Check if hangup button is enabled (indicates call is active)
        if hangup_button.is_enabled():
            print("✅ WebRTC call established successfully")
        else:
            print("❌ Failed to establish WebRTC call")
            return False
        
        # Hang up
        print("Ending call...")
        hangup_button.click()
        time.sleep(1)
        
        print("✅ WebRTC test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ WebRTC test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

if __name__ == "__main__":
    success = test_webrtc()
    sys.exit(0 if success else 1)
