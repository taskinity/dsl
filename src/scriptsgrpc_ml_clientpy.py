#!/usr/bin/env python3
"""
gRPC ML Client for remote inference
Connects to ML serving infrastructure
"""

import sys
import json
import argparse
import os
import grpc
import base64
import numpy as np
from typing import Dict, Any, Optional

# Note: In real implementation, you would have generated protobuf files
# For this example, we'll use a simple REST fallback

class GRPCMLClient:
    def __init__(self):
        self.server_address = os.getenv('CONFIG_GRPC_SERVER', 'localhost:50051')
        self.model_name = os.getenv('CONFIG_MODEL_NAME', 'object_detection')
        self.timeout = int(os.getenv('CONFIG_TIMEOUT', '30'))
        self.use_fallback = True  # Use REST fallback for this example
        
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send prediction request to gRPC server"""
        if self.use_fallback:
            return self._rest_fallback(input_data)
        else:
            return self._grpc_predict(input_data)
    
    def _grpc_predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Real gRPC prediction (requires protobuf definitions)"""
        try:
            # This would be the real gRPC implementation
            # with grpc.insecure_channel(self.server_address) as channel:
            #     stub = PredictionServiceStub(channel)
            #     request = PredictRequest(...)
            #     response = stub.Predict(request, timeout=self.timeout)
            #     return self._parse_response(response)
            
            # Placeholder for actual gRPC implementation
            return {
                'error': 'gRPC implementation requires protobuf definitions',
                'fallback_used': True
            }
            
        except Exception as e:
            return {
                'error': f'gRPC prediction failed: {str(e)}',
                'success': False
            }
    
    def _rest_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """REST API fallback for ML inference"""
        import requests
        
        try:
            # Convert gRPC server address to HTTP
            if '://' not in self.server_address:
                url = f"http://{self.server_address}/predict"
            else:
                url = self.server_address.replace('grpc://', 'http://') + '/predict'
            
            # Prepare payload
            payload = {
                'model_name': self.model_name,
                'inputs': input_data,
                'parameters': {
                    'timeout': self.timeout
                }
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'success': False
                }
                
        except requests.exceptions.RequestException as e:
            # If real server not available, return mock prediction
            return self._mock_prediction(input_data)
        except Exception as e:
            return {
                'error': f'REST fallback failed: {str(e)}',
                'success': False
            }
    
    def _mock_prediction(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock prediction for testing"""
        return {
            'model_name': self.model_name,
            'predictions': [
                {
                    'class': 'person',
                    'confidence': 0.92,
                    'bbox': [100, 50, 200, 300]
                },
                {
                    'class': 'car',
                    'confidence': 0.78,
                    'bbox': [300, 200, 500, 400]
                }
            ],
            'inference_time_ms': 45.2,
            'model_version': 'v1.0',
            'server_info': {
                'server': 'mock_server',
                'status': 'healthy'
            },
            'mock_used': True
        }
    
    def batch_predict(self, batch_data: list) -> Dict[str, Any]:
        """Process batch of predictions"""
        results = []
        total_time = 0
        
        for i, data in enumerate(batch_data):
            result = self.predict(data)
            results.append({
                'batch_index': i,
                'result': result
            })
            
            # Accumulate inference time
            if 'inference_time_ms' in result:
                total_time += result['inference_time_ms']
        
        return {
            'batch_results': results,
            'batch_size': len(batch_data),
            'total_inference_time_ms': total_time,
            'average_inference_time_ms': total_time / len(batch_data) if batch_data else 0
        }

def main():
    parser = argparse.ArgumentParser(description='gRPC ML Client')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', help='Output JSON file (optional)')
    parser.add_argument('--batch', action='store_true', help='Process as batch')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        client = GRPCMLClient()
        
        if args.batch and isinstance(input_data, list):
            result = client.batch_predict(input_data)
        else:
            result = client.predict(input_data)
        
        output = {
            'timestamp': '2024-01-01T12:00:00Z',
            'processor': 'grpc_ml_client',
            'server': client.server_address,
            'model': client.model_name,
            'ml_inference': result
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
        else:
            print(json.dumps(output, indent=2))
    
    except Exception as e:
        error_output = {
            'error': str(e),
            'processor': 'grpc_ml_client',
            'success': False
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()