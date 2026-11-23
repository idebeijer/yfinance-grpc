"""TickerService: wraps yfinance.Ticker, yfinance.Tickers and yfinance.download."""

import logging
from collections.abc import Iterator

import pandas as pd
import yfinance as yf
from yfinance_grpc.v1alpha1 import ticker_pb2, ticker_pb2_grpc

from yfinance_grpc_server.convert import is_missing, safe_float, safe_int, safe_str, to_timestamp
from yfinance_grpc_server.errors import invalid_argument, not_found, require, rpc, unimplemented

logger = logging.getLogger(__name__)

_STREAM_BATCH_SIZE = 500

# Trailing-metadata key listing requested symbols that returned no data.
MISSING_TICKERS_KEY = "missing-tickers"


def _ticker(request) -> yf.Ticker:
    """Build the yf.Ticker a single-ticker request names; INVALID_ARGUMENT if empty."""
    return yf.Ticker(require(request.ticker, "ticker"))


def create_ticker_info(info: dict, symbol: str) -> ticker_pb2.TickerInfo:
    """Create a TickerInfo message from info dict"""
    return ticker_pb2.TickerInfo(
        symbol=safe_str(info.get("symbol", symbol)),
        short_name=safe_str(info.get("shortName")),
        long_name=safe_str(info.get("longName")),
        industry=safe_str(info.get("industry")),
        sector=safe_str(info.get("sector")),
        country=safe_str(info.get("country")),
        city=safe_str(info.get("city")),
        state=safe_str(info.get("state")),
        zip=safe_str(info.get("zip")),
        website=safe_str(info.get("website")),
        long_business_summary=safe_str(info.get("longBusinessSummary")),
        previous_close=safe_float(info.get("previousClose")),
        open=safe_float(info.get("open")),
        day_low=safe_float(info.get("dayLow")),
        day_high=safe_float(info.get("dayHigh")),
        regular_market_previous_close=safe_float(info.get("regularMarketPreviousClose")),
        regular_market_open=safe_float(info.get("regularMarketOpen")),
        regular_market_day_low=safe_float(info.get("regularMarketDayLow")),
        regular_market_day_high=safe_float(info.get("regularMarketDayHigh")),
        current_price=safe_float(info.get("currentPrice")),
        volume=safe_int(info.get("volume")),
        regular_market_volume=safe_int(info.get("regularMarketVolume")),
        average_volume=safe_int(info.get("averageVolume")),
        average_volume_10days=safe_int(info.get("averageVolume10days")),
        shares_outstanding=safe_int(info.get("sharesOutstanding")),
        float_shares=safe_int(info.get("floatShares")),
        market_cap=safe_int(info.get("marketCap")),
        enterprise_value=safe_float(info.get("enterpriseValue")),
        trailing_pe=safe_float(info.get("trailingPE")),
        forward_pe=safe_float(info.get("forwardPE")),
        price_to_book=safe_float(info.get("priceToBook")),
        price_to_sales_trailing_12months=safe_float(info.get("priceToSalesTrailing12Months")),
        enterprise_to_revenue=safe_float(info.get("enterpriseToRevenue")),
        enterprise_to_ebitda=safe_float(info.get("enterpriseToEbitda")),
        dividend_rate=safe_float(info.get("dividendRate")),
        dividend_yield=safe_float(info.get("dividendYield")),
        ex_dividend_date=safe_int(info.get("exDividendDate", 0)),
        payout_ratio=safe_float(info.get("payoutRatio")),
        five_year_avg_dividend_yield=safe_float(info.get("fiveYearAvgDividendYield")),
        beta=safe_float(info.get("beta")),
        trailing_eps=safe_float(info.get("trailingEps")),
        forward_eps=safe_float(info.get("forwardEps")),
        book_value=safe_float(info.get("bookValue")),
        profit_margins=safe_float(info.get("profitMargins")),
        revenue_per_share=safe_float(info.get("revenuePerShare")),
        return_on_assets=safe_float(info.get("returnOnAssets")),
        return_on_equity=safe_float(info.get("returnOnEquity")),
        revenue_growth=safe_float(info.get("revenueGrowth")),
        earnings_growth=safe_float(info.get("earningsGrowth")),
        operating_margins=safe_float(info.get("operatingMargins")),
        ebitda_margins=safe_float(info.get("ebitdaMargins")),
        fifty_two_week_low=safe_float(info.get("fiftyTwoWeekLow")),
        fifty_two_week_high=safe_float(info.get("fiftyTwoWeekHigh")),
        fifty_day_average=safe_float(info.get("fiftyDayAverage")),
        two_hundred_day_average=safe_float(info.get("twoHundredDayAverage")),
        target_high_price=safe_float(info.get("targetHighPrice")),
        target_low_price=safe_float(info.get("targetLowPrice")),
        target_mean_price=safe_float(info.get("targetMeanPrice")),
        target_median_price=safe_float(info.get("targetMedianPrice")),
        number_of_analyst_opinions=safe_int(info.get("numberOfAnalystOpinions")),
        currency=safe_str(info.get("currency")),
        exchange=safe_str(info.get("exchange")),
        quote_type=safe_str(info.get("quoteType")),
        financial_currency=safe_str(info.get("financialCurrency")),
        price_hint=safe_int(info.get("priceHint", 2)),
    )


