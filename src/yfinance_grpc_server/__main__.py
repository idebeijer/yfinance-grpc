"""Entry point: ``python -m yfinance_grpc_server`` or the ``yfinance-grpc`` script."""

import argparse
import logging
import os

from yfinance_grpc_server.server import DEFAULT_PORT, serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Yahoo Finance data over gRPC.")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", DEFAULT_PORT)),
        help=f"port to listen on (default: $PORT or {DEFAULT_PORT})",
    )
    parser.add_argument("--max-workers", type=int, default=10, help="worker threads (default: 10)")
    parser.add_argument(
        "--log-level",
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="logging level (default: $LOG_LEVEL or INFO)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    serve(port=args.port, max_workers=args.max_workers)


if __name__ == "__main__":
    main()
