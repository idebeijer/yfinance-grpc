import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LookupType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOOKUP_TYPE_UNSPECIFIED: _ClassVar[LookupType]
    LOOKUP_TYPE_ALL: _ClassVar[LookupType]
    LOOKUP_TYPE_EQUITY: _ClassVar[LookupType]
    LOOKUP_TYPE_MUTUALFUND: _ClassVar[LookupType]
    LOOKUP_TYPE_ETF: _ClassVar[LookupType]
    LOOKUP_TYPE_INDEX: _ClassVar[LookupType]
    LOOKUP_TYPE_FUTURE: _ClassVar[LookupType]
    LOOKUP_TYPE_CURRENCY: _ClassVar[LookupType]
    LOOKUP_TYPE_CRYPTOCURRENCY: _ClassVar[LookupType]
LOOKUP_TYPE_UNSPECIFIED: LookupType
LOOKUP_TYPE_ALL: LookupType
LOOKUP_TYPE_EQUITY: LookupType
LOOKUP_TYPE_MUTUALFUND: LookupType
LOOKUP_TYPE_ETF: LookupType
LOOKUP_TYPE_INDEX: LookupType
LOOKUP_TYPE_FUTURE: LookupType
LOOKUP_TYPE_CURRENCY: LookupType
LOOKUP_TYPE_CRYPTOCURRENCY: LookupType

class SearchRequest(_message.Message):
    __slots__ = ()
    QUERY_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    NEWS_COUNT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FUZZY_QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    max_results: int
    news_count: int
    enable_fuzzy_query: bool
    def __init__(self, query: _Optional[str] = ..., max_results: _Optional[int] = ..., news_count: _Optional[int] = ..., enable_fuzzy_query: _Optional[bool] = ...) -> None: ...

class SearchQuote(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    LONG_NAME_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    QUOTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    TYPE_DISP_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    short_name: str
    long_name: str
    exchange: str
    quote_type: str
    sector: str
    industry: str
    type_disp: str
    score: float
    def __init__(self, symbol: _Optional[str] = ..., short_name: _Optional[str] = ..., long_name: _Optional[str] = ..., exchange: _Optional[str] = ..., quote_type: _Optional[str] = ..., sector: _Optional[str] = ..., industry: _Optional[str] = ..., type_disp: _Optional[str] = ..., score: _Optional[float] = ...) -> None: ...

class SearchNewsItem(_message.Message):
    __slots__ = ()
    UUID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_PUBLISH_TIME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    title: str
    publisher: str
    link: str
    provider_publish_time: _timestamp_pb2.Timestamp
    type: str
    def __init__(self, uuid: _Optional[str] = ..., title: _Optional[str] = ..., publisher: _Optional[str] = ..., link: _Optional[str] = ..., provider_publish_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ()
    QUOTES_FIELD_NUMBER: _ClassVar[int]
    NEWS_FIELD_NUMBER: _ClassVar[int]
    quotes: _containers.RepeatedCompositeFieldContainer[SearchQuote]
    news: _containers.RepeatedCompositeFieldContainer[SearchNewsItem]
    def __init__(self, quotes: _Optional[_Iterable[_Union[SearchQuote, _Mapping]]] = ..., news: _Optional[_Iterable[_Union[SearchNewsItem, _Mapping]]] = ...) -> None: ...

class LookupRequest(_message.Message):
    __slots__ = ()
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    query: str
    type: LookupType
    count: int
    def __init__(self, query: _Optional[str] = ..., type: _Optional[_Union[LookupType, str]] = ..., count: _Optional[int] = ...) -> None: ...

class LookupResult(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    QUOTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    exchange: str
    quote_type: str
    score: float
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., exchange: _Optional[str] = ..., quote_type: _Optional[str] = ..., score: _Optional[float] = ...) -> None: ...

class LookupResponse(_message.Message):
    __slots__ = ()
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[LookupResult]
    def __init__(self, results: _Optional[_Iterable[_Union[LookupResult, _Mapping]]] = ...) -> None: ...
