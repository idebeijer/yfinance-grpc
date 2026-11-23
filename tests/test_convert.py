"""Unit tests for yfinance_grpc_server.convert."""

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import pytest

from yfinance_grpc_server.convert import is_missing, safe_float, safe_int, safe_str, to_timestamp

MISSING = [None, float("nan"), np.nan, pd.NA, pd.NaT]


@pytest.mark.parametrize("value", MISSING)
def test_missing_values_become_zero_values(value):
    assert is_missing(value)
    assert safe_float(value) == 0.0
    assert safe_int(value) == 0
    assert safe_str(value) == ""
    assert to_timestamp(value) is None


def test_list_likes_are_not_missing():
    assert not is_missing([1, 2])
    assert not is_missing(np.array([np.nan, np.nan]))


def test_defaults_are_honoured():
    assert safe_float(None, default=-1.0) == -1.0
    assert safe_int(None, default=-1) == -1
    assert safe_str(None, default="n/a") == "n/a"


def test_valid_numbers_convert():
    assert safe_float(42.5) == 42.5
    assert safe_float(100) == 100.0
    assert safe_float(np.float64(1.5)) == 1.5
    assert safe_int(42) == 42
    assert safe_int(42.7) == 42
    assert safe_int(np.int64(7)) == 7


@pytest.mark.parametrize("value", ["abc", object(), float("inf")])
def test_unconvertible_numbers_fall_back_to_default(value):
    assert safe_int(value) == 0
    if not isinstance(value, float):
        assert safe_float(value) == 0.0


def test_safe_str():
    assert safe_str("test") == "test"
    assert safe_str(123) == "123"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (datetime(2025, 1, 15, 12, 30, 45), datetime(2025, 1, 15, 12, 30, 45)),
        (pd.Timestamp("2025-01-15 12:30:45"), datetime(2025, 1, 15, 12, 30, 45)),
        (date(2025, 1, 15), datetime(2025, 1, 15)),
        ("2025-01-15", datetime(2025, 1, 15)),
        ("2025-01-15T10:30:00Z", datetime(2025, 1, 15, 10, 30)),
        (datetime(2025, 1, 15, 12, tzinfo=UTC), datetime(2025, 1, 15, 12)),
    ],
)
def test_to_timestamp_converts(value, expected):
    ts = to_timestamp(value)
    assert ts is not None
    assert ts.ToDatetime() == expected


@pytest.mark.parametrize("value", ["not a date", 12345, object()])
def test_to_timestamp_rejects_unknown_values(value):
    assert to_timestamp(value) is None
