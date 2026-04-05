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
from grpc_reflection.v1alpha import reflection

import yfinance as yf
import pandas as pd

# Import generated protobuf and gRPC modules
from yfinance_grpc.v1alpha1 import ticker_pb2, ticker_pb2_grpc
from yfinance_grpc.v1alpha1 import search_pb2, search_pb2_grpc
from yfinance_grpc.v1alpha1 import market_pb2, market_pb2_grpc
from yfinance_grpc.v1alpha1 import sector_pb2, sector_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from src.search_server import SearchServiceServicer
from src.market_server import MarketServiceServicer
from src.sector_server import SectorServiceServicer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_STREAM_BATCH_SIZE = 500


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


def create_ticker_info(info: dict, symbol: str) -> ticker_pb2.TickerInfo:
    """Create a TickerInfo message from info dict"""
    return ticker_pb2.TickerInfo(
        symbol=safe_str(info.get('symbol', symbol)),
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


class TickerServiceServicer(ticker_pb2_grpc.TickerServiceServicer):
    """Implementation of the TickerService gRPC service"""

    def GetInfo(self, request, context):
        """Get general information about a ticker"""
        try:
            logger.info(f"GetInfo called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            info = ticker.info
            
            response = ticker_pb2.GetInfoResponse(
                info=create_ticker_info(info, request.ticker)
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
                    kwargs['start'] = request.start.ToDatetime()
                if request.HasField('end'):
                    kwargs['end'] = request.end.ToDatetime()
            
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
                    except Exception as e:
                        logger.warning(f"Failed to parse pubDate '{article['pubDate']}': {e}")
                
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
            
            major_holders = ticker.get_major_holders(as_dict=True)

            holders = {}
            if major_holders and isinstance(major_holders, dict):
                holders = {k: safe_str(v) for k, v in major_holders.items()}
            
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

    def GetMultipleInfo(self, request, context):
        """Get information for multiple tickers at once"""
        if not request.tickers:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Tickers list cannot be empty")
            return ticker_pb2.GetMultipleInfoResponse()

        try:
            tickers_str = ' '.join(request.tickers)
            logger.info(f"GetMultipleInfo called for tickers: {tickers_str}")
            
            tickers_obj = yf.Tickers(tickers_str)
            info_map = {}
            
            for symbol, ticker in tickers_obj.tickers.items():
                try:
                    info = ticker.info
                    info_map[symbol] = create_ticker_info(info, symbol)
                    
                except Exception as e:
                    logger.error(f"Error fetching info for {symbol}: {str(e)}")
                    # Continue with other tickers even if one fails
                    continue
            
            return ticker_pb2.GetMultipleInfoResponse(info=info_map)
            
        except Exception as e:
            logger.error(f"Error in GetMultipleInfo: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching multiple ticker info: {str(e)}")
            return ticker_pb2.GetMultipleInfoResponse()

    def DownloadHistory(self, request, context):
        """Stream historical data for multiple tickers"""
        if not request.tickers:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Tickers list cannot be empty")
            return

        try:
            tickers_str = ' '.join(request.tickers)
            logger.info(f"DownloadHistory called for tickers: {tickers_str}")
            
            # Build download parameters
            kwargs = {
                'group_by': 'ticker',
                'auto_adjust': request.auto_adjust if request.HasField('auto_adjust') else True,
                'threads': True,  # Use threading for faster downloads
            }
            
            # Handle period or start/end dates
            if request.HasField('period'):
                kwargs['period'] = request.period
            else:
                if request.HasField('start'):
                    kwargs['start'] = request.start.ToDatetime()
                if request.HasField('end'):
                    kwargs['end'] = request.end.ToDatetime()
            
            if request.HasField('interval'):
                kwargs['interval'] = request.interval
            
            # Download data
            data = yf.download(tickers_str, **kwargs)

            # Handle empty data
            if data.empty:
                logger.warning(f"No data returned for {tickers_str}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No historical data found for {tickers_str}")
                return
            
            is_multi = isinstance(data.columns, pd.MultiIndex)

            # Handle single ticker vs multiple tickers
            if len(request.tickers) == 1:
                ticker = request.tickers[0]
                batch = []

                for idx, row in data.iterrows():
                    # For single ticker with group_by='ticker', columns may be MultiIndex (ticker, price_type)
                    if is_multi:
                        open_val = safe_float(row.get((ticker, 'Open'), 0))
                        high_val = safe_float(row.get((ticker, 'High'), 0))
                        low_val = safe_float(row.get((ticker, 'Low'), 0))
                        close_val = safe_float(row.get((ticker, 'Close'), 0))
                        volume_val = safe_int(row.get((ticker, 'Volume'), 0))
                    else:
                        open_val = safe_float(row.get('Open', 0))
                        high_val = safe_float(row.get('High', 0))
                        low_val = safe_float(row.get('Low', 0))
                        close_val = safe_float(row.get('Close', 0))
                        volume_val = safe_int(row.get('Volume', 0))

                    batch.append(ticker_pb2.HistoryRow(
                        date=datetime_to_timestamp(idx),
                        open=open_val,
                        high=high_val,
                        low=low_val,
                        close=close_val,
                        volume=volume_val
                    ))

                    if len(batch) >= _STREAM_BATCH_SIZE:
                        yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)
                        batch = []

                if batch:
                    yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)
            else:
                # Multiple tickers - group by ticker and stream each
                for ticker in request.tickers:
                    try:
                        ticker_data = data[ticker]
                        batch = []

                        for idx, row in ticker_data.iterrows():
                            batch.append(ticker_pb2.HistoryRow(
                                date=datetime_to_timestamp(idx),
                                open=safe_float(row.get('Open', 0)),
                                high=safe_float(row.get('High', 0)),
                                low=safe_float(row.get('Low', 0)),
                                close=safe_float(row.get('Close', 0)),
                                volume=safe_int(row.get('Volume', 0))
                            ))

                            if len(batch) >= _STREAM_BATCH_SIZE:
                                yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)
                                batch = []

                        if batch:
                            yield ticker_pb2.DownloadHistoryResponse(ticker=ticker, rows=batch)

                    except KeyError:
                        logger.error(f"Ticker '{ticker}' not found in data. Check ticker symbol is correct.")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing data for {ticker}: {str(e)}")
                        continue
            
        except Exception as e:
            logger.error(f"Error in DownloadHistory: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error downloading history: {str(e)}")


    def GetCapitalGains(self, request, context):
        """Get capital gains distributions for a ticker"""
        try:
            logger.info(f"GetCapitalGains called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            period = request.period if request.HasField('period') else 'max'
            gains = ticker.get_capital_gains(period=period)
            rows = []
            for idx, value in gains.items():
                rows.append(ticker_pb2.CapitalGainsRow(
                    date=datetime_to_timestamp(idx),
                    amount=safe_float(value)
                ))
            return ticker_pb2.GetCapitalGainsResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetCapitalGains for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching capital gains: {str(e)}")
            return ticker_pb2.GetCapitalGainsResponse()

    def GetSharesHistory(self, request, context):
        """Get full history of shares outstanding"""
        try:
            logger.info(f"GetSharesHistory called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            kwargs = {}
            if request.HasField('start'):
                kwargs['start'] = request.start.ToDatetime()
            if request.HasField('end'):
                kwargs['end'] = request.end.ToDatetime()
            shares = ticker.get_shares_full(**kwargs)
            rows = []
            if shares is not None:
                for idx, value in shares.items():
                    rows.append(ticker_pb2.SharesHistoryRow(
                        date=datetime_to_timestamp(idx),
                        shares=safe_int(value)
                    ))
            return ticker_pb2.GetSharesHistoryResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetSharesHistory for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching shares history: {str(e)}")
            return ticker_pb2.GetSharesHistoryResponse()

    def GetIsin(self, request, context):
        """Get the ISIN code for a ticker"""
        try:
            logger.info(f"GetIsin called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            isin = ticker.get_isin() or ''
            return ticker_pb2.GetIsinResponse(isin=isin)
        except Exception as e:
            logger.error(f"Error in GetIsin for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching ISIN: {str(e)}")
            return ticker_pb2.GetIsinResponse()

    def GetFastInfo(self, request, context):
        """Get a lightweight snapshot of key price/market data"""
        try:
            logger.info(f"GetFastInfo called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            fi = ticker.get_fast_info()
            info = ticker_pb2.FastInfo(
                currency=safe_str(getattr(fi, 'currency', None)),
                exchange=safe_str(getattr(fi, 'exchange', None)),
                exchange_data_delayed_by=safe_int(getattr(fi, 'exchange_data_delayed_by', 0)),
                exchange_timezone_name=safe_str(getattr(fi, 'exchange_timezone_name', None)),
                last_price=safe_float(getattr(fi, 'last_price', 0)),
                last_volume=safe_int(getattr(fi, 'last_volume', 0)),
                market_cap=safe_int(getattr(fi, 'market_cap', 0)),
                open=safe_float(getattr(fi, 'open', 0)),
                previous_close=safe_float(getattr(fi, 'previous_close', 0)),
                quote_type=safe_str(getattr(fi, 'quote_type', None)),
                regular_market_day_high=safe_float(getattr(fi, 'regular_market_day_high', 0)),
                regular_market_day_low=safe_float(getattr(fi, 'regular_market_day_low', 0)),
                regular_market_previous_close=safe_float(getattr(fi, 'regular_market_previous_close', 0)),
                regular_market_price=safe_float(getattr(fi, 'regular_market_price', 0)),
                shares=safe_int(getattr(fi, 'shares', 0)),
                three_month_average_volume=safe_float(getattr(fi, 'three_month_average_volume', 0)),
                timezone=safe_str(getattr(fi, 'timezone', None)),
                fifty_day_average=safe_float(getattr(fi, 'fifty_day_average', 0)),
                two_hundred_day_average=safe_float(getattr(fi, 'two_hundred_day_average', 0)),
                year_change=safe_float(getattr(fi, 'year_change', 0)),
                year_high=safe_float(getattr(fi, 'year_high', 0)),
                year_low=safe_float(getattr(fi, 'year_low', 0)),
            )
            return ticker_pb2.GetFastInfoResponse(info=info)
        except Exception as e:
            logger.error(f"Error in GetFastInfo for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching fast info: {str(e)}")
            return ticker_pb2.GetFastInfoResponse()

    def GetSustainability(self, request, context):
        """Get ESG scores and controversy flags"""
        try:
            logger.info(f"GetSustainability called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_sustainability(as_dict=True)
            if not data:
                return ticker_pb2.GetSustainabilityResponse()
            return ticker_pb2.GetSustainabilityResponse(
                total_esg=safe_float(data.get('totalEsg', 0)),
                esg_performance=safe_str(data.get('esgPerformance')),
                environment_score=safe_float(data.get('environmentScore', 0)),
                social_score=safe_float(data.get('socialScore', 0)),
                governance_score=safe_float(data.get('governanceScore', 0)),
                percentile=safe_float(data.get('percentile', 0)),
                peer_group=safe_str(data.get('peerGroup')),
                adult=bool(data.get('adult', False)),
                alcoholic=bool(data.get('alcoholic', False)),
                animal_testing=bool(data.get('animalTesting', False)),
                catholic=bool(data.get('catholic', False)),
                controversial_weapons=bool(data.get('controversialWeapons', False)),
                small_arms=bool(data.get('smallArms', False)),
                fur_leather=bool(data.get('furLeather', False)),
                gambling=bool(data.get('gambling', False)),
                gmo=bool(data.get('gmo', False)),
                military_contract=bool(data.get('militaryContract', False)),
                nuclear=bool(data.get('nuclear', False)),
                pesticides=bool(data.get('pesticides', False)),
                palm_oil=bool(data.get('palmOil', False)),
                coal=bool(data.get('coal', False)),
                tobacco=bool(data.get('tobacco', False)),
            )
        except Exception as e:
            logger.error(f"Error in GetSustainability for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching sustainability: {str(e)}")
            return ticker_pb2.GetSustainabilityResponse()

    def GetInsiderPurchases(self, request, context):
        """Get summary table of insider buying/selling activity"""
        try:
            logger.info(f"GetInsiderPurchases called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_insider_purchases(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for label, row in data.iterrows():
                    rows.append(ticker_pb2.InsiderPurchaseSummaryRow(
                        label=safe_str(label),
                        values={safe_str(col): safe_str(row[col]) for col in data.columns}
                    ))
            return ticker_pb2.GetInsiderPurchasesResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetInsiderPurchases for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching insider purchases: {str(e)}")
            return ticker_pb2.GetInsiderPurchasesResponse()

    def GetInsiderTransactions(self, request, context):
        """Get individual insider transaction records"""
        try:
            logger.info(f"GetInsiderTransactions called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_insider_transactions(as_dict=False)
            transactions = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    transactions.append(ticker_pb2.InsiderTransaction(
                        start_date=datetime_to_timestamp(row.get('Start Date', idx)),
                        insider=safe_str(row.get('Insider', '')),
                        position=safe_str(row.get('Position', '')),
                        transaction=safe_str(row.get('Transaction', '')),
                        shares=safe_int(row.get('Shares', 0)),
                        value=safe_float(row.get('Value', 0)),
                        text=safe_str(row.get('Text', '')),
                        url=safe_str(row.get('URL', '')),
                    ))
            return ticker_pb2.GetInsiderTransactionsResponse(transactions=transactions)
        except Exception as e:
            logger.error(f"Error in GetInsiderTransactions for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching insider transactions: {str(e)}")
            return ticker_pb2.GetInsiderTransactionsResponse()

    def GetInsiderRosterHolders(self, request, context):
        """Get the roster of insider holders"""
        try:
            logger.info(f"GetInsiderRosterHolders called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_insider_roster_holders(as_dict=False)
            holders = []
            if data is not None and not data.empty:
                for _, row in data.iterrows():
                    holders.append(ticker_pb2.InsiderRosterHolder(
                        name=safe_str(row.get('Name', '')),
                        position=safe_str(row.get('Position', '')),
                        url=safe_str(row.get('URL', '')),
                        most_recent_transaction=datetime_to_timestamp(row.get('Most Recent Transaction')),
                        latest_transaction_shares=safe_int(row.get('Latest Transaction Shares', 0)),
                    ))
            return ticker_pb2.GetInsiderRosterHoldersResponse(holders=holders)
        except Exception as e:
            logger.error(f"Error in GetInsiderRosterHolders for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching insider roster holders: {str(e)}")
            return ticker_pb2.GetInsiderRosterHoldersResponse()

    def GetAnalystPriceTargets(self, request, context):
        """Get consensus analyst price targets"""
        try:
            logger.info(f"GetAnalystPriceTargets called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            targets = ticker.get_analyst_price_targets()
            return ticker_pb2.GetAnalystPriceTargetsResponse(
                current=safe_float(targets.get('current', 0)),
                low=safe_float(targets.get('low', 0)),
                high=safe_float(targets.get('high', 0)),
                mean=safe_float(targets.get('mean', 0)),
                median=safe_float(targets.get('median', 0)),
            )
        except Exception as e:
            logger.error(f"Error in GetAnalystPriceTargets for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching analyst price targets: {str(e)}")
            return ticker_pb2.GetAnalystPriceTargetsResponse()

    def GetRecommendationsSummary(self, request, context):
        """Get period-based aggregated analyst recommendation counts"""
        try:
            logger.info(f"GetRecommendationsSummary called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_recommendations(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.RecommendationSummaryRow(
                        period=safe_str(idx),
                        strong_buy=safe_int(row.get('strongBuy', 0)),
                        buy=safe_int(row.get('buy', 0)),
                        hold=safe_int(row.get('hold', 0)),
                        sell=safe_int(row.get('sell', 0)),
                        strong_sell=safe_int(row.get('strongSell', 0)),
                    ))
            return ticker_pb2.GetRecommendationsSummaryResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetRecommendationsSummary for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching recommendations summary: {str(e)}")
            return ticker_pb2.GetRecommendationsSummaryResponse()

    def GetEarningsEstimate(self, request, context):
        """Get forward EPS estimates by period"""
        try:
            logger.info(f"GetEarningsEstimate called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_earnings_estimate(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.EarningsEstimateRow(
                        period=safe_str(idx),
                        number_of_analysts=safe_int(row.get('numberOfAnalysts', 0)),
                        avg=safe_float(row.get('avg', 0)),
                        low=safe_float(row.get('low', 0)),
                        high=safe_float(row.get('high', 0)),
                        year_ago_eps=safe_float(row.get('yearAgoEps', 0)),
                        growth=safe_float(row.get('growth', 0)),
                    ))
            return ticker_pb2.GetEarningsEstimateResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetEarningsEstimate for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching earnings estimate: {str(e)}")
            return ticker_pb2.GetEarningsEstimateResponse()

    def GetRevenueEstimate(self, request, context):
        """Get forward revenue estimates by period"""
        try:
            logger.info(f"GetRevenueEstimate called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_revenue_estimate(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.RevenueEstimateRow(
                        period=safe_str(idx),
                        number_of_analysts=safe_int(row.get('numberOfAnalysts', 0)),
                        avg=safe_float(row.get('avg', 0)),
                        low=safe_float(row.get('low', 0)),
                        high=safe_float(row.get('high', 0)),
                        year_ago_revenue=safe_float(row.get('yearAgoRevenue', 0)),
                        growth=safe_float(row.get('growth', 0)),
                    ))
            return ticker_pb2.GetRevenueEstimateResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetRevenueEstimate for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching revenue estimate: {str(e)}")
            return ticker_pb2.GetRevenueEstimateResponse()

    def GetEarningsHistory(self, request, context):
        """Get historical EPS actuals vs estimates"""
        try:
            logger.info(f"GetEarningsHistory called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_earnings_history(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.EarningsHistoryRow(
                        date=datetime_to_timestamp(idx),
                        eps_estimate=safe_float(row.get('epsEstimate', 0)),
                        eps_actual=safe_float(row.get('epsActual', 0)),
                        eps_difference=safe_float(row.get('epsDifference', 0)),
                        surprise_percent=safe_float(row.get('surprisePercent', 0)),
                    ))
            return ticker_pb2.GetEarningsHistoryResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetEarningsHistory for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching earnings history: {str(e)}")
            return ticker_pb2.GetEarningsHistoryResponse()

    def GetEpsTrend(self, request, context):
        """Get EPS estimate trend across recent revision windows"""
        try:
            logger.info(f"GetEpsTrend called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_eps_trend(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.EpsTrendRow(
                        period=safe_str(idx),
                        current=safe_float(row.get('current', 0)),
                        seven_days_ago=safe_float(row.get('7daysAgo', 0)),
                        thirty_days_ago=safe_float(row.get('30daysAgo', 0)),
                        sixty_days_ago=safe_float(row.get('60daysAgo', 0)),
                        ninety_days_ago=safe_float(row.get('90daysAgo', 0)),
                    ))
            return ticker_pb2.GetEpsTrendResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetEpsTrend for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching EPS trend: {str(e)}")
            return ticker_pb2.GetEpsTrendResponse()

    def GetEpsRevisions(self, request, context):
        """Get counts of upward/downward EPS revisions"""
        try:
            logger.info(f"GetEpsRevisions called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_eps_revisions(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.EpsRevisionsRow(
                        period=safe_str(idx),
                        up_last_7days=safe_int(row.get('upLast7days', 0)),
                        up_last_30days=safe_int(row.get('upLast30days', 0)),
                        down_last_7days=safe_int(row.get('downLast7days', 0)),
                        down_last_30days=safe_int(row.get('downLast30days', 0)),
                    ))
            return ticker_pb2.GetEpsRevisionsResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetEpsRevisions for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching EPS revisions: {str(e)}")
            return ticker_pb2.GetEpsRevisionsResponse()

    def GetGrowthEstimates(self, request, context):
        """Get growth estimates for stock, industry, sector and index"""
        try:
            logger.info(f"GetGrowthEstimates called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_growth_estimates(as_dict=False)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    rows.append(ticker_pb2.GrowthEstimatesRow(
                        period=safe_str(idx),
                        stock=safe_float(row.get('stock', 0)),
                        industry=safe_float(row.get('industry', 0)),
                        sector=safe_float(row.get('sector', 0)),
                        index=safe_float(row.get('index', 0)),
                    ))
            return ticker_pb2.GetGrowthEstimatesResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetGrowthEstimates for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching growth estimates: {str(e)}")
            return ticker_pb2.GetGrowthEstimatesResponse()

    def GetEarningsDates(self, request, context):
        """Get upcoming and past earnings dates with EPS data"""
        try:
            logger.info(f"GetEarningsDates called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            limit = request.limit if request.HasField('limit') else 12
            data = ticker.get_earnings_dates(limit=limit)
            rows = []
            if data is not None and not data.empty:
                for idx, row in data.iterrows():
                    earnings_row = ticker_pb2.EarningsDateRow(
                        date=datetime_to_timestamp(idx),
                    )
                    eps_est = row.get('EPS Estimate')
                    if eps_est is not None and not pd.isna(eps_est):
                        earnings_row.eps_estimate = safe_float(eps_est)
                    reported = row.get('Reported EPS')
                    if reported is not None and not pd.isna(reported):
                        earnings_row.reported_eps = safe_float(reported)
                    surprise = row.get('Surprise(%)')
                    if surprise is not None and not pd.isna(surprise):
                        earnings_row.surprise_pct = safe_float(surprise)
                    rows.append(earnings_row)
            return ticker_pb2.GetEarningsDatesResponse(rows=rows)
        except Exception as e:
            logger.error(f"Error in GetEarningsDates for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching earnings dates: {str(e)}")
            return ticker_pb2.GetEarningsDatesResponse()

    def GetHistoryMetadata(self, request, context):
        """Get exchange and instrument metadata for a ticker"""
        try:
            logger.info(f"GetHistoryMetadata called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            meta = ticker.get_history_metadata()
            return ticker_pb2.GetHistoryMetadataResponse(
                currency=safe_str(meta.get('currency')),
                symbol=safe_str(meta.get('symbol')),
                exchange_name=safe_str(meta.get('exchangeName')),
                full_exchange_name=safe_str(meta.get('fullExchangeName')),
                instrument_type=safe_str(meta.get('instrumentType')),
                first_trade_date=safe_int(meta.get('firstTradeDate', 0)),
                regular_market_time=safe_int(meta.get('regularMarketTime', 0)),
                has_pre_post_market_data=bool(meta.get('hasPrePostMarketData', False)),
                gmt_offset=safe_int(meta.get('gmtoffset', 0)),
                timezone=safe_str(meta.get('timezone')),
                exchange_timezone_name=safe_str(meta.get('exchangeTimezoneName')),
                regular_market_price=safe_float(meta.get('regularMarketPrice', 0)),
                fifty_two_week_high=safe_float(meta.get('fiftyTwoWeekHigh', 0)),
                fifty_two_week_low=safe_float(meta.get('fiftyTwoWeekLow', 0)),
                data_granularity=safe_str(meta.get('dataGranularity')),
                range=safe_str(meta.get('range')),
                valid_ranges=list(meta.get('validRanges', [])),
            )
        except Exception as e:
            logger.error(f"Error in GetHistoryMetadata for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching history metadata: {str(e)}")
            return ticker_pb2.GetHistoryMetadataResponse()

    def GetSecFilings(self, request, context):
        """Get SEC filings for a ticker"""
        try:
            logger.info(f"GetSecFilings called for ticker: {request.ticker}")
            ticker = yf.Ticker(request.ticker)
            data = ticker.get_sec_filings()
            filings = []
            if data and isinstance(data, dict):
                for filing in data.get('filings', []):
                    date_val = filing.get('date')
                    ts = None
                    if date_val:
                        try:
                            dt = date_parser.isoparse(str(date_val))
                            ts = Timestamp()
                            ts.FromDatetime(dt)
                        except Exception as e:
                            logger.warning(f"Failed to parse SEC filing date '{date_val}': {e}")
                    sec_filing = ticker_pb2.SecFiling(
                        type=safe_str(filing.get('type')),
                        title=safe_str(filing.get('title')),
                        url=safe_str(filing.get('edgarUrl', filing.get('url', ''))),
                    )
                    if ts:
                        sec_filing.date.CopyFrom(ts)
                    filings.append(sec_filing)
            return ticker_pb2.GetSecFilingsResponse(filings=filings)
        except Exception as e:
            logger.error(f"Error in GetSecFilings for {request.ticker}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching SEC filings: {str(e)}")
            return ticker_pb2.GetSecFilingsResponse()


def serve(port: int = 50051, max_workers: int = 10):
    """Start the gRPC server with reflection enabled"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    ticker_pb2_grpc.add_TickerServiceServicer_to_server(
        TickerServiceServicer(), server
    )
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchServiceServicer(), server)
    market_pb2_grpc.add_MarketServiceServicer_to_server(MarketServiceServicer(), server)
    sector_pb2_grpc.add_SectorServiceServicer_to_server(SectorServiceServicer(), server)

    # Enable reflection for grpcurl and other tools
    SERVICE_NAMES = (
        ticker_pb2.DESCRIPTOR.services_by_name['TickerService'].full_name,
        search_pb2.DESCRIPTOR.services_by_name['SearchService'].full_name,
        market_pb2.DESCRIPTOR.services_by_name['MarketService'].full_name,
        sector_pb2.DESCRIPTOR.services_by_name['SectorService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()
    logger.info(f"Server started on port {port} with reflection enabled")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
