# S&P 500 Market Intelligence Dashboard

**AnalystLab Africa Experience Lab · Week 6 · Track A (Data Analytics)**

An interactive dashboard and analysis of 497,464 daily stock records for 505 S&P 500 symbols (2 Jan 2014 to 29 Dec 2017). It answers which stocks returned most, which were most volatile, how trading volume behaved, and how a set of stocks compare, and it documents the data problems found along the way.

> Historical, price-only analysis. Not investment advice and not a forecast.

## Dashboard

| Market Overview | Price Performance |
|---|---|
| ![Market Overview](screenshots/dashboard_page_overview.png) | ![Price Performance](screenshots/dashboard_page_price.png) |
| **Returns & Volatility** | **Trading Volume** |
| ![Returns and Volatility](screenshots/dashboard_page_returns.png) | ![Trading Volume](screenshots/dashboard_page_volume.png) |

Filters on every page: stock symbols (up to 6 compared at once), date range, and moving-average window (5, 10, 20 or 50 days).

## Key findings

- An equal-weight index of all symbols grew from 100 to 154.7 (+54.7%). Calendar-year moves: +16.9% (2014), −1.1% (2015), +14.0% (2016), +17.4% (2017). The deepest drawdown was −16.4%, bottoming on 11 Feb 2016.
- Among the 477 stocks with a full history, the median price return was +47.6% and 80.5% finished higher. NVDA rose 1,120%; CHK fell 85.1%.
- The highest share prices (PCLN, AMZN, GOOGL) were not the best performers, so price level says little about performance.
- Higher volatility was weakly associated with lower return (Spearman −0.21). Most volatile: CHK (72.3% annualised), AMD, FCX.
- Volume tracks the size of a price move (rank correlation 0.44 to 0.51 with absolute return), not its direction (about 0 with signed return). BAC was the most heavily traded stock.
- Daily-return correlations among AAPL, MSFT, AMZN, JPM, XOM and JNJ ranged from 0.23 to 0.50.

Full write-up with recommendations: [`docs/executive_summary.md`](docs/executive_summary.md).

## Data quality

The supplied file differs from the assignment brief, and this is documented in full in [`docs/data_quality_assessment.md`](docs/data_quality_assessment.md).

| Item | Finding |
|---|---|
| Rows | 497,464 (brief: 497,472); cause of the 8-row difference is not documented |
| Missing values / zero volume | none (brief reports some); an upstream `data_note` column logs 15 repairs |
| Incomplete histories | 28 symbols; rankings use the 477 complete ones |
| Flagged returns | 21 probable splits, spin-offs or bad prints, excluded from return and volatility statistics (raw return kept) |
| Adjustment | no adjusted close; returns are price-only, prices assumed USD |

## Validation

[`validation/03_validate_dashboard.py`](validation/03_validate_dashboard.py) recalculates dashboard numbers from the raw CSV using only the `csv` module and NumPy, then compares them with the dashboard's figure builders. 14 of 14 checks pass (record counts, daily return, moving averages, filters, volatility, average volume, total return). Results: [`validation/validation_evidence.md`](validation/validation_evidence.md).

## Project structure

```
├── data/raw/                  original CSV, unchanged
├── data/processed/            prepared dataset (created by script 01)
├── scripts/
│   ├── 01_prepare_data.py     inspection audit, sorting, engineered fields, flags
│   ├── 02_analysis_and_charts.py   analysis tables and 9 charts
│   ├── 03_insight_stats.py    headline numbers for the summary
│   └── viz_style.py           shared chart style and colour palette
├── notebooks/SP500_Data_Analytics.ipynb   executed end-to-end notebook
├── dashboard/app.py           4-page Plotly Dash app
├── visualisations/            9 charts (PNG + interactive HTML)
├── screenshots/               one screenshot per dashboard page
├── validation/                validation script and evidence
└── docs/                      data-quality assessment, KPI definitions,
                               business problem and success criteria,
                               executive summary, analysis tables
```

## How to run

Requires Python 3.10+ and Chrome (Kaleido uses it to export chart images).

```bash
pip install pandas numpy pyarrow plotly kaleido dash scipy nbformat nbconvert ipykernel

# place the original sp500_stock_prices_cleaned.csv in data/raw/
python scripts/01_prepare_data.py
python scripts/02_analysis_and_charts.py
python scripts/03_insight_stats.py
python validation/03_validate_dashboard.py   # exits non-zero if any check fails
python dashboard/app.py                      # open http://127.0.0.1:8050
```

Dashboard pages: `/overview`, `/price`, `/returns`, `/volume`.

## Method

1. Sort by symbol, then date; every calculation is grouped by symbol.
2. Engineer year, month, quarter, daily price change, daily % return, daily range, intraday return and 5/10/20/50-day moving averages.
3. Flag and exclude probable corporate-action and bad-print returns from statistics.
4. Annualised volatility = standard deviation of daily returns × √252. Total return compounds daily returns with flagged days at 0%.
5. Rank over the 477 complete-history symbols; compare AAPL, MSFT, AMZN, JPM, XOM and JNJ in detail (all have 1,007 dates and span technology, retail, banking, energy and healthcare).

KPI formulas: [`docs/KPI_definitions.md`](docs/KPI_definitions.md).

## Limitations

- Price-only returns; dividends are excluded, which understates returns for dividend payers.
- Corporate-action adjustment is incomplete and the flagged causes are inferred from price breaks, not stated in the data.
- Currency assumed to be USD; no sector data in the file.
- Not every symbol was in the index for the whole period.
- 2014 to 2017 only; results do not describe current markets.

## Tools

Python, pandas, NumPy, Plotly, Dash, Kaleido, Jupyter. Chart colours were checked for colour-blind separation. Claude (Anthropic) assisted with code and documentation; all outputs were run and validated as described above.
