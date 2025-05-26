#!/usr/bin/env python3
"""Test script for the gRPC service."""

import grpc
import sys
import time
import logging
from datetime import datetime

# Import the generated gRPC stubs
import example_pb2
import example_pb2_grpc

def test_unary_rpc(stub):
    """Test the unary RPC method."""
    print("Testing unary RPC...")
    try:
        response = stub.SayHello(example_pb2.HelloRequest(name="Test User"))
        print(f"✅ Unary RPC successful: {response.message}")
        return True
    except grpc.RpcError as e:
        print(f"❌ Unary RPC failed: {e.code()}: {e.details()}")
        return False

def test_server_streaming(stub):
    """Test the server streaming RPC method."""
    print("\nTesting server streaming RPC...")
    try:
        request = example_pb2.DataRequest(count=3, prefix="test")
        response_stream = stub.StreamData(request)
        
        received_count = 0
        for response in response_stream:
            received_count += 1
            print(f"  - Received: ID={response.id}, Value='{response.value}'")
        
        if received_count == 3:
            print("✅ Server streaming RPC successful")
            return True
        else:
            print(f"❌ Server streaming RPC failed: Expected 3 messages, got {received_count}")
            return False
            
    except grpc.RpcError as e:
        print(f"❌ Server streaming RPC failed: {e.code()}: {e.details()}")
        return False

def test_client_streaming(stub):
    """Test the client streaming RPC method."""
    print("\nTesting client streaming RPC...")
    
    def generate_messages():
        for i in range(3):
            yield example_pb2.ClientMessage(
                client_id=f"client-{i}",
                message=f"Message {i+1}",
                sequence=i+1
            )
    
    try:
        response = stub.ClientStream(generate_messages())
        print(f"✅ Client streaming RPC successful. Response: {response.response}")
        print(f"  - Received {response.received_sequence} messages")
        return True
        
    except grpc.RpcError as e:
        print(f"❌ Client streaming RPC failed: {e.code()}: {e.details()}")
        return False

def test_bidirectional_streaming(stub):
    """Test the bidirectional streaming RPC method."""
    print("\nTesting bidirectional streaming RPC...")
    
    def generate_messages():
        for i in range(3):
            yield example_pb2.ClientMessage(
                client_id=f"client-{i}",
                message=f"Bidi {i+1}",
                sequence=i+1
            )
    
    try:
        response_stream = stub.BidirectionalStream(generate_messages())
        
        response_count = 0
        for response in response_stream:
            response_count += 1
            print(f"  - Received response: {response.response}")
        
        if response_count == 3:
            print("✅ Bidirectional streaming RPC successful")
            return True
        else:
            print(f"❌ Bidirectional streaming RPC failed: Expected 3 responses, got {response_count}")
            return False
            
    except grpc.RpcError as e:
        print(f"❌ Bidirectional streaming RPC failed: {e.code()}: {e.details()}")
        return False

def test_metrics():
    """Test Prometheus metrics endpoint."""
    print("\nTesting metrics endpoint...")
    try:
        import requests
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("✅ Metrics endpoint is accessible")
            return True
        else:
            print(f"❌ Metrics endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to access metrics endpoint: {str(e)}")
        return False

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Set up the gRPC channel and stub
    server_address = 'localhost:50051'
    print(f"Connecting to gRPC server at {server_address}...")
    
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = example_pb2_grpc.GreeterStub(channel)
            
            # Run tests
            tests = [
                ("Unary RPC", lambda: test_unary_rpc(stub)),
                ("Server Streaming", lambda: test_server_streaming(stub)),
                ("Client Streaming", lambda: test_client_streaming(stub)),
                ("Bidirectional Streaming", lambda: test_bidirectional_streaming(stub)),
                ("Metrics Endpoint", test_metrics)
            ]
            
            success = True
            for test_name, test_func in tests:
                print(f"\n=== {test_name} ===")
                if not test_func():
                    success = False
            
            # Print final result
            print("\n=== Test Results ===")
            if success:
                print("✅ All tests passed!")
                sys.exit(0)
            else:
                print("❌ Some tests failed!")
                sys.exit(1)
                
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
