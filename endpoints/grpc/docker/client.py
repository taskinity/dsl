#!/usr/bin/env python3
"""Test client for the gRPC service."""

import argparse
import logging
import sys
import time
from datetime import datetime

import grpc

# Import the generated gRPC stubs
import example_pb2
import example_pb2_grpc

def run_unary_rpc(stub, name="World"):
    """Test the unary RPC method."""
    print(f"\n=== Testing Unary RPC (SayHello) ===")
    try:
        response = stub.SayHello(example_pb2.HelloRequest(name=name))
        print(f"Response: {response.message} (Status: {response.status})")
        return True
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
        return False

def run_server_streaming(stub, count=5, prefix="test"):
    """Test the server streaming RPC method."""
    print(f"\n=== Testing Server Streaming (StreamData) ===")
    try:
        request = example_pb2.DataRequest(count=count, prefix=prefix)
        print(f"Requesting {count} messages with prefix: {prefix}")
        
        start_time = time.time()
        response_stream = stub.StreamData(request)
        
        print("Receiving messages:")
        received_count = 0
        for response in response_stream:
            received_count += 1
            print(f"  - ID: {response.id}, Value: {response.value}, Timestamp: {response.timestamp}")
        
        duration = time.time() - start_time
        print(f"Received {received_count} messages in {duration:.2f} seconds")
        return received_count == count
        
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
        return False

def run_client_streaming(stub, messages):
    """Test the client streaming RPC method."""
    print(f"\n=== Testing Client Streaming (ClientStream) ===")
    
    def generate_messages():
        for i, msg in enumerate(messages, 1):
            yield example_pb2.ClientMessage(
                client_id=f"client-{i}",
                message=msg,
                sequence=i
            )
    
    try:
        print(f"Sending {len(messages)} messages...")
        start_time = time.time()
        response = stub.ClientStream(generate_messages())
        duration = time.time() - start_time
        
        print(f"Server response: {response.response}")
        print(f"Received sequence: {response.received_sequence}")
        print(f"Server ID: {response.server_id}")
        print(f"Duration: {duration:.2f} seconds")
        
        return response.received_sequence == len(messages)
        
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
        return False

def run_bidirectional_streaming(stub, messages):
    """Test the bidirectional streaming RPC method."""
    print(f"\n=== Testing Bidirectional Streaming (BidirectionalStream) ===")
    
    def generate_messages():
        for i, msg in enumerate(messages, 1):
            yield example_pb2.ClientMessage(
                client_id=f"client-{i}",
                message=msg,
                sequence=i
            )
    
    try:
        print(f"Starting bidirectional stream with {len(messages)} messages...")
        start_time = time.time()
        
        # Start the RPC
        response_stream = stub.BidirectionalStream(generate_messages())
        
        # Process responses
        print("Responses:")
        response_count = 0
        for response in response_stream:
            response_count += 1
            print(f"  - {response.response} (Seq: {response.received_sequence})")
        
        duration = time.time() - start_time
        print(f"Received {response_count} responses in {duration:.2f} seconds")
        
        return response_count == len(messages)
        
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
        return False

def run_health_check(stub):
    """Run a simple health check."""
    try:
        response = stub.SayHello(example_pb2.HelloRequest(name="healthcheck"), timeout=5)
        print(f"Health check OK: {response.message}")
        return True
    except grpc.RpcError as e:
        print(f"Health check failed: {e.code()}: {e.details()}")
        return False

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='gRPC client for testing the mock service')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=50051, help='Server port (default: 50051)')
    parser.add_argument('--test', choices=['all', 'unary', 'server_stream', 'client_stream', 'bidi', 'health'], 
                       default='all', help='Test to run (default: all)')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Set up the gRPC channel and stub
    server_address = f'{args.host}:{args.port}'
    print(f"Connecting to gRPC server at {server_address}...")
    
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = example_pb2_grpc.GreeterStub(channel)
            
            # Run the selected test(s)
            success = True
            
            if args.test in ['all', 'health']:
                if not run_health_check(stub):
                    success = False
            
            if success and args.test in ['all', 'unary']:
                if not run_unary_rpc(stub, "Test User"):
                    success = False
            
            if success and args.test in ['all', 'server_stream']:
                if not run_server_streaming(stub, count=3, prefix="test"):
                    success = False
            
            if success and args.test in ['all', 'client_stream']:
                messages = [f"Message {i+1}" for i in range(3)]
                if not run_client_streaming(stub, messages):
                    success = False
            
            if success and args.test in ['all', 'bidi']:
                messages = [f"Bidi {i+1}" for i in range(3)]
                if not run_bidirectional_streaming(stub, messages):
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
