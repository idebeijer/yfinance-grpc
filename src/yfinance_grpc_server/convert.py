"""Convert yfinance and pandas values into values protobuf fields accept.

yfinance hands back ``None``, ``NaN``, ``pd.NA`` and ``pd.NaT`` freely, and
protobuf scalar fields reject all of them. Every servicer funnels values
through this module so that missing data has one meaning everywhere: the
field's zero value (or ``None`` for message fields such as timestamps).
"""

import logging
from datetime import date, datetime, time
from typing import Any

import pandas as pd
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)


def is_missing(value: Any) -> bool:
    """Return True for None and pandas/numpy missing-value markers."""
    if value is None:
        return True
    return bool(pd.api.types.is_scalar(value) and pd.isna(value))


def safe_float(value: Any, default: float = 0.0) -> float:
    if is_missing(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    if is_missing(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    if is_missing(value):
        return default
    return str(value)


def to_timestamp(value: Any) -> Timestamp | None:
    """Convert a datetime, date, pandas Timestamp or ISO-8601 string to a Timestamp.

    Naive values are treated as UTC; plain dates become midnight UTC.

    Returns None for missing or unparseable values, so callers can leave the
    message field unset.
    """
    if is_missing(value):
        return None
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            logger.warning("Unparseable timestamp %r", value)
            return None
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, time())
    if isinstance(value, datetime):
        ts = Timestamp()
        ts.FromDatetime(value)
        return ts
    return None
