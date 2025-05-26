import time
import grpc
import logging
from concurrent import futures
from datetime import datetime
import os

# Import the generated gRPC stubs
import example_pb2
import example_pb2_grpc

# Import Prometheus metrics
from prometheus_client import start_http_server, Counter, Gauge, Histogram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'grpc_server_requests_total',
    'Total number of gRPC requests',
    ['method']
)
REQUEST_LATENCY = Histogram(
    'grpc_server_request_latency_seconds',
    'Latency of gRPC requests in seconds',
    ['method']
)
ACTIVE_REQUESTS = Gauge(
    'grpc_server_active_requests',
    'Number of active gRPC requests',
    ['method']
)

class Greeter(example_pb2_grpc.GreeterServicer):
    """Implementation of the gRPC service."""
    
    def __init__(self):
        self.server_id = f"grpc-server-{os.getpid()}"
        
    def _record_metrics(self, method_name, start_time):
        """Record metrics for the request."""
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method=method_name).observe(latency)
        ACTIVE_REQUESTS.labels(method=method_name).dec()
        logger.info(f"{method_name} completed in {latency:.4f}s")
    
    def SayHello(self, request, context):
        """Unary RPC method implementation."""
        method_name = "SayHello"
        start_time = time.time()
        ACTIVE_REQUESTS.labels(method=method_name).inc()
        REQUEST_COUNT.labels(method=method_name).inc()
        
        try:
            logger.info(f"Received SayHello request with name: {request.name}")
            
            # Create and return the response
            response = example_pb2.HelloReply(
                message=f"Hello, {request.name} from {self.server_id}!",
                status=200
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in {method_name}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return example_pb2.HelloReply()
            
        finally:
            self._record_metrics(method_name, start_time)
    
    def StreamData(self, request, context):
        """Server streaming RPC method implementation."""
        method_name = "StreamData"
        start_time = time.time()
        ACTIVE_REQUESTS.labels(method=method_name).inc()
        REQUEST_COUNT.labels(method=method_name).inc()
        
        try:
            logger.info(f"Streaming {request.count} messages with prefix: {request.prefix}")
            
            # Stream responses back to the client
            for i in range(request.count):
                if context.is_active():
                    response = example_pb2.DataResponse(
                        id=i,
                        value=f"{request.prefix}-{i}",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    yield response
                    time.sleep(0.1)  # Simulate work
                else:
                    logger.warning("Client disconnected")
                    break
                    
        except Exception as e:
            logger.error(f"Error in {method_name}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            
        finally:
            self._record_metrics(method_name, start_time)
    
    def ClientStream(self, request_iterator, context):
        """Client streaming RPC method implementation."""
        method_name = "ClientStream"
        start_time = time.time()
        ACTIVE_REQUESTS.labels(method=method_name).inc()
        REQUEST_COUNT.labels(method=method_name).inc()
        
        try:
            received_messages = []
            
            # Process incoming stream
            for request in request_iterator:
                received_messages.append(request)
                logger.info(f"Received message from {request.client_id}: {request.message}")
            
            # Return a single response
            return example_pb2.ServerResponse(
                server_id=self.server_id,
                response=f"Received {len(received_messages)} messages",
                received_sequence=len(received_messages),
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in {method_name}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return example_pb2.ServerResponse()
            
        finally:
            self._record_metrics(method_name, start_time)
    
    def BidirectionalStream(self, request_iterator, context):
        """Bidirectional streaming RPC method implementation."""
        method_name = "BidirectionalStream"
        start_time = time.time()
        ACTIVE_REQUESTS.labels(method=method_name).inc()
        REQUEST_COUNT.labels(method=method_name).inc()
        
        try:
            # Process incoming stream and send responses
            for request in request_iterator:
                if context.is_active():
                    # Process the request
                    logger.info(f"Bidirectional: {request.client_id} sent: {request.message}")
                    
                    # Send a response
                    response = example_pb2.ServerResponse(
                        server_id=self.server_id,
                        response=f"Echo: {request.message}",
                        received_sequence=request.sequence,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    yield response
                    
        except Exception as e:
            logger.error(f"Error in {method_name}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            
        finally:
            self._record_metrics(method_name, start_time)

def serve():
    """Start the gRPC server."""
    # Start Prometheus metrics server
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")
    
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the service implementation
    example_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    
    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    
    # Start the server
    server.start()
    logger.info("gRPC server started on port 50051")
    
    try:
        # Keep the server running
        while True:
            time.sleep(60 * 60 * 24)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
        logger.info("gRPC server stopped")

if __name__ == '__main__':
    # Generate gRPC code if it doesn't exist
    if not os.path.exists('example_pb2.py') or not os.path.exists('example_pb2_grpc.py'):
        logger.info("Generating gRPC code...")
        from grpc_tools import protoc
        protoc.main([
            'grpc_tools.protoc',
            '-I.',
            '--python_out=.',
            '--grpc_python_out=.',
            'protos/example.proto'
        ])
        logger.info("gRPC code generated")
    
    # Import the generated modules
    import example_pb2
    import example_pb2_grpc
    
    # Start the server
    serve()
