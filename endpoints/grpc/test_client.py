import grpc
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the generated gRPC modules
import example_pb2
import example_pb2_grpc

def run():
    # Create a channel to the server
    with grpc.insecure_channel('localhost:50051') as channel:
        # Create a stub (client)
        stub = example_pb2_grpc.GreeterStub(channel)
        
        # Test unary RPC
        print("Testing SayHello RPC...")
        response = stub.SayHello(example_pb2.HelloRequest(name='World'))
        print(f"Server responded: {response.message}")
        
        # Test server streaming RPC
        print("\nTesting StreamData RPC...")
        response_stream = stub.StreamData(example_pb2.DataRequest(count=3, prefix="test"))
        print("Server streaming response:")
        for response in response_stream:
            print(f"  - ID: {response.id}, Value: {response.value}, Timestamp: {response.timestamp}")
            
        # Test client streaming RPC
        print("\nTesting ClientStream RPC...")
        def generate_messages():
            messages = [
                example_pb2.ClientMessage(client_id="client-1", message="Hello 1", sequence=1),
                example_pb2.ClientMessage(client_id="client-1", message="Hello 2", sequence=2),
                example_pb2.ClientMessage(client_id="client-1", message="Hello 3", sequence=3),
            ]
            for msg in messages:
                print(f"  - Sending: {msg.message}")
                yield msg
                
        response = stub.ClientStream(generate_messages())
        print(f"Server response: {response.response} (Server ID: {response.server_id}, Sequence: {response.received_sequence}, Timestamp: {response.timestamp})")
        
        # Test bidirectional streaming RPC
        print("\nTesting BidirectionalStream RPC...")
        def generate_bidi_messages():
            messages = [
                example_pb2.ClientMessage(client_id="bidic-1", message="Ping 1", sequence=1),
                example_pb2.ClientMessage(client_id="bidic-1", message="Ping 2", sequence=2),
                example_pb2.ClientMessage(client_id="bidic-1", message="Ping 3", sequence=3),
            ]
            for msg in messages:
                print(f"  - Sending: {msg.message}")
                yield msg
                
        response_stream = stub.BidirectionalStream(generate_bidi_messages())
        for response in response_stream:
            print(f"  - Received: {response.response} (Server ID: {response.server_id}, Sequence: {response.received_sequence}, Timestamp: {response.timestamp})")

if __name__ == '__main__':
    run()
