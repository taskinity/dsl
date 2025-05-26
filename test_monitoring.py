#!/usr/bin/env python3
"""
Test script for the monitoring dashboard.
"""
import os
import sys
import time
import threading
import http.server
import socketserver
import webbrowser

def start_http_server(port=8080):
    """Start a simple HTTP server in the monitoring directory."""
    os.chdir(os.path.join(os.path.dirname(__file__), 'monitoring'))
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving monitoring dashboard at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()
            sys.exit(0)

if __name__ == "__main__":
    print("Starting monitoring dashboard...")
    print("Press Ctrl+C to stop")
    
    try:
        # Start the server in the main thread
        start_http_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
