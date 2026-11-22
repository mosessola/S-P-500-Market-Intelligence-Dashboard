# Week 6 – Track A (Data Analytics): S&P 500 Stock Market Performance and Business Intelligence Dashboard

AnalystLab Africa Experience Lab, Week 6. Rename this folder to `Week 6 – <Your Full Name> – Data Analytics` before submitting.

## What is in the folder

| Path | Contents |
|---|---|
| `notebooks/SP500_Data_Analytics.ipynb` | Executed notebook: inspection, cleaning, analysis, comparison, charts, validation |
| `scripts/01_prepare_data.py` | Inspection audit, sorting, engineered fields, flags → `data/processed/sp500_prepared.parquet` |
| `scripts/02_analysis_and_charts.py` | Task 3 and 4 tables (`docs/tables/`) and 9 charts (`visualisations/`, PNG + interactive HTML) |
| `scripts/03_insight_stats.py` | Headline numbers used in the executive summary |
| `scripts/viz_style.py` | Shared chart style and the colour palette |
| `dashboard/app.py` | 4-page interactive Plotly Dash dashboard |
| `validation/` | `03_validate_dashboard.py`, `validation_evidence.md`, `validation_results.json` |
| `screenshots/` | One screenshot per dashboard page |
| `docs/` | Data-quality assessment, KPI definition sheet, business problem and success criteria, executive summary |
| `data/raw/` | The original CSV, unchanged |

## How to reproduce

The submission zip leaves out the two large data files to stay small. Copy the original `sp500_stock_prices_cleaned.csv` into `data/raw/` first; step 1 below recreates `data/processed/sp500_prepared.parquet`.

```bash
pip install pandas numpy pyarrow plotly kaleido dash scipy nbformat nbconvert ipykernel
python scripts/01_prepare_data.py
python scripts/02_analysis_and_charts.py     # charts export PNG through Kaleido, which needs Chrome installed
python scripts/03_insight_stats.py
python validation/03_validate_dashboard.py   # exits non-zero if any check fails
python dashboard/app.py                      # open http://127.0.0.1:8050
```

Dashboard pages: `/overview`, `/price`, `/returns`, `/volume`. Filters (top of every page): stock symbols (up to 6 are compared at once), date range, moving-average window (5, 10, 20 or 50).

## Method in brief

1. Data sorted by symbol then date; all calculations are grouped by symbol.
2. Added year, month, quarter, daily price change, daily % return, daily range, intraday return, and 5/10/20/50-day moving averages.
3. 21 returns that are probable splits, spin-offs, special dividends or bad prints are flagged and excluded from return and volatility statistics (raw return retained).
4. Rankings use the 477 symbols with all 1,007 dates. Six stocks (AAPL, MSFT, AMZN, JPM, XOM, JNJ) are compared in detail.
5. Total return compounds daily returns with flagged days at 0%.

## Assumptions and limitations

Price-only returns (no dividends); prices assumed USD; adjustment for corporate actions is incomplete; the supplied file has 8 fewer rows than the brief states; historical results do not predict future performance. Full detail in `docs/data_quality_assessment.md`.

## Tools

Python, pandas, NumPy, Plotly, Dash, Kaleido, Jupyter. Charts follow a palette checked for colour-blind separation. Claude (Anthropic) was used to help write the code and documents; all outputs were run and validated as described in `validation/`.