def _statements(df: pd.DataFrame | None, message_cls):
    """Turn a yfinance statement frame (line items x period columns) into messages."""
    if df is None or df.empty:
        return []
    return [
        message_cls(
            date=to_timestamp(col),
            values={str(item): safe_float(v) for item, v in df[col].items() if not is_missing(v)},
        )
        for col in df.columns
    ]


def _option_contracts(df: pd.DataFrame) -> list[ticker_pb2.OptionContract]:
    return [
        ticker_pb2.OptionContract(
            contract_symbol=safe_str(row.get("contractSymbol")),
            strike=safe_float(row.get("strike")),
            currency=safe_str(row.get("currency")),
            last_price=safe_float(row.get("lastPrice")),
            bid=safe_float(row.get("bid")),
            ask=safe_float(row.get("ask")),
            change=safe_float(row.get("change")),
            percent_change=safe_float(row.get("percentChange")),
            volume=safe_int(row.get("volume")),
            open_interest=safe_int(row.get("openInterest")),
            implied_volatility=safe_float(row.get("impliedVolatility")),
            in_the_money=bool(row.get("inTheMoney", False)),
            contract_size=safe_str(row.get("contractSize", "REGULAR")),
            last_trade_date=to_timestamp(row.get("lastTradeDate")),
        )
        for _, row in df.iterrows()
    ]


def _holders(df: pd.DataFrame | None, message_cls):
    """Institutional / mutual-fund holder rows.

    yfinance renamed the '% Out' column to 'pctHeld' (a fraction, 0.05 = 5%);
    read the new name and fall back to the old one.
    """
    if df is None or df.empty:
        return []
    return [
        message_cls(
            holder=safe_str(row.get("Holder")),
            shares=safe_int(row.get("Shares")),
            date_reported=to_timestamp(row.get("Date Reported")),
            pct_out=safe_float(row.get("pctHeld", row.get("% Out"))),
            value=safe_float(row.get("Value")),
        )
        for _, row in df.iterrows()
    ]


def _history_rows(df: pd.DataFrame) -> Iterator[ticker_pb2.HistoryRow]:
    """OHLCV rows for one ticker's frame."""
    for idx, row in df.iterrows():
        yield ticker_pb2.HistoryRow(
            date=to_timestamp(idx),
            open=safe_float(row.get("Open")),
            high=safe_float(row.get("High")),
            low=safe_float(row.get("Low")),
            close=safe_float(row.get("Close")),
            volume=safe_int(row.get("Volume")),
        )


def _batched(ticker: str, rows: Iterator[ticker_pb2.HistoryRow]):
    """Group rows into DownloadHistoryResponse messages of _STREAM_BATCH_SIZE."""
    batch: list[ticker_pb2.HistoryRow] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= _STREAM_BATCH_SIZE:
            yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)
            batch = []
    if batch:
        yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)


def _set_timestamp(message, field: str, value) -> None:
    """Set a Timestamp field when ``value`` converts; leave it unset otherwise."""
    if (ts := to_timestamp(value)) is not None:
        getattr(message, field).CopyFrom(ts)


def _symbols(tickers) -> list[str]:
    """Validate a repeated ticker field: non-empty, one symbol per entry."""
    symbols = list(tickers)
    if not symbols:
        raise invalid_argument("tickers must not be empty")
    for symbol in symbols:
        if not symbol or symbol != symbol.strip() or " " in symbol:
            raise invalid_argument(
                f"invalid ticker {symbol!r}: pass one symbol per list entry, e.g. ['AAPL', 'MSFT']"
            )
    return symbols


def _frame_for(data: pd.DataFrame, symbol: str, single: bool) -> pd.DataFrame | None:
    """Pick one ticker's OHLCV rows out of a yf.download result; None if it has none."""
    if isinstance(data.columns, pd.MultiIndex):
        if symbol not in data.columns.get_level_values(0):
            return None
        frame: object = data[symbol]
    else:
        frame = data if single else None
    if not isinstance(frame, pd.DataFrame):
        return None
    frame = frame.dropna(how="all")
    return None if frame.empty else frame


