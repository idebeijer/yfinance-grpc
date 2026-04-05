import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetMarketStatusRequest(_message.Message):
    __slots__ = ()
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: str
    def __init__(self, market: _Optional[str] = ...) -> None: ...

class MarketStatus(_message.Message):
    __slots__ = ()
    MARKET_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_SHORT_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_GMTOFFSET_FIELD_NUMBER: _ClassVar[int]
    market_type: str
    open: _timestamp_pb2.Timestamp
    close: _timestamp_pb2.Timestamp
    timezone_short: str
    timezone_gmtoffset: int
    def __init__(self, market_type: _Optional[str] = ..., open: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., close: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., timezone_short: _Optional[str] = ..., timezone_gmtoffset: _Optional[int] = ...) -> None: ...

class GetMarketStatusResponse(_message.Message):
    __slots__ = ()
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: MarketStatus
    def __init__(self, status: _Optional[_Union[MarketStatus, _Mapping]] = ...) -> None: ...

class GetMarketSummaryRequest(_message.Message):
    __slots__ = ()
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: str
    def __init__(self, market: _Optional[str] = ...) -> None: ...

class MarketSummaryItem(_message.Message):
    __slots__ = ()
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_PRICE_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_CHANGE_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    short_name: str
    regular_market_price: float
    regular_market_change: float
    regular_market_change_percent: float
    def __init__(self, short_name: _Optional[str] = ..., regular_market_price: _Optional[float] = ..., regular_market_change: _Optional[float] = ..., regular_market_change_percent: _Optional[float] = ...) -> None: ...

class GetMarketSummaryResponse(_message.Message):
    __slots__ = ()
    class SummaryEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MarketSummaryItem
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MarketSummaryItem, _Mapping]] = ...) -> None: ...
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    summary: _containers.MessageMap[str, MarketSummaryItem]
    def __init__(self, summary: _Optional[_Mapping[str, MarketSummaryItem]] = ...) -> None: ...
