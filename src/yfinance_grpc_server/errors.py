"""Map RPC handler outcomes onto gRPC status codes.

Every servicer method is wrapped in ``@rpc``. Handlers raise ``RpcError``
(built with the helpers below) for client-facing failures and let anything
else propagate; ``@rpc`` turns the former into their status code, known
yfinance exceptions into a matching code, and everything else into INTERNAL
with the traceback logged server-side. Handlers never call
``context.set_code`` themselves.
"""

import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any

import grpc
from yfinance.exceptions import (
    YFInvalidPeriodError,
    YFRateLimitError,
    YFTickerMissingError,
)

logger = logging.getLogger(__name__)


class RpcError(Exception):
    """A failure to report to the client with a specific status code."""

    def __init__(self, code: grpc.StatusCode, details: str) -> None:
        super().__init__(details)
        self.code = code
        self.details = details


def invalid_argument(details: str) -> RpcError:
    return RpcError(grpc.StatusCode.INVALID_ARGUMENT, details)


def not_found(details: str) -> RpcError:
    return RpcError(grpc.StatusCode.NOT_FOUND, details)


def unimplemented(details: str) -> RpcError:
    return RpcError(grpc.StatusCode.UNIMPLEMENTED, details)


def require(value: str, field: str) -> str:
    """Return ``value``, or raise INVALID_ARGUMENT if it is empty."""
    if not value:
        raise invalid_argument(f"{field} must not be empty")
    return value


def _status_for(exc: Exception, method: str) -> tuple[grpc.StatusCode, str]:
    match exc:
        case RpcError():
            return exc.code, exc.details
        case YFRateLimitError():
            return grpc.StatusCode.RESOURCE_EXHAUSTED, "Rate limited by Yahoo Finance; retry later"
        case YFInvalidPeriodError():
            return grpc.StatusCode.INVALID_ARGUMENT, str(exc)
        case YFTickerMissingError():
            return grpc.StatusCode.NOT_FOUND, str(exc)
    logger.error("%s failed", method, exc_info=exc)
    return grpc.StatusCode.INTERNAL, f"{method} failed; see server logs"


def rpc[F: Callable[..., Any]](method: F) -> F:
    """Wrap a unary or server-streaming servicer method with status mapping."""
    name = method.__name__

    if inspect.isgeneratorfunction(method):

        @functools.wraps(method)
        def stream(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
            try:
                yield from method(self, request, context)
            except Exception as exc:  # noqa: BLE001 - mapped to a status code
                context.abort(*_status_for(exc, name))

        return stream  # type: ignore[return-value]

    @functools.wraps(method)
    def unary(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
        try:
            return method(self, request, context)
        except Exception as exc:  # noqa: BLE001 - mapped to a status code
            context.abort(*_status_for(exc, name))

    return unary  # type: ignore[return-value]
