import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetInfoRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetInfoResponse(_message.Message):
    __slots__ = ()
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: TickerInfo
    def __init__(self, info: _Optional[_Union[TickerInfo, _Mapping]] = ...) -> None: ...

class TickerInfo(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    LONG_NAME_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ZIP_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    LONG_BUSINESS_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    DAY_LOW_FIELD_NUMBER: _ClassVar[int]
    DAY_HIGH_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_PREVIOUS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_OPEN_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_DAY_LOW_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_DAY_HIGH_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MARKET_VOLUME_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_VOLUME_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_VOLUME_10DAYS_FIELD_NUMBER: _ClassVar[int]
    SHARES_OUTSTANDING_FIELD_NUMBER: _ClassVar[int]
    FLOAT_SHARES_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    ENTERPRISE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TRAILING_PE_FIELD_NUMBER: _ClassVar[int]
    FORWARD_PE_FIELD_NUMBER: _ClassVar[int]
    PRICE_TO_BOOK_FIELD_NUMBER: _ClassVar[int]
    PRICE_TO_SALES_TRAILING_12MONTHS_FIELD_NUMBER: _ClassVar[int]
    ENTERPRISE_TO_REVENUE_FIELD_NUMBER: _ClassVar[int]
    ENTERPRISE_TO_EBITDA_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_RATE_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_YIELD_FIELD_NUMBER: _ClassVar[int]
    EX_DIVIDEND_DATE_FIELD_NUMBER: _ClassVar[int]
    PAYOUT_RATIO_FIELD_NUMBER: _ClassVar[int]
    FIVE_YEAR_AVG_DIVIDEND_YIELD_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    TRAILING_EPS_FIELD_NUMBER: _ClassVar[int]
    FORWARD_EPS_FIELD_NUMBER: _ClassVar[int]
    BOOK_VALUE_FIELD_NUMBER: _ClassVar[int]
    PROFIT_MARGINS_FIELD_NUMBER: _ClassVar[int]
    REVENUE_PER_SHARE_FIELD_NUMBER: _ClassVar[int]
    RETURN_ON_ASSETS_FIELD_NUMBER: _ClassVar[int]
    RETURN_ON_EQUITY_FIELD_NUMBER: _ClassVar[int]
    REVENUE_GROWTH_FIELD_NUMBER: _ClassVar[int]
    EARNINGS_GROWTH_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MARGINS_FIELD_NUMBER: _ClassVar[int]
    EBITDA_MARGINS_FIELD_NUMBER: _ClassVar[int]
    FIFTY_TWO_WEEK_LOW_FIELD_NUMBER: _ClassVar[int]
    FIFTY_TWO_WEEK_HIGH_FIELD_NUMBER: _ClassVar[int]
    FIFTY_DAY_AVERAGE_FIELD_NUMBER: _ClassVar[int]
    TWO_HUNDRED_DAY_AVERAGE_FIELD_NUMBER: _ClassVar[int]
    TARGET_HIGH_PRICE_FIELD_NUMBER: _ClassVar[int]
    TARGET_LOW_PRICE_FIELD_NUMBER: _ClassVar[int]
    TARGET_MEAN_PRICE_FIELD_NUMBER: _ClassVar[int]
    TARGET_MEDIAN_PRICE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ANALYST_OPINIONS_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    QUOTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FINANCIAL_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PRICE_HINT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    short_name: str
    long_name: str
    industry: str
    sector: str
    country: str
    city: str
    state: str
    zip: str
    website: str
    long_business_summary: str
    previous_close: float
    open: float
    day_low: float
    day_high: float
    regular_market_previous_close: float
    regular_market_open: float
    regular_market_day_low: float
    regular_market_day_high: float
    current_price: float
    volume: int
    regular_market_volume: int
    average_volume: int
    average_volume_10days: int
    shares_outstanding: int
    float_shares: int
    market_cap: int
    enterprise_value: float
    trailing_pe: float
    forward_pe: float
    price_to_book: float
    price_to_sales_trailing_12months: float
    enterprise_to_revenue: float
    enterprise_to_ebitda: float
    dividend_rate: float
    dividend_yield: float
    ex_dividend_date: int
    payout_ratio: float
    five_year_avg_dividend_yield: float
    beta: float
    trailing_eps: float
    forward_eps: float
    book_value: float
    profit_margins: float
    revenue_per_share: float
    return_on_assets: float
    return_on_equity: float
    revenue_growth: float
    earnings_growth: float
    operating_margins: float
    ebitda_margins: float
    fifty_two_week_low: float
    fifty_two_week_high: float
    fifty_day_average: float
    two_hundred_day_average: float
    target_high_price: float
    target_low_price: float
    target_mean_price: float
    target_median_price: float
    number_of_analyst_opinions: int
    currency: str
    exchange: str
    quote_type: str
    financial_currency: str
    price_hint: int
    def __init__(self, symbol: _Optional[str] = ..., short_name: _Optional[str] = ..., long_name: _Optional[str] = ..., industry: _Optional[str] = ..., sector: _Optional[str] = ..., country: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., zip: _Optional[str] = ..., website: _Optional[str] = ..., long_business_summary: _Optional[str] = ..., previous_close: _Optional[float] = ..., open: _Optional[float] = ..., day_low: _Optional[float] = ..., day_high: _Optional[float] = ..., regular_market_previous_close: _Optional[float] = ..., regular_market_open: _Optional[float] = ..., regular_market_day_low: _Optional[float] = ..., regular_market_day_high: _Optional[float] = ..., current_price: _Optional[float] = ..., volume: _Optional[int] = ..., regular_market_volume: _Optional[int] = ..., average_volume: _Optional[int] = ..., average_volume_10days: _Optional[int] = ..., shares_outstanding: _Optional[int] = ..., float_shares: _Optional[int] = ..., market_cap: _Optional[int] = ..., enterprise_value: _Optional[float] = ..., trailing_pe: _Optional[float] = ..., forward_pe: _Optional[float] = ..., price_to_book: _Optional[float] = ..., price_to_sales_trailing_12months: _Optional[float] = ..., enterprise_to_revenue: _Optional[float] = ..., enterprise_to_ebitda: _Optional[float] = ..., dividend_rate: _Optional[float] = ..., dividend_yield: _Optional[float] = ..., ex_dividend_date: _Optional[int] = ..., payout_ratio: _Optional[float] = ..., five_year_avg_dividend_yield: _Optional[float] = ..., beta: _Optional[float] = ..., trailing_eps: _Optional[float] = ..., forward_eps: _Optional[float] = ..., book_value: _Optional[float] = ..., profit_margins: _Optional[float] = ..., revenue_per_share: _Optional[float] = ..., return_on_assets: _Optional[float] = ..., return_on_equity: _Optional[float] = ..., revenue_growth: _Optional[float] = ..., earnings_growth: _Optional[float] = ..., operating_margins: _Optional[float] = ..., ebitda_margins: _Optional[float] = ..., fifty_two_week_low: _Optional[float] = ..., fifty_two_week_high: _Optional[float] = ..., fifty_day_average: _Optional[float] = ..., two_hundred_day_average: _Optional[float] = ..., target_high_price: _Optional[float] = ..., target_low_price: _Optional[float] = ..., target_mean_price: _Optional[float] = ..., target_median_price: _Optional[float] = ..., number_of_analyst_opinions: _Optional[int] = ..., currency: _Optional[str] = ..., exchange: _Optional[str] = ..., quote_type: _Optional[str] = ..., financial_currency: _Optional[str] = ..., price_hint: _Optional[int] = ...) -> None: ...

class GetHistoryRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    PREPOST_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    AUTO_ADJUST_FIELD_NUMBER: _ClassVar[int]
    BACK_ADJUST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_FIELD_NUMBER: _ClassVar[int]
    KEEPNA_FIELD_NUMBER: _ClassVar[int]
    ROUNDING_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    period: str
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    interval: str
    prepost: bool
    actions: bool
    auto_adjust: bool
    back_adjust: bool
    repair: bool
    keepna: bool
    rounding: bool
    def __init__(self, ticker: _Optional[str] = ..., period: _Optional[str] = ..., start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., interval: _Optional[str] = ..., prepost: _Optional[bool] = ..., actions: _Optional[bool] = ..., auto_adjust: _Optional[bool] = ..., back_adjust: _Optional[bool] = ..., repair: _Optional[bool] = ..., keepna: _Optional[bool] = ..., rounding: _Optional[bool] = ...) -> None: ...

class GetHistoryResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[HistoryRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[HistoryRow, _Mapping]]] = ...) -> None: ...

class HistoryRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    DIVIDENDS_FIELD_NUMBER: _ClassVar[int]
    STOCK_SPLITS_FIELD_NUMBER: _ClassVar[int]
    CAPITAL_GAINS_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: int
    dividends: float
    stock_splits: float
    capital_gains: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., dividends: _Optional[float] = ..., stock_splits: _Optional[float] = ..., capital_gains: _Optional[float] = ...) -> None: ...

class GetDividendsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    period: str
    def __init__(self, ticker: _Optional[str] = ..., period: _Optional[str] = ...) -> None: ...

class GetDividendsResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[DividendRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[DividendRow, _Mapping]]] = ...) -> None: ...

class DividendRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    amount: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., amount: _Optional[float] = ...) -> None: ...

class GetSplitsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    period: str
    def __init__(self, ticker: _Optional[str] = ..., period: _Optional[str] = ...) -> None: ...

class GetSplitsResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[SplitRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[SplitRow, _Mapping]]] = ...) -> None: ...

class SplitRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    RATIO_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    ratio: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ratio: _Optional[float] = ...) -> None: ...

class GetActionsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    period: str
    def __init__(self, ticker: _Optional[str] = ..., period: _Optional[str] = ...) -> None: ...

class GetActionsResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[ActionRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[ActionRow, _Mapping]]] = ...) -> None: ...

class ActionRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    DIVIDENDS_FIELD_NUMBER: _ClassVar[int]
    STOCK_SPLITS_FIELD_NUMBER: _ClassVar[int]
    CAPITAL_GAINS_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    dividends: float
    stock_splits: float
    capital_gains: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., dividends: _Optional[float] = ..., stock_splits: _Optional[float] = ..., capital_gains: _Optional[float] = ...) -> None: ...

class GetFinancialsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    FREQ_FIELD_NUMBER: _ClassVar[int]
    AS_DICT_FIELD_NUMBER: _ClassVar[int]
    PRETTY_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    freq: str
    as_dict: bool
    pretty: bool
    def __init__(self, ticker: _Optional[str] = ..., freq: _Optional[str] = ..., as_dict: _Optional[bool] = ..., pretty: _Optional[bool] = ...) -> None: ...

class GetFinancialsResponse(_message.Message):
    __slots__ = ()
    STATEMENTS_FIELD_NUMBER: _ClassVar[int]
    statements: _containers.RepeatedCompositeFieldContainer[FinancialStatement]
    def __init__(self, statements: _Optional[_Iterable[_Union[FinancialStatement, _Mapping]]] = ...) -> None: ...

class FinancialStatement(_message.Message):
    __slots__ = ()
    class ValuesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    DATE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    values: _containers.ScalarMap[str, float]
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., values: _Optional[_Mapping[str, float]] = ...) -> None: ...

class GetBalanceSheetRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    FREQ_FIELD_NUMBER: _ClassVar[int]
    AS_DICT_FIELD_NUMBER: _ClassVar[int]
    PRETTY_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    freq: str
    as_dict: bool
    pretty: bool
    def __init__(self, ticker: _Optional[str] = ..., freq: _Optional[str] = ..., as_dict: _Optional[bool] = ..., pretty: _Optional[bool] = ...) -> None: ...

class GetBalanceSheetResponse(_message.Message):
    __slots__ = ()
    STATEMENTS_FIELD_NUMBER: _ClassVar[int]
    statements: _containers.RepeatedCompositeFieldContainer[BalanceSheetStatement]
    def __init__(self, statements: _Optional[_Iterable[_Union[BalanceSheetStatement, _Mapping]]] = ...) -> None: ...

class BalanceSheetStatement(_message.Message):
    __slots__ = ()
    class ValuesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    DATE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    values: _containers.ScalarMap[str, float]
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., values: _Optional[_Mapping[str, float]] = ...) -> None: ...

class GetCashFlowRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    FREQ_FIELD_NUMBER: _ClassVar[int]
    AS_DICT_FIELD_NUMBER: _ClassVar[int]
    PRETTY_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    freq: str
    as_dict: bool
    pretty: bool
    def __init__(self, ticker: _Optional[str] = ..., freq: _Optional[str] = ..., as_dict: _Optional[bool] = ..., pretty: _Optional[bool] = ...) -> None: ...

class GetCashFlowResponse(_message.Message):
    __slots__ = ()
    STATEMENTS_FIELD_NUMBER: _ClassVar[int]
    statements: _containers.RepeatedCompositeFieldContainer[CashFlowStatement]
    def __init__(self, statements: _Optional[_Iterable[_Union[CashFlowStatement, _Mapping]]] = ...) -> None: ...

