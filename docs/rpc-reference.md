# RPC Reference

Complete mapping of all RPCs to the underlying yfinance methods.

The server exposes four gRPC services:

- **TickerService** — single-ticker data (info, history, financials, options, etc.)
- **SearchService** — full-text search and typed instrument lookup
- **MarketService** — market-level trading status and price summaries
- **SectorService** — sector and industry aggregate data

## Ticker Information

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetInfo` | `ticker.info` | `TickerInfo` | 50+ typed fields covering price, valuation, dividends, financial metrics, targets |
| `GetFastInfo` | `ticker.get_fast_info()` | `FastInfo` | Lightweight snapshot — fewer fields but faster than `GetInfo` |
| `GetMultipleInfo` | `yf.Tickers(...).tickers` | `map<string, TickerInfo>` | One symbol per list entry; symbols that fail are omitted from the map and listed in `missing-tickers` trailing metadata |
| `GetIsin` | `ticker.get_isin()` | `string` | Returns empty string when no ISIN is available |
| `GetHistoryMetadata` | `ticker.get_history_metadata()` | `GetHistoryMetadataResponse` | Exchange name, timezone, first trade date, valid intervals, current market price |

## Price History

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetHistory` | `ticker.history(...)` | `repeated HistoryRow` | Supports `period` or `start`/`end`; all yfinance options (prepost, auto_adjust, repair, etc.) are forwarded |
| `DownloadHistory` | `yf.download(...)` | `stream DownloadHistoryResponse` | Server-streaming; batches of up to 500 rows, one ticker at a time; `NOT_FOUND` if no ticker has data, otherwise symbols without data are listed in `missing-tickers` trailing metadata |

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
| `GetFinancials` | `ticker.get_income_stmt(freq, pretty)` | `repeated FinancialStatement` | Income statement; `freq`: `yearly` (default), `quarterly`, `trailing` |
| `GetBalanceSheet` | `ticker.get_balance_sheet(freq, pretty)` | `repeated BalanceSheetStatement` | `freq`: `yearly` (default), `quarterly` |
| `GetCashFlow` | `ticker.get_cash_flow(freq, pretty)` | `repeated CashFlowStatement` | `freq`: `yearly` (default), `quarterly`, `trailing` |
| `GetEarnings` | — | — | **Deprecated.** Always `UNIMPLEMENTED`: Yahoo Finance no longer serves this data. Use `GetFinancials` (`Net Income`, `Total Revenue`) or `GetEarningsHistory` |

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
| `GetInstitutionalHolders` | `ticker.get_institutional_holders()` | `repeated InstitutionalHolder` | Top institutional holders with shares, value, date reported and `pct_out` (fraction of shares outstanding, 0.05 = 5%) |
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

---

## SearchService

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `Search` | `yf.Search(query, ...)` | `repeated SearchQuote`, `repeated SearchNewsItem` | Full-text search returning matching quotes and news; `max_results` and `news_count` default to 8; optional fuzzy matching |
| `Lookup` | `yf.Lookup(query).get_<type>(count)` | `repeated LookupResult` | Typed instrument lookup; `type` enum filters to equity/etf/index/future/currency/cryptocurrency/mutualfund; `count` defaults to 25 |

---

## MarketService

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetMarketStatus` | `yf.Market(market).status` | `MarketStatus` | Current session type (REGULAR/PRE/POST), open/close timestamps, and timezone; `market` is a Yahoo Finance market ID e.g. `US`; `NOT_FOUND` for an unknown market |
| `GetMarketSummary` | `yf.Market(market).summary` | `map<string, MarketSummaryItem>` | Price snapshot of major instruments keyed by exchange symbol (e.g. `^GSPC`); includes price, change, and change %; `NOT_FOUND` for an unknown market |

---

## SectorService

| RPC | yfinance | Returns | Notes |
|-----|----------|---------|-------|
| `GetSector` | `yf.Sector(key)` | `GetSectorResponse` | Overview, top companies, top ETFs (`map<string,string>`), top mutual funds (`map<string,string>`), and industries list; `key` e.g. `technology`, `financial-services` |
| `GetIndustry` | `yf.Industry(key)` | `GetIndustryResponse` | Overview, top companies, top performing companies (YTD return, last price, target price), and top growth companies (YTD return, growth estimate); `key` e.g. `consumer-electronics` |

---

## Errors

Every RPC reports failures as a gRPC status code. "No data" is not an error: a valid ticker with no dividends returns `OK` with an empty list, and so does an unknown symbol on most single-ticker RPCs, because Yahoo Finance answers it with empty data rather than an error.

| Code | When |
|------|------|
| `INVALID_ARGUMENT` | A required field is empty (`ticker`, `tickers`, `query`, `market`, `key`); a `tickers` entry holds more than one symbol (`"AAPL MSFT"`); yfinance rejects a `period` |
| `NOT_FOUND` | `DownloadHistory` finds no data for any requested ticker; `GetMarketStatus` / `GetMarketSummary` get no data for the market; yfinance reports the ticker missing |
| `RESOURCE_EXHAUSTED` | Yahoo Finance rate-limited the server; retry later |
| `UNIMPLEMENTED` | The deprecated `GetEarnings` RPC |
| `INTERNAL` | Any other failure. The message names the RPC; details stay in the server log |

`GetMultipleInfo` and `DownloadHistory` succeed partially: symbols that returned no data are listed, comma-separated, in the `missing-tickers` trailing metadata.
