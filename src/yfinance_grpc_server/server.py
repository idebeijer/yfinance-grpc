"""Build and run the gRPC server: all four services plus reflection."""

import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from yfinance_grpc.v1alpha1 import (
    market_pb2,
    market_pb2_grpc,
    search_pb2,
    search_pb2_grpc,
    sector_pb2,
    sector_pb2_grpc,
    ticker_pb2,
    ticker_pb2_grpc,
)

from yfinance_grpc_server.market import MarketServiceServicer
from yfinance_grpc_server.search import SearchServiceServicer
from yfinance_grpc_server.sector import SectorServiceServicer
from yfinance_grpc_server.ticker import TickerServiceServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50059

_SERVICE_NAMES = (
    ticker_pb2.DESCRIPTOR.services_by_name["TickerService"].full_name,
    search_pb2.DESCRIPTOR.services_by_name["SearchService"].full_name,
    market_pb2.DESCRIPTOR.services_by_name["MarketService"].full_name,
    sector_pb2.DESCRIPTOR.services_by_name["SectorService"].full_name,
    reflection.SERVICE_NAME,
)


def build_server(max_workers: int = 10) -> grpc.Server:
    """Create a server with every service and reflection registered (not started)."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    ticker_pb2_grpc.add_TickerServiceServicer_to_server(TickerServiceServicer(), server)
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchServiceServicer(), server)
    market_pb2_grpc.add_MarketServiceServicer_to_server(MarketServiceServicer(), server)
    sector_pb2_grpc.add_SectorServiceServicer_to_server(SectorServiceServicer(), server)
    reflection.enable_server_reflection(_SERVICE_NAMES, server)
    return server


def serve(port: int = DEFAULT_PORT, max_workers: int = 10) -> None:
    """Start the server and block until interrupted."""
    server = build_server(max_workers)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info("Server listening on port %d with reflection enabled", port)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        server.stop(grace=5)
