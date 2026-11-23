"""Unit tests for yfinance_grpc_server.errors."""

from unittest.mock import ANY, Mock

import grpc
import pytest
from yfinance.exceptions import YFInvalidPeriodError, YFRateLimitError

from yfinance_grpc_server.errors import invalid_argument, not_found, require, rpc


class _AbortError(Exception):
    """Stands in for the exception grpc's real ServicerContext.abort raises."""


def _context():
    context = Mock()
    context.abort.side_effect = _AbortError
    return context


class _Servicer:
    def __init__(self, exc=None, result="ok"):
        self.exc = exc
        self.result = result

    @rpc
    def Unary(self, request, context):
        if self.exc:
            raise self.exc
        return self.result

    @rpc
    def Stream(self, request, context):
        yield 1
        if self.exc:
            raise self.exc
        yield 2


def test_success_passes_through():
    context = _context()
    assert _Servicer().Unary(None, context) == "ok"
    assert list(_Servicer().Stream(None, context)) == [1, 2]
    context.abort.assert_not_called()


@pytest.mark.parametrize(
    ("exc", "code", "details"),
    [
        (invalid_argument("bad"), grpc.StatusCode.INVALID_ARGUMENT, "bad"),
        (not_found("gone"), grpc.StatusCode.NOT_FOUND, "gone"),
        (YFRateLimitError(), grpc.StatusCode.RESOURCE_EXHAUSTED, ANY),
        (YFInvalidPeriodError("AAPL", "7y", "1d, 5d"), grpc.StatusCode.INVALID_ARGUMENT, ANY),
        (RuntimeError("secret internals"), grpc.StatusCode.INTERNAL, "Unary failed; see server logs"),
    ],
)
def test_unary_maps_exceptions_to_status(exc, code, details):
    context = _context()
    with pytest.raises(_AbortError):
        _Servicer(exc).Unary(None, context)
    context.abort.assert_called_once_with(code, details)


def test_streaming_aborts_after_partial_output():
    context = _context()
    received = []
    with pytest.raises(_AbortError):
        received.extend(_Servicer(not_found("gone")).Stream(None, context))
    assert received == [1]
    context.abort.assert_called_once_with(grpc.StatusCode.NOT_FOUND, "gone")


def test_internal_errors_are_logged_without_leaking_details(caplog):
    context = _context()
    with pytest.raises(_AbortError):
        _Servicer(RuntimeError("secret internals")).Unary(None, context)
    assert "secret internals" not in str(context.abort.call_args)
    assert "Unary failed" in caplog.text


def test_require():
    assert require("AAPL", "ticker") == "AAPL"
    with pytest.raises(Exception, match="ticker must not be empty"):
        require("", "ticker")
