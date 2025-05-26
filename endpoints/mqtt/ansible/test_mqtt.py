#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import json
import sys

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
    else:
        print(f"❌ Failed to connect to MQTT broker with code {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    print(f"📬 Received message on topic {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode())
        print(f"   Message: {payload}")
    except json.JSONDecodeError:
        print(f"   Message: {msg.payload.decode()}")

def test_mqtt():
    print("Testing MQTT broker...")
    
    # Create client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to broker
        print("🔌 Connecting to MQTT broker...")
        client.connect("localhost", 1883, 60)
        
        # Start network loop
        client.loop_start()
        
        # Subscribe to test topic
        test_topic = "test/topic"
        client.subscribe(test_topic)
        print(f"📡 Subscribed to topic: {test_topic}")
        
        # Publish test message
        test_message = {"message": "Hello, MQTT!", "status": "test"}
        client.publish(test_topic, json.dumps(test_message))
        print(f"📤 Published test message to {test_topic}")
        
        # Wait for message to be received
        time.sleep(2)
        
        # Disconnect
        client.loop_stop()
        client.disconnect()
        
        print("✅ MQTT test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ MQTT test failed: {str(e)}")
        return False
    finally:
        try:
            client.disconnect()
        except:
            pass

if __name__ == "__main__":
    success = test_mqtt()
    sys.exit(0 if success else 1)
