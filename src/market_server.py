"""MarketService gRPC implementation. Wraps yfinance.Market."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
import logging
from datetime import datetime

import yfinance as yf
import pandas as pd

from yfinance_grpc.v1alpha1 import market_pb2, market_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)


def safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_int(val, default: int = 0) -> int:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return int(val)
    except (TypeError, ValueError):
        return default


def safe_str(val, default: str = "") -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    return str(val)


def _dt_to_ts(dt) -> Timestamp | None:
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    if isinstance(dt, datetime):
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts
    return None


class MarketServiceServicer(market_pb2_grpc.MarketServiceServicer):
    def GetMarketStatus(self, request, context):
        if not request.market:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("market must not be empty")
            return market_pb2.GetMarketStatusResponse()
        try:
            status = yf.Market(request.market).status
            if not status:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No status data for market '{request.market}'")
                return market_pb2.GetMarketStatusResponse()

            tz = status.get("timezone") if isinstance(status.get("timezone"), dict) else {}
            msg = market_pb2.MarketStatus(
                market_type=safe_str(status.get("type")),
                timezone_short=safe_str(tz.get("short")),
                timezone_gmtoffset=safe_int(tz.get("gmtoffset")),
            )
            for field, attr in (("open", "open"), ("close", "close")):
                ts = _dt_to_ts(status.get(attr))
                if ts:
                    getattr(msg, field).CopyFrom(ts)

            return market_pb2.GetMarketStatusResponse(status=msg)
        except Exception as e:
            logger.error(f"Error in GetMarketStatus for '{request.market}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching market status: {e}")
            return market_pb2.GetMarketStatusResponse()

    def GetMarketSummary(self, request, context):
        if not request.market:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("market must not be empty")
            return market_pb2.GetMarketSummaryResponse()
        try:
            summary = yf.Market(request.market).summary
            if not summary:
                return market_pb2.GetMarketSummaryResponse()

            items = {
                exchange: market_pb2.MarketSummaryItem(
                    short_name=safe_str(data.get("shortName")),
                    regular_market_price=safe_float(data.get("regularMarketPrice")),
                    regular_market_change=safe_float(data.get("regularMarketChange")),
                    regular_market_change_percent=safe_float(data.get("regularMarketChangePercent")),
                )
                for exchange, data in summary.items()
            }
            return market_pb2.GetMarketSummaryResponse(summary=items)
        except Exception as e:
            logger.error(f"Error in GetMarketSummary for '{request.market}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching market summary: {e}")
            return market_pb2.GetMarketSummaryResponse()