class CashFlowStatement(_message.Message):
    __slots__ = ()
    class ValuesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    DATE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    values: _containers.ScalarMap[str, float]
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., values: _Optional[_Mapping[str, float]] = ...) -> None: ...

class GetEarningsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    FREQ_FIELD_NUMBER: _ClassVar[int]
    AS_DICT_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    freq: str
    as_dict: bool
    def __init__(self, ticker: _Optional[str] = ..., freq: _Optional[str] = ..., as_dict: _Optional[bool] = ...) -> None: ...

class GetEarningsResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[EarningsRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[EarningsRow, _Mapping]]] = ...) -> None: ...

class EarningsRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    REVENUE_FIELD_NUMBER: _ClassVar[int]
    EARNINGS_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    revenue: float
    earnings: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., revenue: _Optional[float] = ..., earnings: _Optional[float] = ...) -> None: ...

class GetRecommendationsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetRecommendationsResponse(_message.Message):
    __slots__ = ()
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[RecommendationRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[RecommendationRow, _Mapping]]] = ...) -> None: ...

class RecommendationRow(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    FIRM_FIELD_NUMBER: _ClassVar[int]
    TO_GRADE_FIELD_NUMBER: _ClassVar[int]
    FROM_GRADE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    firm: str
    to_grade: str
    from_grade: str
    action: str
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., firm: _Optional[str] = ..., to_grade: _Optional[str] = ..., from_grade: _Optional[str] = ..., action: _Optional[str] = ...) -> None: ...

class GetOptionsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetOptionsResponse(_message.Message):
    __slots__ = ()
    EXPIRATION_DATES_FIELD_NUMBER: _ClassVar[int]
    expiration_dates: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, expiration_dates: _Optional[_Iterable[str]] = ...) -> None: ...

class GetOptionChainRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    TZ_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    date: str
    tz: str
    def __init__(self, ticker: _Optional[str] = ..., date: _Optional[str] = ..., tz: _Optional[str] = ...) -> None: ...

class GetOptionChainResponse(_message.Message):
    __slots__ = ()
    CALLS_FIELD_NUMBER: _ClassVar[int]
    PUTS_FIELD_NUMBER: _ClassVar[int]
    calls: _containers.RepeatedCompositeFieldContainer[OptionContract]
    puts: _containers.RepeatedCompositeFieldContainer[OptionContract]
    def __init__(self, calls: _Optional[_Iterable[_Union[OptionContract, _Mapping]]] = ..., puts: _Optional[_Iterable[_Union[OptionContract, _Mapping]]] = ...) -> None: ...

