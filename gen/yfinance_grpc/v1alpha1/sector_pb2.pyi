from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DomainOverview(_message.Message):
    __slots__ = ()
    COMPANIES_COUNT_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INDUSTRIES_COUNT_FIELD_NUMBER: _ClassVar[int]
    MARKET_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_COUNT_FIELD_NUMBER: _ClassVar[int]
    companies_count: int
    market_cap: float
    description: str
    industries_count: int
    market_weight: float
    employee_count: float
    def __init__(self, companies_count: _Optional[int] = ..., market_cap: _Optional[float] = ..., description: _Optional[str] = ..., industries_count: _Optional[int] = ..., market_weight: _Optional[float] = ..., employee_count: _Optional[float] = ...) -> None: ...

class DomainCompany(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    MARKET_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    rating: str
    market_weight: float
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., rating: _Optional[str] = ..., market_weight: _Optional[float] = ...) -> None: ...

class GetSectorRequest(_message.Message):
    __slots__ = ()
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class IndustryInfo(_message.Message):
    __slots__ = ()
    KEY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    key: str
    name: str
    symbol: str
    market_weight: float
    def __init__(self, key: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., market_weight: _Optional[float] = ...) -> None: ...

class GetSectorResponse(_message.Message):
    __slots__ = ()
    class TopEtfsEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class TopMutualFundsEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KEY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    OVERVIEW_FIELD_NUMBER: _ClassVar[int]
    TOP_COMPANIES_FIELD_NUMBER: _ClassVar[int]
    TOP_ETFS_FIELD_NUMBER: _ClassVar[int]
    TOP_MUTUAL_FUNDS_FIELD_NUMBER: _ClassVar[int]
    INDUSTRIES_FIELD_NUMBER: _ClassVar[int]
    key: str
    name: str
    symbol: str
    overview: DomainOverview
    top_companies: _containers.RepeatedCompositeFieldContainer[DomainCompany]
    top_etfs: _containers.ScalarMap[str, str]
    top_mutual_funds: _containers.ScalarMap[str, str]
    industries: _containers.RepeatedCompositeFieldContainer[IndustryInfo]
    def __init__(self, key: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., overview: _Optional[_Union[DomainOverview, _Mapping]] = ..., top_companies: _Optional[_Iterable[_Union[DomainCompany, _Mapping]]] = ..., top_etfs: _Optional[_Mapping[str, str]] = ..., top_mutual_funds: _Optional[_Mapping[str, str]] = ..., industries: _Optional[_Iterable[_Union[IndustryInfo, _Mapping]]] = ...) -> None: ...

class GetIndustryRequest(_message.Message):
    __slots__ = ()
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class TopPerformingCompany(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    YTD_RETURN_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    TARGET_PRICE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    ytd_return: float
    last_price: float
    target_price: float
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., ytd_return: _Optional[float] = ..., last_price: _Optional[float] = ..., target_price: _Optional[float] = ...) -> None: ...

class TopGrowthCompany(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    YTD_RETURN_FIELD_NUMBER: _ClassVar[int]
    GROWTH_ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    ytd_return: float
    growth_estimate: float
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., ytd_return: _Optional[float] = ..., growth_estimate: _Optional[float] = ...) -> None: ...

class GetIndustryResponse(_message.Message):
    __slots__ = ()
    KEY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SECTOR_KEY_FIELD_NUMBER: _ClassVar[int]
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    OVERVIEW_FIELD_NUMBER: _ClassVar[int]
    TOP_COMPANIES_FIELD_NUMBER: _ClassVar[int]
    TOP_PERFORMING_COMPANIES_FIELD_NUMBER: _ClassVar[int]
    TOP_GROWTH_COMPANIES_FIELD_NUMBER: _ClassVar[int]
    key: str
    name: str
    symbol: str
    sector_key: str
    sector_name: str
    overview: DomainOverview
    top_companies: _containers.RepeatedCompositeFieldContainer[DomainCompany]
    top_performing_companies: _containers.RepeatedCompositeFieldContainer[TopPerformingCompany]
    top_growth_companies: _containers.RepeatedCompositeFieldContainer[TopGrowthCompany]
    def __init__(self, key: _Optional[str] = ..., name: _Optional[str] = ..., symbol: _Optional[str] = ..., sector_key: _Optional[str] = ..., sector_name: _Optional[str] = ..., overview: _Optional[_Union[DomainOverview, _Mapping]] = ..., top_companies: _Optional[_Iterable[_Union[DomainCompany, _Mapping]]] = ..., top_performing_companies: _Optional[_Iterable[_Union[TopPerformingCompany, _Mapping]]] = ..., top_growth_companies: _Optional[_Iterable[_Union[TopGrowthCompany, _Mapping]]] = ...) -> None: ...
