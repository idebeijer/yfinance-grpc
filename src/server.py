"""
yfinance gRPC Server Implementation

This module implements a gRPC server that wraps the yfinance Python library,
allowing access to Yahoo Finance data over gRPC from any language.
"""

import sys
from pathlib import Path

# Add both project root and gen directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
from concurrent import futures
import logging
from datetime import datetime
from typing import Optional
from dateutil import parser as date_parser

import yfinance as yf
import pandas as pd

# Import generated protobuf and gRPC modules
from yfinance_grpc.v1 import ticker_pb2, ticker_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def datetime_to_timestamp(dt) -> Timestamp:
    """Convert datetime or pandas Timestamp to protobuf Timestamp"""
    if pd.isna(dt):
        return None
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    if isinstance(dt, datetime):
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts
    return None


def safe_float(value) -> float:
    """Safely convert value to float, handling NaN and None"""
    if pd.isna(value) or value is None:
        return 0.0
    return float(value)


def safe_int(value) -> int:
    """Safely convert value to int, handling NaN and None"""
    if pd.isna(value) or value is None:
        return 0
    return int(value)


def safe_str(value) -> str:
    """Safely convert value to string, handling None"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)


class TickerServiceServicer(ticker_pb2_grpc.TickerServiceServicer):
    """Implementation of the TickerService gRPC service"""

    def GetInfo(self, request, context):
        """Get general information about a ticker"""
        try:
            logger.info(f"GetInfo called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            info = ticker.info
            
            response = ticker_pb2.GetInfoResponse(
                info=ticker_pb2.TickerInfo(
                    symbol=safe_str(info.get('symbol', request.ticker)),
                    short_name=safe_str(info.get('shortName')),
                    long_name=safe_str(info.get('longName')),
                    industry=safe_str(info.get('industry')),
                    sector=safe_str(info.get('sector')),
                    country=safe_str(info.get('country')),
                    city=safe_str(info.get('city')),
                    state=safe_str(info.get('state')),
                    zip=safe_str(info.get('zip')),
                    website=safe_str(info.get('website')),
                    long_business_summary=safe_str(info.get('longBusinessSummary')),
                    
                    previous_close=safe_float(info.get('previousClose')),
                    open=safe_float(info.get('open')),
                    day_low=safe_float(info.get('dayLow')),
                    day_high=safe_float(info.get('dayHigh')),
                    regular_market_previous_close=safe_float(info.get('regularMarketPreviousClose')),
                    regular_market_open=safe_float(info.get('regularMarketOpen')),
                    regular_market_day_low=safe_float(info.get('regularMarketDayLow')),
                    regular_market_day_high=safe_float(info.get('regularMarketDayHigh')),
                    current_price=safe_float(info.get('currentPrice')),
                    
                    volume=safe_int(info.get('volume')),
                    regular_market_volume=safe_int(info.get('regularMarketVolume')),
                    average_volume=safe_int(info.get('averageVolume')),
                    average_volume_10days=safe_int(info.get('averageVolume10days')),
                    shares_outstanding=safe_int(info.get('sharesOutstanding')),
                    float_shares=safe_int(info.get('floatShares')),
                    
                    market_cap=safe_int(info.get('marketCap')),
                    enterprise_value=safe_float(info.get('enterpriseValue')),
                    trailing_pe=safe_float(info.get('trailingPE')),
                    forward_pe=safe_float(info.get('forwardPE')),
                    price_to_book=safe_float(info.get('priceToBook')),
                    price_to_sales_trailing_12months=safe_float(info.get('priceToSalesTrailing12Months')),
                    enterprise_to_revenue=safe_float(info.get('enterpriseToRevenue')),
                    enterprise_to_ebitda=safe_float(info.get('enterpriseToEbitda')),
                    
                    dividend_rate=safe_float(info.get('dividendRate')),
                    dividend_yield=safe_float(info.get('dividendYield')),
                    ex_dividend_date=safe_int(info.get('exDividendDate', 0)),
                    payout_ratio=safe_float(info.get('payoutRatio')),
                    five_year_avg_dividend_yield=safe_float(info.get('fiveYearAvgDividendYield')),
                    
                    beta=safe_float(info.get('beta')),
                    trailing_eps=safe_float(info.get('trailingEps')),
                    forward_eps=safe_float(info.get('forwardEps')),
                    book_value=safe_float(info.get('bookValue')),
                    profit_margins=safe_float(info.get('profitMargins')),
                    revenue_per_share=safe_float(info.get('revenuePerShare')),
                    return_on_assets=safe_float(info.get('returnOnAssets')),
                    return_on_equity=safe_float(info.get('returnOnEquity')),
                    revenue_growth=safe_float(info.get('revenueGrowth')),
                    earnings_growth=safe_float(info.get('earningsGrowth')),
                    operating_margins=safe_float(info.get('operatingMargins')),
                    ebitda_margins=safe_float(info.get('ebitdaMargins')),
                    
                    fifty_two_week_low=safe_float(info.get('fiftyTwoWeekLow')),
                    fifty_two_week_high=safe_float(info.get('fiftyTwoWeekHigh')),
                    fifty_day_average=safe_float(info.get('fiftyDayAverage')),
                    two_hundred_day_average=safe_float(info.get('twoHundredDayAverage')),
                    
                    target_high_price=safe_float(info.get('targetHighPrice')),
                    target_low_price=safe_float(info.get('targetLowPrice')),
                    target_mean_price=safe_float(info.get('targetMeanPrice')),
                    target_median_price=safe_float(info.get('targetMedianPrice')),
                    number_of_analyst_opinions=safe_int(info.get('numberOfAnalystOpinions')),
                    
                    currency=safe_str(info.get('currency')),
                    exchange=safe_str(info.get('exchange')),
                    quote_type=safe_str(info.get('quoteType')),
                    financial_currency=safe_str(info.get('financialCurrency')),
                    price_hint=safe_int(info.get('priceHint', 2)),
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in GetInfo for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching info: {str(e)}")
            return ticker_pb2.GetInfoResponse()

    def GetHistory(self, request, context):
        """Get historical market data for a ticker"""
        try:
            logger.info(f"GetHistory called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            # Build kwargs for history call
            kwargs = {}
            
            # Period or date range
            if request.HasField('period'):
                kwargs['period'] = request.period
            else:
                if request.HasField('start'):
                    kwargs['start'] = datetime.fromtimestamp(request.start.seconds)
                if request.HasField('end'):
                    kwargs['end'] = datetime.fromtimestamp(request.end.seconds)
            
            # Interval
            if request.interval:
                kwargs['interval'] = request.interval
            else:
                kwargs['interval'] = '1d'
            
            # Options - use HasField for optional booleans to detect if they were set
            # This allows us to use yfinance defaults when not specified
            if request.HasField('prepost'):
                kwargs['prepost'] = request.prepost
            # default is False, which matches yfinance
            
            if request.HasField('actions'):
                kwargs['actions'] = request.actions
            else:
                kwargs['actions'] = True  # yfinance default
            
            if request.HasField('auto_adjust'):
                kwargs['auto_adjust'] = request.auto_adjust
            else:
                kwargs['auto_adjust'] = True  # yfinance default
            
            if request.HasField('back_adjust'):
                kwargs['back_adjust'] = request.back_adjust
            # default is False, which matches yfinance
            
            if request.HasField('repair'):
                kwargs['repair'] = request.repair
            # default is False, which matches yfinance
            
            if request.HasField('keepna'):
                kwargs['keepna'] = request.keepna
            # default is False, which matches yfinance
            
            if request.HasField('rounding'):
                kwargs['rounding'] = request.rounding
            # default is False, which matches yfinance
            
            # Get history
            hist = ticker.history(**kwargs)
            
            # Convert to response
            rows = []
            for idx, row in hist.iterrows():
                history_row = ticker_pb2.HistoryRow(
                    date=datetime_to_timestamp(idx),
                    open=safe_float(row.get('Open', 0)),
                    high=safe_float(row.get('High', 0)),
                    low=safe_float(row.get('Low', 0)),
                    close=safe_float(row.get('Close', 0)),
                    volume=safe_int(row.get('Volume', 0)),
                )
                
                # Optional fields
                if 'Dividends' in row and row['Dividends'] > 0:
                    history_row.dividends = safe_float(row['Dividends'])
                if 'Stock Splits' in row and row['Stock Splits'] > 0:
                    history_row.stock_splits = safe_float(row['Stock Splits'])
                if 'Capital Gains' in row and row['Capital Gains'] > 0:
                    history_row.capital_gains = safe_float(row['Capital Gains'])
                
                rows.append(history_row)
            
            return ticker_pb2.GetHistoryResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetHistory for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching history: {str(e)}")
            return ticker_pb2.GetHistoryResponse()

    def GetDividends(self, request, context):
        """Get dividend history for a ticker"""
        try:
            logger.info(f"GetDividends called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            period = request.period if request.HasField('period') else 'max'
            dividends = ticker.get_dividends(period=period)
            
            rows = []
            for idx, value in dividends.items():
                rows.append(ticker_pb2.DividendRow(
                    date=datetime_to_timestamp(idx),
                    amount=safe_float(value)
                ))
            
            return ticker_pb2.GetDividendsResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetDividends for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching dividends: {str(e)}")
            return ticker_pb2.GetDividendsResponse()

    def GetSplits(self, request, context):
        """Get stock split history for a ticker"""
        try:
            logger.info(f"GetSplits called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            period = request.period if request.HasField('period') else 'max'
            splits = ticker.get_splits(period=period)
            
            rows = []
            for idx, value in splits.items():
                rows.append(ticker_pb2.SplitRow(
                    date=datetime_to_timestamp(idx),
                    ratio=safe_float(value)
                ))
            
            return ticker_pb2.GetSplitsResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetSplits for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching splits: {str(e)}")
            return ticker_pb2.GetSplitsResponse()

    def GetActions(self, request, context):
        """Get all corporate actions (dividends, splits, capital gains)"""
        try:
            logger.info(f"GetActions called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            period = request.period if request.HasField('period') else 'max'
            actions = ticker.get_actions(period=period)
            
            rows = []
            for idx, row in actions.iterrows():
                action_row = ticker_pb2.ActionRow(
                    date=datetime_to_timestamp(idx)
                )
                
                if 'Dividends' in row and not pd.isna(row['Dividends']) and row['Dividends'] > 0:
                    action_row.dividends = safe_float(row['Dividends'])
                if 'Stock Splits' in row and not pd.isna(row['Stock Splits']) and row['Stock Splits'] > 0:
                    action_row.stock_splits = safe_float(row['Stock Splits'])
                if 'Capital Gains' in row and not pd.isna(row['Capital Gains']) and row['Capital Gains'] > 0:
                    action_row.capital_gains = safe_float(row['Capital Gains'])
                
                rows.append(action_row)
            
            return ticker_pb2.GetActionsResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetActions for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching actions: {str(e)}")
            return ticker_pb2.GetActionsResponse()

    def GetFinancials(self, request, context):
        """Get financial statements (income statement)"""
        try:
            logger.info(f"GetFinancials called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            freq = request.freq if request.freq else 'yearly'
            financials = ticker.get_financials(freq=freq, as_dict=False, pretty=request.pretty)
            
            statements = []
            for col in financials.columns:
                values = {}
                for idx in financials.index:
                    value = financials.loc[idx, col]
                    if not pd.isna(value):
                        values[str(idx)] = safe_float(value)
                
                statements.append(ticker_pb2.FinancialStatement(
                    date=datetime_to_timestamp(col),
                    values=values
                ))
            
            return ticker_pb2.GetFinancialsResponse(statements=statements)
            
        except Exception as e:
            logger.error(f"Error in GetFinancials for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching financials: {str(e)}")
            return ticker_pb2.GetFinancialsResponse()

    def GetBalanceSheet(self, request, context):
        """Get balance sheet data"""
        try:
            logger.info(f"GetBalanceSheet called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            freq = request.freq if request.freq else 'yearly'
            balance_sheet = ticker.get_balance_sheet(freq=freq, as_dict=False, pretty=request.pretty)
            
            statements = []
            for col in balance_sheet.columns:
                values = {}
                for idx in balance_sheet.index:
                    value = balance_sheet.loc[idx, col]
                    if not pd.isna(value):
                        values[str(idx)] = safe_float(value)
                
                statements.append(ticker_pb2.BalanceSheetStatement(
                    date=datetime_to_timestamp(col),
                    values=values
                ))
            
            return ticker_pb2.GetBalanceSheetResponse(statements=statements)
            
        except Exception as e:
            logger.error(f"Error in GetBalanceSheet for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching balance sheet: {str(e)}")
            return ticker_pb2.GetBalanceSheetResponse()

    def GetCashFlow(self, request, context):
        """Get cash flow statement data"""
        try:
            logger.info(f"GetCashFlow called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            freq = request.freq if request.freq else 'yearly'
            cash_flow = ticker.get_cash_flow(freq=freq, as_dict=False, pretty=request.pretty)
            
            statements = []
            for col in cash_flow.columns:
                values = {}
                for idx in cash_flow.index:
                    value = cash_flow.loc[idx, col]
                    if not pd.isna(value):
                        values[str(idx)] = safe_float(value)
                
                statements.append(ticker_pb2.CashFlowStatement(
                    date=datetime_to_timestamp(col),
                    values=values
                ))
            
            return ticker_pb2.GetCashFlowResponse(statements=statements)
            
        except Exception as e:
            logger.error(f"Error in GetCashFlow for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching cash flow: {str(e)}")
            return ticker_pb2.GetCashFlowResponse()

    def GetEarnings(self, request, context):
        """Get earnings data"""
        try:
            logger.info(f"GetEarnings called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            freq = request.freq if request.freq else 'yearly'
            earnings = ticker.get_earnings(freq=freq, as_dict=False)
            
            rows = []
            if earnings is not None and not earnings.empty:
                for idx, row in earnings.iterrows():
                    earnings_row = ticker_pb2.EarningsRow(
                        date=datetime_to_timestamp(idx)
                    )
                    
                    if 'Revenue' in row:
                        earnings_row.revenue = safe_float(row['Revenue'])
                    if 'Earnings' in row:
                        earnings_row.earnings = safe_float(row['Earnings'])
                    
                    rows.append(earnings_row)
            
            return ticker_pb2.GetEarningsResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetEarnings for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching earnings: {str(e)}")
            return ticker_pb2.GetEarningsResponse()

    def GetRecommendations(self, request, context):
        """Get analyst recommendations"""
        try:
            logger.info(f"GetRecommendations called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            # Use upgrades_downgrades which has the detailed recommendation data
            recommendations = ticker.upgrades_downgrades

            rows = []
            if recommendations is not None and not recommendations.empty:
                # Sort by date descending (most recent first)
                recommendations = recommendations.sort_index(ascending=False)
                
                for idx, row in recommendations.iterrows():
                    rows.append(ticker_pb2.RecommendationRow(
                        date=datetime_to_timestamp(idx),
                        firm=safe_str(row.get('Firm', '')),
                        to_grade=safe_str(row.get('ToGrade', '')),
                        from_grade=safe_str(row.get('FromGrade', '')),
                        action=safe_str(row.get('Action', ''))
                    ))
            
            return ticker_pb2.GetRecommendationsResponse(rows=rows)
            
        except Exception as e:
            logger.error(f"Error in GetRecommendations for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching recommendations: {str(e)}")
            return ticker_pb2.GetRecommendationsResponse()

    def GetOptions(self, request, context):
        """Get available option expiration dates"""
        try:
            logger.info(f"GetOptions called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            options = ticker.options
            
            return ticker_pb2.GetOptionsResponse(expiration_dates=list(options))
            
        except Exception as e:
            logger.error(f"Error in GetOptions for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching options: {str(e)}")
            return ticker_pb2.GetOptionsResponse()

    def GetOptionChain(self, request, context):
        """Get option chain data for a specific expiration date"""
        try:
            logger.info(f"GetOptionChain called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            date = request.date if request.HasField('date') else None
            tz = request.tz if request.HasField('tz') else None
            
            option_chain = ticker.option_chain(date=date, tz=tz)
            
            # Convert calls
            calls = []
            for _, row in option_chain.calls.iterrows():
                calls.append(ticker_pb2.OptionContract(
                    contract_symbol=safe_str(row.get('contractSymbol', '')),
                    strike=safe_float(row.get('strike', 0)),
                    currency=safe_str(row.get('currency', '')),
                    last_price=safe_float(row.get('lastPrice', 0)),
                    bid=safe_float(row.get('bid', 0)),
                    ask=safe_float(row.get('ask', 0)),
                    change=safe_float(row.get('change', 0)),
                    percent_change=safe_float(row.get('percentChange', 0)),
                    volume=safe_int(row.get('volume', 0)),
                    open_interest=safe_int(row.get('openInterest', 0)),
                    implied_volatility=safe_float(row.get('impliedVolatility', 0)),
                    in_the_money=bool(row.get('inTheMoney', False)),
                    contract_size=safe_str(row.get('contractSize', 'REGULAR')),
                    last_trade_date=datetime_to_timestamp(row.get('lastTradeDate'))
                ))
            
            # Convert puts
            puts = []
            for _, row in option_chain.puts.iterrows():
                puts.append(ticker_pb2.OptionContract(
                    contract_symbol=safe_str(row.get('contractSymbol', '')),
                    strike=safe_float(row.get('strike', 0)),
                    currency=safe_str(row.get('currency', '')),
                    last_price=safe_float(row.get('lastPrice', 0)),
                    bid=safe_float(row.get('bid', 0)),
                    ask=safe_float(row.get('ask', 0)),
                    change=safe_float(row.get('change', 0)),
                    percent_change=safe_float(row.get('percentChange', 0)),
                    volume=safe_int(row.get('volume', 0)),
                    open_interest=safe_int(row.get('openInterest', 0)),
                    implied_volatility=safe_float(row.get('impliedVolatility', 0)),
                    in_the_money=bool(row.get('inTheMoney', False)),
                    contract_size=safe_str(row.get('contractSize', 'REGULAR')),
                    last_trade_date=datetime_to_timestamp(row.get('lastTradeDate'))
                ))
            
            return ticker_pb2.GetOptionChainResponse(calls=calls, puts=puts)
            
        except Exception as e:
            logger.error(f"Error in GetOptionChain for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching option chain: {str(e)}")
            return ticker_pb2.GetOptionChainResponse()

    def GetCalendar(self, request, context):
        """Get upcoming events, earnings, and dividends"""
        try:
            logger.info(f"GetCalendar called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            calendar = ticker.get_calendar()
            
            response = ticker_pb2.GetCalendarResponse()
            
            if calendar and isinstance(calendar, dict):
                # Earnings dates
                if 'Earnings Date' in calendar:
                    earnings_dates = calendar['Earnings Date']
                    if isinstance(earnings_dates, list) and len(earnings_dates) > 0:
                        earnings = ticker_pb2.EarningsDate()
                        if len(earnings_dates) > 0:
                            earnings.start.CopyFrom(datetime_to_timestamp(earnings_dates[0]))
                        if len(earnings_dates) > 1:
                            earnings.end.CopyFrom(datetime_to_timestamp(earnings_dates[1]))
                        response.earnings.CopyFrom(earnings)
                
                # Ex-dividend date
                if 'Ex-Dividend Date' in calendar:
                    ex_div = calendar['Ex-Dividend Date']
                    if ex_div:
                        div_date = ticker_pb2.DividendDate()
                        div_date.date.CopyFrom(datetime_to_timestamp(ex_div))
                        response.ex_dividend_date.CopyFrom(div_date)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in GetCalendar for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching calendar: {str(e)}")
            return ticker_pb2.GetCalendarResponse()

    def GetNews(self, request, context):
        """Get recent news articles for a ticker"""
        try:
            logger.info(f"GetNews called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            count = request.count if request.count > 0 else 10
            news = ticker.news
            
            articles = []
            for article_wrapper in news[:count]:
                article = article_wrapper.get('content', article_wrapper)
                
                news_article = ticker_pb2.NewsArticle(
                    uuid=safe_str(article.get('id', '')),
                    title=safe_str(article.get('title', '')),
                    publisher=safe_str(article.get('provider', {}).get('displayName', '')),
                    link=safe_str(article.get('canonicalUrl', {}).get('url', '')),
                    type=safe_str(article.get('contentType', ''))
                )
                
                if 'pubDate' in article:
                    try:
                        dt = date_parser.isoparse(article['pubDate'])
                        news_article.provider_publish_time.FromDatetime(dt)
                    except Exception:
                        pass
                
                if 'thumbnail' in article and article['thumbnail']:
                    thumbnail = article['thumbnail']
                    if isinstance(thumbnail, dict) and 'resolutions' in thumbnail:
                        resolutions = thumbnail['resolutions']
                        if resolutions and len(resolutions) > 0:
                            news_article.thumbnail = safe_str(resolutions[0].get('url', ''))
                    elif isinstance(thumbnail, dict) and 'originalUrl' in thumbnail:
                        news_article.thumbnail = safe_str(thumbnail['originalUrl'])
                
                articles.append(news_article)
            
            return ticker_pb2.GetNewsResponse(articles=articles)
            
        except Exception as e:
            logger.error(f"Error in GetNews for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching news: {str(e)}")
            return ticker_pb2.GetNewsResponse()

    def GetMajorHolders(self, request, context):
        """Get major holders information"""
        try:
            logger.info(f"GetMajorHolders called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            major_holders = ticker.get_major_holders(as_dict=False)
            
            holders = {}
            if major_holders is not None and not major_holders.empty:
                for _, row in major_holders.iterrows():
                    if len(row) >= 2:
                        holders[safe_str(row[1])] = safe_str(row[0])
            
            return ticker_pb2.GetMajorHoldersResponse(holders=holders)
            
        except Exception as e:
            logger.error(f"Error in GetMajorHolders for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching major holders: {str(e)}")
            return ticker_pb2.GetMajorHoldersResponse()

    def GetInstitutionalHolders(self, request, context):
        """Get institutional holders information"""
        try:
            logger.info(f"GetInstitutionalHolders called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            institutional_holders = ticker.get_institutional_holders(as_dict=False)
            
            holders = []
            if institutional_holders is not None and not institutional_holders.empty:
                for _, row in institutional_holders.iterrows():
                    holders.append(ticker_pb2.InstitutionalHolder(
                        holder=safe_str(row.get('Holder', '')),
                        shares=safe_int(row.get('Shares', 0)),
                        date_reported=datetime_to_timestamp(row.get('Date Reported')),
                        pct_out=safe_float(row.get('% Out', 0)),
                        value=safe_float(row.get('Value', 0))
                    ))
            
            return ticker_pb2.GetInstitutionalHoldersResponse(holders=holders)
            
        except Exception as e:
            logger.error(f"Error in GetInstitutionalHolders for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching institutional holders: {str(e)}")
            return ticker_pb2.GetInstitutionalHoldersResponse()

    def GetMutualFundHolders(self, request, context):
        """Get mutual fund holders information"""
        try:
            logger.info(f"GetMutualFundHolders called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            
            mutualfund_holders = ticker.get_mutualfund_holders(as_dict=False)
            
            holders = []
            if mutualfund_holders is not None and not mutualfund_holders.empty:
                for _, row in mutualfund_holders.iterrows():
                    holders.append(ticker_pb2.MutualFundHolder(
                        holder=safe_str(row.get('Holder', '')),
                        shares=safe_int(row.get('Shares', 0)),
                        date_reported=datetime_to_timestamp(row.get('Date Reported')),
                        pct_out=safe_float(row.get('% Out', 0)),
                        value=safe_float(row.get('Value', 0))
                    ))
            
            return ticker_pb2.GetMutualFundHoldersResponse(holders=holders)
            
        except Exception as e:
            logger.error(f"Error in GetMutualFundHolders for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching mutual fund holders: {str(e)}")
            return ticker_pb2.GetMutualFundHoldersResponse()


def serve(port: int = 50051, max_workers: int = 10):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    ticker_pb2_grpc.add_TickerServiceServicer_to_server(
        TickerServiceServicer(), server
    )
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()
    logger.info(f"Server started on port {port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