class OptionContract(_message.Message):
    __slots__ = ()
    CONTRACT_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    CHANGE_FIELD_NUMBER: _ClassVar[int]
    PERCENT_CHANGE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    IMPLIED_VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    IN_THE_MONEY_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_SIZE_FIELD_NUMBER: _ClassVar[int]
    LAST_TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    contract_symbol: str
    strike: float
    currency: str
    last_price: float
    bid: float
    ask: float
    change: float
    percent_change: float
    volume: int
    open_interest: int
    implied_volatility: float
    in_the_money: bool
    contract_size: str
    last_trade_date: _timestamp_pb2.Timestamp
    def __init__(self, contract_symbol: _Optional[str] = ..., strike: _Optional[float] = ..., currency: _Optional[str] = ..., last_price: _Optional[float] = ..., bid: _Optional[float] = ..., ask: _Optional[float] = ..., change: _Optional[float] = ..., percent_change: _Optional[float] = ..., volume: _Optional[int] = ..., open_interest: _Optional[int] = ..., implied_volatility: _Optional[float] = ..., in_the_money: _Optional[bool] = ..., contract_size: _Optional[str] = ..., last_trade_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetCalendarRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetCalendarResponse(_message.Message):
    __slots__ = ()
    EARNINGS_FIELD_NUMBER: _ClassVar[int]
    EX_DIVIDEND_DATE_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    earnings: EarningsDate
    ex_dividend_date: DividendDate
    events: _containers.RepeatedCompositeFieldContainer[CalendarEvent]
    def __init__(self, earnings: _Optional[_Union[EarningsDate, _Mapping]] = ..., ex_dividend_date: _Optional[_Union[DividendDate, _Mapping]] = ..., events: _Optional[_Iterable[_Union[CalendarEvent, _Mapping]]] = ...) -> None: ...

class EarningsDate(_message.Message):
    __slots__ = ()
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DividendDate(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CalendarEvent(_message.Message):
    __slots__ = ()
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    date: _timestamp_pb2.Timestamp
    description: str
    def __init__(self, event_type: _Optional[str] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class GetNewsRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    count: int
    def __init__(self, ticker: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class GetNewsResponse(_message.Message):
    __slots__ = ()
    ARTICLES_FIELD_NUMBER: _ClassVar[int]
    articles: _containers.RepeatedCompositeFieldContainer[NewsArticle]
    def __init__(self, articles: _Optional[_Iterable[_Union[NewsArticle, _Mapping]]] = ...) -> None: ...

class NewsArticle(_message.Message):
    __slots__ = ()
    UUID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_PUBLISH_TIME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    THUMBNAIL_FIELD_NUMBER: _ClassVar[int]
    RELATED_TICKERS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    title: str
    publisher: str
    link: str
    provider_publish_time: _timestamp_pb2.Timestamp
    type: str
    thumbnail: str
    related_tickers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uuid: _Optional[str] = ..., title: _Optional[str] = ..., publisher: _Optional[str] = ..., link: _Optional[str] = ..., provider_publish_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[str] = ..., thumbnail: _Optional[str] = ..., related_tickers: _Optional[_Iterable[str]] = ...) -> None: ...

class GetMajorHoldersRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetMajorHoldersResponse(_message.Message):
    __slots__ = ()
    class HoldersEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    holders: _containers.ScalarMap[str, str]
    def __init__(self, holders: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetInstitutionalHoldersRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetInstitutionalHoldersResponse(_message.Message):
    __slots__ = ()
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    holders: _containers.RepeatedCompositeFieldContainer[InstitutionalHolder]
    def __init__(self, holders: _Optional[_Iterable[_Union[InstitutionalHolder, _Mapping]]] = ...) -> None: ...

class InstitutionalHolder(_message.Message):
    __slots__ = ()
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    DATE_REPORTED_FIELD_NUMBER: _ClassVar[int]
    PCT_OUT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    holder: str
    shares: int
    date_reported: _timestamp_pb2.Timestamp
    pct_out: float
    value: float
    def __init__(self, holder: _Optional[str] = ..., shares: _Optional[int] = ..., date_reported: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., pct_out: _Optional[float] = ..., value: _Optional[float] = ...) -> None: ...

class GetMutualFundHoldersRequest(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    def __init__(self, ticker: _Optional[str] = ...) -> None: ...

class GetMutualFundHoldersResponse(_message.Message):
    __slots__ = ()
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    holders: _containers.RepeatedCompositeFieldContainer[MutualFundHolder]
    def __init__(self, holders: _Optional[_Iterable[_Union[MutualFundHolder, _Mapping]]] = ...) -> None: ...

class MutualFundHolder(_message.Message):
    __slots__ = ()
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    DATE_REPORTED_FIELD_NUMBER: _ClassVar[int]
    PCT_OUT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    holder: str
    shares: int
    date_reported: _timestamp_pb2.Timestamp
    pct_out: float
    value: float
    def __init__(self, holder: _Optional[str] = ..., shares: _Optional[int] = ..., date_reported: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., pct_out: _Optional[float] = ..., value: _Optional[float] = ...) -> None: ...

class GetMultipleInfoRequest(_message.Message):
    __slots__ = ()
    TICKERS_FIELD_NUMBER: _ClassVar[int]
    tickers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tickers: _Optional[_Iterable[str]] = ...) -> None: ...

class GetMultipleInfoResponse(_message.Message):
    __slots__ = ()
    class InfoEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TickerInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TickerInfo, _Mapping]] = ...) -> None: ...
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _containers.MessageMap[str, TickerInfo]
    def __init__(self, info: _Optional[_Mapping[str, TickerInfo]] = ...) -> None: ...

class DownloadHistoryRequest(_message.Message):
    __slots__ = ()
    TICKERS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    AUTO_ADJUST_FIELD_NUMBER: _ClassVar[int]
    tickers: _containers.RepeatedScalarFieldContainer[str]
    period: str
    interval: str
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    auto_adjust: bool
    def __init__(self, tickers: _Optional[_Iterable[str]] = ..., period: _Optional[str] = ..., interval: _Optional[str] = ..., start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., auto_adjust: _Optional[bool] = ...) -> None: ...

class DownloadHistoryResponse(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    rows: _containers.RepeatedCompositeFieldContainer[HistoryRow]
    def __init__(self, ticker: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[HistoryRow, _Mapping]]] = ...) -> None: ...