def _report_missing(context, missing: list[str]) -> None:
    if missing:
        context.set_trailing_metadata(((MISSING_TICKERS_KEY, ",".join(missing)),))


class TickerServiceServicer(ticker_pb2_grpc.TickerServiceServicer):
    """Implementation of the TickerService gRPC service"""

    @rpc
    def GetInfo(self, request, context):
        """Get general information about a ticker"""
        ticker = _ticker(request)
        info = ticker.info

        response = ticker_pb2.GetInfoResponse(info=create_ticker_info(info, request.ticker))

        return response

    @rpc
    def GetHistory(self, request, context):
        """Get historical market data for a ticker"""
        ticker = _ticker(request)

        # Build kwargs for history call
        kwargs = {}

        # Period or date range
        if request.HasField("period"):
            kwargs["period"] = request.period
        else:
            if request.HasField("start"):
                kwargs["start"] = request.start.ToDatetime()
            if request.HasField("end"):
                kwargs["end"] = request.end.ToDatetime()

        # Interval
        if request.interval:
            kwargs["interval"] = request.interval
        else:
            kwargs["interval"] = "1d"

        # Options - use HasField for optional booleans to detect if they were set
        # This allows us to use yfinance defaults when not specified
        if request.HasField("prepost"):
            kwargs["prepost"] = request.prepost
        # default is False, which matches yfinance

        if request.HasField("actions"):
            kwargs["actions"] = request.actions
        else:
            kwargs["actions"] = True  # yfinance default

        if request.HasField("auto_adjust"):
            kwargs["auto_adjust"] = request.auto_adjust
        else:
            kwargs["auto_adjust"] = True  # yfinance default

        if request.HasField("back_adjust"):
            kwargs["back_adjust"] = request.back_adjust
        # default is False, which matches yfinance

        if request.HasField("repair"):
            kwargs["repair"] = request.repair
        # default is False, which matches yfinance

        if request.HasField("keepna"):
            kwargs["keepna"] = request.keepna
        # default is False, which matches yfinance

        if request.HasField("rounding"):
            kwargs["rounding"] = request.rounding
        # default is False, which matches yfinance

        # Get history
        hist = ticker.history(**kwargs)

        # Convert to response
        rows = []
        for idx, row in hist.iterrows():
            history_row = ticker_pb2.HistoryRow(
                date=to_timestamp(idx),
                open=safe_float(row.get("Open", 0)),
                high=safe_float(row.get("High", 0)),
                low=safe_float(row.get("Low", 0)),
                close=safe_float(row.get("Close", 0)),
                volume=safe_int(row.get("Volume", 0)),
            )

            # Optional fields
            if "Dividends" in row and row["Dividends"] > 0:
                history_row.dividends = safe_float(row["Dividends"])
            if "Stock Splits" in row and row["Stock Splits"] > 0:
                history_row.stock_splits = safe_float(row["Stock Splits"])
            if "Capital Gains" in row and row["Capital Gains"] > 0:
                history_row.capital_gains = safe_float(row["Capital Gains"])

            rows.append(history_row)

        return ticker_pb2.GetHistoryResponse(rows=rows)

    @rpc
    def GetDividends(self, request, context):
        """Get dividend history for a ticker"""
        ticker = _ticker(request)

        period = request.period if request.HasField("period") else "max"
        dividends = ticker.get_dividends(period=period)

        rows = []
        for idx, value in dividends.items():
            rows.append(ticker_pb2.DividendRow(date=to_timestamp(idx), amount=safe_float(value)))

        return ticker_pb2.GetDividendsResponse(rows=rows)

    @rpc
    def GetSplits(self, request, context):
        """Get stock split history for a ticker"""
        ticker = _ticker(request)

        period = request.period if request.HasField("period") else "max"
        splits = ticker.get_splits(period=period)

        rows = []
        for idx, value in splits.items():
            rows.append(ticker_pb2.SplitRow(date=to_timestamp(idx), ratio=safe_float(value)))

        return ticker_pb2.GetSplitsResponse(rows=rows)

    @rpc
    def GetActions(self, request, context):
        """Get all corporate actions (dividends, splits, capital gains)"""
        ticker = _ticker(request)

        period = request.period if request.HasField("period") else "max"
        actions = ticker.get_actions(period=period)

        rows = []
        for idx, row in actions.iterrows():
            action_row = ticker_pb2.ActionRow(date=to_timestamp(idx))

            if "Dividends" in row and not pd.isna(row["Dividends"]) and row["Dividends"] > 0:
                action_row.dividends = safe_float(row["Dividends"])
            if "Stock Splits" in row and not pd.isna(row["Stock Splits"]) and row["Stock Splits"] > 0:
                action_row.stock_splits = safe_float(row["Stock Splits"])
            if "Capital Gains" in row and not pd.isna(row["Capital Gains"]) and row["Capital Gains"] > 0:
                action_row.capital_gains = safe_float(row["Capital Gains"])

            rows.append(action_row)

        return ticker_pb2.GetActionsResponse(rows=rows)

    @rpc
    def GetFinancials(self, request, context):
        """Get the income statement."""
        df = _ticker(request).get_income_stmt(freq=request.freq or "yearly", pretty=request.pretty)
        return ticker_pb2.GetFinancialsResponse(statements=_statements(df, ticker_pb2.FinancialStatement))

    @rpc
    def GetBalanceSheet(self, request, context):
        """Get the balance sheet."""
        df = _ticker(request).get_balance_sheet(freq=request.freq or "yearly", pretty=request.pretty)
        return ticker_pb2.GetBalanceSheetResponse(
            statements=_statements(df, ticker_pb2.BalanceSheetStatement)
        )

    @rpc
    def GetCashFlow(self, request, context):
        """Get the cash flow statement."""
        df = _ticker(request).get_cash_flow(freq=request.freq or "yearly", pretty=request.pretty)
        return ticker_pb2.GetCashFlowResponse(statements=_statements(df, ticker_pb2.CashFlowStatement))

    @rpc
    def GetEarnings(self, request, context):
        """Deprecated: yfinance no longer provides this data."""
        raise unimplemented(
            "GetEarnings is deprecated: Yahoo Finance no longer serves this data. "
            "Use GetFinancials ('Net Income', 'Total Revenue') or GetEarningsHistory instead."
        )

    @rpc
    def GetRecommendations(self, request, context):
        """Get analyst recommendations"""
        ticker = _ticker(request)

        # Use upgrades_downgrades which has the detailed recommendation data
        recommendations = ticker.upgrades_downgrades

        rows = []
        if recommendations is not None and not recommendations.empty:
            # Sort by date descending (most recent first)
            recommendations = recommendations.sort_index(ascending=False)

            for idx, row in recommendations.iterrows():
                rows.append(
                    ticker_pb2.RecommendationRow(
                        date=to_timestamp(idx),
                        firm=safe_str(row.get("Firm", "")),
                        to_grade=safe_str(row.get("ToGrade", "")),
                        from_grade=safe_str(row.get("FromGrade", "")),
                        action=safe_str(row.get("Action", "")),
                    )
                )

        return ticker_pb2.GetRecommendationsResponse(rows=rows)

    @rpc
    def GetOptions(self, request, context):
        """Get available option expiration dates"""
        ticker = _ticker(request)

        options = ticker.options

        return ticker_pb2.GetOptionsResponse(expiration_dates=list(options))

    @rpc
    def GetOptionChain(self, request, context):
        """Get the option chain for one expiration date."""
        chain = _ticker(request).option_chain(
            date=request.date if request.HasField("date") else None,
            tz=request.tz if request.HasField("tz") else None,
        )
        return ticker_pb2.GetOptionChainResponse(
            calls=_option_contracts(chain.calls), puts=_option_contracts(chain.puts)
        )

    @rpc
    def GetCalendar(self, request, context):
        """Get upcoming earnings and ex-dividend dates."""
        calendar = _ticker(request).get_calendar()
        response = ticker_pb2.GetCalendarResponse()
        if not isinstance(calendar, dict):
            return response

        earnings_dates = calendar.get("Earnings Date")
        if isinstance(earnings_dates, list) and earnings_dates:
            earnings = ticker_pb2.EarningsDate()
            _set_timestamp(earnings, "start", earnings_dates[0])
            if len(earnings_dates) > 1:
                _set_timestamp(earnings, "end", earnings_dates[1])
            response.earnings.CopyFrom(earnings)

        if ex_div := calendar.get("Ex-Dividend Date"):
            div_date = ticker_pb2.DividendDate()
            _set_timestamp(div_date, "date", ex_div)
            response.ex_dividend_date.CopyFrom(div_date)

        return response

    @rpc
    def GetNews(self, request, context):
        """Get recent news articles."""
        count = request.count if request.count > 0 else 10
        articles = []
        for wrapper in _ticker(request).news[:count]:
            article = wrapper.get("content", wrapper)
            news_article = ticker_pb2.NewsArticle(
                uuid=safe_str(article.get("id")),
                title=safe_str(article.get("title")),
                publisher=safe_str((article.get("provider") or {}).get("displayName")),
                link=safe_str((article.get("canonicalUrl") or {}).get("url")),
                type=safe_str(article.get("contentType")),
            )
            _set_timestamp(news_article, "provider_publish_time", article.get("pubDate"))

            thumbnail = article.get("thumbnail")
            if isinstance(thumbnail, dict):
                if resolutions := thumbnail.get("resolutions"):
                    news_article.thumbnail = safe_str(resolutions[0].get("url"))
                elif "originalUrl" in thumbnail:
                    news_article.thumbnail = safe_str(thumbnail["originalUrl"])

            articles.append(news_article)
        return ticker_pb2.GetNewsResponse(articles=articles)

    @rpc
    def GetMajorHolders(self, request, context):
        """Get the major-holders breakdown."""
        major_holders = _ticker(request).get_major_holders(as_dict=True)
        holders = {}
        if isinstance(major_holders, dict):
            holders = {str(k): safe_str(v) for k, v in major_holders.items()}
        return ticker_pb2.GetMajorHoldersResponse(holders=holders)

    @rpc
    def GetInstitutionalHolders(self, request, context):
        """Get the top institutional holders."""
        df = _ticker(request).get_institutional_holders(as_dict=False)
        return ticker_pb2.GetInstitutionalHoldersResponse(
            holders=_holders(df, ticker_pb2.InstitutionalHolder)
        )

    @rpc
    def GetMutualFundHolders(self, request, context):
        """Get the top mutual-fund holders."""
        df = _ticker(request).get_mutualfund_holders(as_dict=False)
        return ticker_pb2.GetMutualFundHoldersResponse(holders=_holders(df, ticker_pb2.MutualFundHolder))

    @rpc
    def GetMultipleInfo(self, request, context):
        """Get info for several tickers. Symbols that fail are omitted from the
        map and listed in the 'missing-tickers' trailing metadata."""
        symbols = _symbols(request.tickers)
        info_map = {}
        missing = []
        for symbol, ticker in yf.Tickers(" ".join(symbols)).tickers.items():
            try:
                info_map[symbol] = create_ticker_info(ticker.info, symbol)
            except Exception:
                logger.warning("GetMultipleInfo: no info for %s", symbol, exc_info=True)
                missing.append(symbol)
        _report_missing(context, missing)
        return ticker_pb2.GetMultipleInfoResponse(info=info_map)

    @rpc
    def DownloadHistory(self, request, context):
        """Stream OHLCV history for several tickers, one ticker at a time.

        NOT_FOUND when no requested ticker has data; otherwise tickers without
        data are listed in the 'missing-tickers' trailing metadata.
        """
        symbols = _symbols(request.tickers)
        kwargs = {
            "group_by": "ticker",
            "auto_adjust": request.auto_adjust if request.HasField("auto_adjust") else True,
            "threads": True,
            "progress": False,
        }
        if request.HasField("period"):
            kwargs["period"] = request.period
        else:
            if request.HasField("start"):
                kwargs["start"] = request.start.ToDatetime()
            if request.HasField("end"):
                kwargs["end"] = request.end.ToDatetime()
        if request.HasField("interval"):
            kwargs["interval"] = request.interval

        data = yf.download(" ".join(symbols), **kwargs)

        frames = {}
        missing = []
        for symbol in symbols:
            frame = _frame_for(data, symbol, single=len(symbols) == 1)
            if frame is None:
                missing.append(symbol)
            else:
                frames[symbol] = frame
        if not frames:
            raise not_found(f"No historical data found for {', '.join(symbols)}")
        _report_missing(context, missing)

        for symbol, frame in frames.items():
            yield from _batched(symbol, _history_rows(frame))

    @rpc
    def GetCapitalGains(self, request, context):
        """Get capital gains distributions for a ticker"""
        ticker = _ticker(request)
        period = request.period if request.HasField("period") else "max"
        gains = ticker.get_capital_gains(period=period)
        rows = []
        for idx, value in gains.items():
            rows.append(ticker_pb2.CapitalGainsRow(date=to_timestamp(idx), amount=safe_float(value)))
        return ticker_pb2.GetCapitalGainsResponse(rows=rows)

    @rpc
    def GetSharesHistory(self, request, context):
        """Get full history of shares outstanding"""
        ticker = _ticker(request)
        kwargs = {}
        if request.HasField("start"):
            kwargs["start"] = request.start.ToDatetime()
        if request.HasField("end"):
            kwargs["end"] = request.end.ToDatetime()
        shares = ticker.get_shares_full(**kwargs)
        rows = []
        if shares is not None:
            for idx, value in shares.items():
                rows.append(ticker_pb2.SharesHistoryRow(date=to_timestamp(idx), shares=safe_int(value)))
        return ticker_pb2.GetSharesHistoryResponse(rows=rows)

    @rpc
    def GetIsin(self, request, context):
        """Get the ISIN code for a ticker"""
        ticker = _ticker(request)
        isin = ticker.get_isin() or ""
        return ticker_pb2.GetIsinResponse(isin=isin)

    @rpc
    def GetFastInfo(self, request, context):
        """Get a lightweight snapshot of key price/market data"""
        ticker = _ticker(request)
        fi = ticker.get_fast_info()
        info = ticker_pb2.FastInfo(
            currency=safe_str(getattr(fi, "currency", None)),
            exchange=safe_str(getattr(fi, "exchange", None)),
            exchange_data_delayed_by=safe_int(getattr(fi, "exchange_data_delayed_by", 0)),
            exchange_timezone_name=safe_str(getattr(fi, "exchange_timezone_name", None)),
            last_price=safe_float(getattr(fi, "last_price", 0)),
            last_volume=safe_int(getattr(fi, "last_volume", 0)),
            market_cap=safe_int(getattr(fi, "market_cap", 0)),
            open=safe_float(getattr(fi, "open", 0)),
            previous_close=safe_float(getattr(fi, "previous_close", 0)),
            quote_type=safe_str(getattr(fi, "quote_type", None)),
            regular_market_day_high=safe_float(getattr(fi, "regular_market_day_high", 0)),
            regular_market_day_low=safe_float(getattr(fi, "regular_market_day_low", 0)),
            regular_market_previous_close=safe_float(getattr(fi, "regular_market_previous_close", 0)),
            regular_market_price=safe_float(getattr(fi, "regular_market_price", 0)),
            shares=safe_int(getattr(fi, "shares", 0)),
            three_month_average_volume=safe_float(getattr(fi, "three_month_average_volume", 0)),
            timezone=safe_str(getattr(fi, "timezone", None)),
            fifty_day_average=safe_float(getattr(fi, "fifty_day_average", 0)),
            two_hundred_day_average=safe_float(getattr(fi, "two_hundred_day_average", 0)),
            year_change=safe_float(getattr(fi, "year_change", 0)),
            year_high=safe_float(getattr(fi, "year_high", 0)),
            year_low=safe_float(getattr(fi, "year_low", 0)),
        )
        return ticker_pb2.GetFastInfoResponse(info=info)

    @rpc
    def GetSustainability(self, request, context):
        """Get ESG scores and controversy flags"""
        ticker = _ticker(request)
        data = ticker.get_sustainability(as_dict=True)
        if not data:
            return ticker_pb2.GetSustainabilityResponse()
        return ticker_pb2.GetSustainabilityResponse(
            total_esg=safe_float(data.get("totalEsg", 0)),
            esg_performance=safe_str(data.get("esgPerformance")),
            environment_score=safe_float(data.get("environmentScore", 0)),
            social_score=safe_float(data.get("socialScore", 0)),
            governance_score=safe_float(data.get("governanceScore", 0)),
            percentile=safe_float(data.get("percentile", 0)),
            peer_group=safe_str(data.get("peerGroup")),
            adult=bool(data.get("adult", False)),
            alcoholic=bool(data.get("alcoholic", False)),
            animal_testing=bool(data.get("animalTesting", False)),
            catholic=bool(data.get("catholic", False)),
            controversial_weapons=bool(data.get("controversialWeapons", False)),
            small_arms=bool(data.get("smallArms", False)),
            fur_leather=bool(data.get("furLeather", False)),
            gambling=bool(data.get("gambling", False)),
            gmo=bool(data.get("gmo", False)),
            military_contract=bool(data.get("militaryContract", False)),
            nuclear=bool(data.get("nuclear", False)),
            pesticides=bool(data.get("pesticides", False)),
            palm_oil=bool(data.get("palmOil", False)),
            coal=bool(data.get("coal", False)),
            tobacco=bool(data.get("tobacco", False)),
        )

    @rpc
    def GetInsiderPurchases(self, request, context):
        """Get summary table of insider buying/selling activity"""
        ticker = _ticker(request)
        data = ticker.get_insider_purchases(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for label, row in data.iterrows():
                rows.append(
                    ticker_pb2.InsiderPurchaseSummaryRow(
                        label=safe_str(label),
                        values={safe_str(col): safe_str(row[col]) for col in data.columns},
                    )
                )
        return ticker_pb2.GetInsiderPurchasesResponse(rows=rows)

    @rpc
    def GetInsiderTransactions(self, request, context):
        """Get individual insider transaction records"""
        ticker = _ticker(request)
        data = ticker.get_insider_transactions(as_dict=False)
        transactions = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                transactions.append(
                    ticker_pb2.InsiderTransaction(
                        start_date=to_timestamp(row.get("Start Date", idx)),
                        insider=safe_str(row.get("Insider", "")),
                        position=safe_str(row.get("Position", "")),
                        transaction=safe_str(row.get("Transaction", "")),
                        shares=safe_int(row.get("Shares", 0)),
                        value=safe_float(row.get("Value", 0)),
                        text=safe_str(row.get("Text", "")),
                        url=safe_str(row.get("URL", "")),
                    )
                )
        return ticker_pb2.GetInsiderTransactionsResponse(transactions=transactions)

    @rpc
    def GetInsiderRosterHolders(self, request, context):
        """Get the roster of insider holders"""
        ticker = _ticker(request)
        data = ticker.get_insider_roster_holders(as_dict=False)
        holders = []
        if data is not None and not data.empty:
            for _, row in data.iterrows():
                holders.append(
                    ticker_pb2.InsiderRosterHolder(
                        name=safe_str(row.get("Name", "")),
                        position=safe_str(row.get("Position", "")),
                        url=safe_str(row.get("URL", "")),
                        most_recent_transaction=to_timestamp(row.get("Most Recent Transaction")),
                        latest_transaction_shares=safe_int(row.get("Latest Transaction Shares", 0)),
                    )
                )
        return ticker_pb2.GetInsiderRosterHoldersResponse(holders=holders)

    @rpc
    def GetAnalystPriceTargets(self, request, context):
        """Get consensus analyst price targets"""
        ticker = _ticker(request)
        targets = ticker.get_analyst_price_targets()
        return ticker_pb2.GetAnalystPriceTargetsResponse(
            current=safe_float(targets.get("current", 0)),
            low=safe_float(targets.get("low", 0)),
            high=safe_float(targets.get("high", 0)),
            mean=safe_float(targets.get("mean", 0)),
            median=safe_float(targets.get("median", 0)),
        )

    @rpc
    def GetRecommendationsSummary(self, request, context):
        """Get period-based aggregated analyst recommendation counts"""
        ticker = _ticker(request)
        data = ticker.get_recommendations(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.RecommendationSummaryRow(
                        period=safe_str(idx),
                        strong_buy=safe_int(row.get("strongBuy", 0)),
                        buy=safe_int(row.get("buy", 0)),
                        hold=safe_int(row.get("hold", 0)),
                        sell=safe_int(row.get("sell", 0)),
                        strong_sell=safe_int(row.get("strongSell", 0)),
                    )
                )
        return ticker_pb2.GetRecommendationsSummaryResponse(rows=rows)

    @rpc
    def GetEarningsEstimate(self, request, context):
        """Get forward EPS estimates by period"""
        ticker = _ticker(request)
        data = ticker.get_earnings_estimate(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.EarningsEstimateRow(
                        period=safe_str(idx),
                        number_of_analysts=safe_int(row.get("numberOfAnalysts", 0)),
                        avg=safe_float(row.get("avg", 0)),
                        low=safe_float(row.get("low", 0)),
                        high=safe_float(row.get("high", 0)),
                        year_ago_eps=safe_float(row.get("yearAgoEps", 0)),
                        growth=safe_float(row.get("growth", 0)),
                    )
                )
        return ticker_pb2.GetEarningsEstimateResponse(rows=rows)

    @rpc
    def GetRevenueEstimate(self, request, context):
        """Get forward revenue estimates by period"""
        ticker = _ticker(request)
        data = ticker.get_revenue_estimate(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.RevenueEstimateRow(
                        period=safe_str(idx),
                        number_of_analysts=safe_int(row.get("numberOfAnalysts", 0)),
                        avg=safe_float(row.get("avg", 0)),
                        low=safe_float(row.get("low", 0)),
                        high=safe_float(row.get("high", 0)),
                        year_ago_revenue=safe_float(row.get("yearAgoRevenue", 0)),
                        growth=safe_float(row.get("growth", 0)),
                    )
                )
        return ticker_pb2.GetRevenueEstimateResponse(rows=rows)

    @rpc
    def GetEarningsHistory(self, request, context):
        """Get historical EPS actuals vs estimates"""
        ticker = _ticker(request)
        data = ticker.get_earnings_history(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.EarningsHistoryRow(
                        date=to_timestamp(idx),
                        eps_estimate=safe_float(row.get("epsEstimate", 0)),
                        eps_actual=safe_float(row.get("epsActual", 0)),
                        eps_difference=safe_float(row.get("epsDifference", 0)),
                        surprise_percent=safe_float(row.get("surprisePercent", 0)),
                    )
                )
        return ticker_pb2.GetEarningsHistoryResponse(rows=rows)

    @rpc
    def GetEpsTrend(self, request, context):
        """Get EPS estimate trend across recent revision windows"""
        ticker = _ticker(request)
        data = ticker.get_eps_trend(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.EpsTrendRow(
                        period=safe_str(idx),
                        current=safe_float(row.get("current", 0)),
                        seven_days_ago=safe_float(row.get("7daysAgo", 0)),
                        thirty_days_ago=safe_float(row.get("30daysAgo", 0)),
                        sixty_days_ago=safe_float(row.get("60daysAgo", 0)),
                        ninety_days_ago=safe_float(row.get("90daysAgo", 0)),
                    )
                )
        return ticker_pb2.GetEpsTrendResponse(rows=rows)

    @rpc
    def GetEpsRevisions(self, request, context):
        """Get counts of upward/downward EPS revisions"""
        ticker = _ticker(request)
        data = ticker.get_eps_revisions(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.EpsRevisionsRow(
                        period=safe_str(idx),
                        up_last_7days=safe_int(row.get("upLast7days", 0)),
                        up_last_30days=safe_int(row.get("upLast30days", 0)),
                        down_last_7days=safe_int(row.get("downLast7days", 0)),
                        down_last_30days=safe_int(row.get("downLast30days", 0)),
                    )
                )
        return ticker_pb2.GetEpsRevisionsResponse(rows=rows)

    @rpc
    def GetGrowthEstimates(self, request, context):
        """Get growth estimates for stock, industry, sector and index"""
        ticker = _ticker(request)
        data = ticker.get_growth_estimates(as_dict=False)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                rows.append(
                    ticker_pb2.GrowthEstimatesRow(
                        period=safe_str(idx),
                        stock=safe_float(row.get("stock", 0)),
                        industry=safe_float(row.get("industry", 0)),
                        sector=safe_float(row.get("sector", 0)),
                        index=safe_float(row.get("index", 0)),
                    )
                )
        return ticker_pb2.GetGrowthEstimatesResponse(rows=rows)

    @rpc
    def GetEarningsDates(self, request, context):
        """Get upcoming and past earnings dates with EPS data"""
        ticker = _ticker(request)
        limit = request.limit if request.HasField("limit") else 12
        data = ticker.get_earnings_dates(limit=limit)
        rows = []
        if data is not None and not data.empty:
            for idx, row in data.iterrows():
                earnings_row = ticker_pb2.EarningsDateRow(
                    date=to_timestamp(idx),
                )
                eps_est = row.get("EPS Estimate")
                if eps_est is not None and not pd.isna(eps_est):
                    earnings_row.eps_estimate = safe_float(eps_est)
                reported = row.get("Reported EPS")
                if reported is not None and not pd.isna(reported):
                    earnings_row.reported_eps = safe_float(reported)
                surprise = row.get("Surprise(%)")
                if surprise is not None and not pd.isna(surprise):
                    earnings_row.surprise_pct = safe_float(surprise)
                rows.append(earnings_row)
        return ticker_pb2.GetEarningsDatesResponse(rows=rows)

    @rpc
    def GetHistoryMetadata(self, request, context):
        """Get exchange and instrument metadata for a ticker"""
        ticker = _ticker(request)
        meta = ticker.get_history_metadata()
        return ticker_pb2.GetHistoryMetadataResponse(
            currency=safe_str(meta.get("currency")),
            symbol=safe_str(meta.get("symbol")),
            exchange_name=safe_str(meta.get("exchangeName")),
            full_exchange_name=safe_str(meta.get("fullExchangeName")),
            instrument_type=safe_str(meta.get("instrumentType")),
            first_trade_date=safe_int(meta.get("firstTradeDate", 0)),
            regular_market_time=safe_int(meta.get("regularMarketTime", 0)),
            has_pre_post_market_data=bool(meta.get("hasPrePostMarketData", False)),
            gmt_offset=safe_int(meta.get("gmtoffset", 0)),
            timezone=safe_str(meta.get("timezone")),
            exchange_timezone_name=safe_str(meta.get("exchangeTimezoneName")),
            regular_market_price=safe_float(meta.get("regularMarketPrice", 0)),
            fifty_two_week_high=safe_float(meta.get("fiftyTwoWeekHigh", 0)),
            fifty_two_week_low=safe_float(meta.get("fiftyTwoWeekLow", 0)),
            data_granularity=safe_str(meta.get("dataGranularity")),
            range=safe_str(meta.get("range")),
            valid_ranges=list(meta.get("validRanges", [])),
        )

    @rpc
    def GetSecFilings(self, request, context):
        """Get SEC filings."""
        data = _ticker(request).get_sec_filings()
        filings = []
        if isinstance(data, dict):
            for filing in data.get("filings", []):
                sec_filing = ticker_pb2.SecFiling(
                    type=safe_str(filing.get("type")),
                    title=safe_str(filing.get("title")),
                    url=safe_str(filing.get("edgarUrl", filing.get("url"))),
                )
                _set_timestamp(sec_filing, "date", filing.get("date"))
                filings.append(sec_filing)
        return ticker_pb2.GetSecFilingsResponse(filings=filings)
