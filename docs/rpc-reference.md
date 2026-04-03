# RPC Reference

Complete mapping of every `TickerService` RPC to the underlying yfinance method.

## Ticker Information

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetInfo` | `ticker.info` | `TickerInfo` | 50+ typed fields covering price, valuation, dividends, financial metrics, targets |
| `GetFastInfo` | `ticker.get_fast_info()` | `FastInfo` | Lightweight snapshot — fewer fields but faster than `GetInfo` |
| `GetMultipleInfo` | `yf.Tickers(...).tickers` | `map<string, TickerInfo>` | Fetches info for all requested tickers; failures on individual tickers are logged and skipped |
| `GetIsin` | `ticker.get_isin()` | `string` | Returns empty string when no ISIN is available |
| `GetHistoryMetadata` | `ticker.get_history_metadata()` | `GetHistoryMetadataResponse` | Exchange name, timezone, first trade date, valid intervals, current market price |

## Price History

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetHistory` | `ticker.history(...)` | `repeated HistoryRow` | Supports `period` or `start`/`end`; all yfinance options (prepost, auto_adjust, repair, etc.) are forwarded |
| `DownloadHistory` | `yf.download(...)` | `stream DownloadHistoryResponse` | Server-streaming; yields batches of 500 rows per ticker; uses threading internally |

## Corporate Actions

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetDividends` | `ticker.get_dividends(period)` | `repeated DividendRow` | Defaults to `period="max"` |
| `GetSplits` | `ticker.get_splits(period)` | `repeated SplitRow` | Defaults to `period="max"` |
| `GetCapitalGains` | `ticker.get_capital_gains(period)` | `repeated CapitalGainsRow` | Primarily relevant for ETFs and mutual funds; defaults to `period="max"` |
| `GetActions` | `ticker.get_actions(period)` | `repeated ActionRow` | Combined dividends + splits + capital gains; defaults to `period="max"` |

## Financial Statements

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetFinancials` | `ticker.get_financials(freq, pretty)` | `repeated FinancialStatement` | Income statement; `freq`: `yearly` (default), `quarterly`, `trailing` |
| `GetBalanceSheet` | `ticker.get_balance_sheet(freq, pretty)` | `repeated BalanceSheetStatement` | `freq`: `yearly` (default), `quarterly` |
| `GetCashFlow` | `ticker.get_cash_flow(freq, pretty)` | `repeated CashFlowStatement` | `freq`: `yearly` (default), `quarterly`, `trailing` |
| `GetEarnings` | `ticker.get_earnings(freq)` | `repeated EarningsRow` | Revenue and EPS per period; `freq`: `yearly` (default), `quarterly`, `trailing` |

## Analyst Data & Estimates

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetRecommendations` | `ticker.upgrades_downgrades` | `repeated RecommendationRow` | Individual analyst actions (firm, from/to grade, action); sorted newest first |
| `GetRecommendationsSummary` | `ticker.get_recommendations()` | `repeated RecommendationSummaryRow` | Aggregated counts per period (0m, -1m, …); distinct from `GetRecommendations` |
| `GetAnalystPriceTargets` | `ticker.get_analyst_price_targets()` | `GetAnalystPriceTargetsResponse` | Consensus current/low/high/mean/median price targets |
| `GetEarningsEstimate` | `ticker.get_earnings_estimate()` | `repeated EarningsEstimateRow` | Forward EPS estimates for 0q/+1q/0y/+1y with analyst count and growth |
| `GetRevenueEstimate` | `ticker.get_revenue_estimate()` | `repeated RevenueEstimateRow` | Forward revenue estimates; same period structure as `GetEarningsEstimate` |
| `GetEarningsHistory` | `ticker.get_earnings_history()` | `repeated EarningsHistoryRow` | Historical EPS estimate vs actual with surprise % |
| `GetEpsTrend` | `ticker.get_eps_trend()` | `repeated EpsTrendRow` | EPS consensus estimate across 7/30/60/90-day revision windows per period |
| `GetEpsRevisions` | `ticker.get_eps_revisions()` | `repeated EpsRevisionsRow` | Up/down revision counts over the last 7 and 30 days per period |
| `GetGrowthEstimates` | `ticker.get_growth_estimates()` | `repeated GrowthEstimatesRow` | Growth estimates for stock, industry, sector and index across 0q/+1q/0y/+1y/+5y/-5y |

## Calendar & Events

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetCalendar` | `ticker.get_calendar()` | `GetCalendarResponse` | Next earnings date window (start/end) and next ex-dividend date |
| `GetEarningsDates` | `ticker.get_earnings_dates(limit)` | `repeated EarningsDateRow` | Past and upcoming earnings dates; optional EPS fields are omitted when not yet reported; defaults to 12 dates |

## Options

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetOptions` | `ticker.options` | `repeated string` | List of available expiration dates in `YYYY-MM-DD` format |
| `GetOptionChain` | `ticker.option_chain(date, tz)` | `GetOptionChainResponse` | Full calls and puts for a given expiration; `date` defaults to nearest expiry |

## Ownership

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetMajorHolders` | `ticker.get_major_holders(as_dict=True)` | `map<string, string>` | Percentage breakdown (insiders held, institutions held, float held, etc.) |
| `GetInstitutionalHolders` | `ticker.get_institutional_holders()` | `repeated InstitutionalHolder` | Top institutional holders with shares, value, % outstanding, date reported |
| `GetMutualFundHolders` | `ticker.get_mutualfund_holders()` | `repeated MutualFundHolder` | Top mutual fund holders; same fields as `GetInstitutionalHolders` |
| `GetInsiderPurchases` | `ticker.get_insider_purchases()` | `repeated InsiderPurchaseSummaryRow` | Summary table of insider activity; each row has a label and a `map<string,string>` of column values |
| `GetInsiderTransactions` | `ticker.get_insider_transactions()` | `repeated InsiderTransaction` | Individual insider transactions with insider name, position, shares, value, and SEC URL |
| `GetInsiderRosterHolders` | `ticker.get_insider_roster_holders()` | `repeated InsiderRosterHolder` | Current insider roster with name, position, most recent transaction date and share count |

## ESG & Filings

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetSustainability` | `ticker.get_sustainability(as_dict=True)` | `GetSustainabilityResponse` | Total ESG score, environment/social/governance sub-scores, percentile, peer group, and 15 controversy boolean flags (coal, tobacco, weapons, etc.); returns empty response when no ESG data is available |
| `GetSecFilings` | `ticker.get_sec_filings()` | `repeated SecFiling` | SEC filing history with date, type (10-K, 10-Q, 8-K, …), title and EDGAR URL |

## Shares

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetSharesHistory` | `ticker.get_shares_full(start, end)` | `repeated SharesHistoryRow` | Full history of shares outstanding; optional `start`/`end` timestamps to filter range |

## News

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetNews` | `ticker.news` | `repeated NewsArticle` | Recent news articles with title, publisher, link, publish time, content type, and thumbnail URL; `count` defaults to 10 |
