"""
yfinance gRPC Server Entry Point
"""

from src.server import serve

if __name__ == '__main__':
    serve(port=50059, max_workers=10)
