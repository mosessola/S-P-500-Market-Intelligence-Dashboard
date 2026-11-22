# Validation evidence (Task 6)

Method: dashboard figure builders (`dashboard/app.py`) were called with fixed inputs and compared with an independent recalculation from the raw CSV using only the `csv` module and NumPy. Script: `validation/03_validate_dashboard.py`.

| Check | Result | Detail |
|---|---|---|
| V1a record count | PASS | csv rows 497,464 vs dashboard 497,464 |
| V1b symbol count | PASS | 505 symbols |
| V1c total shares traded | PASS | 2,116,051,738,554 |
| V1d KPI average close (selected) | PASS | $176.34 vs $176.34 |
| V2 daily return formula | PASS | max abs difference across 6 stocks x 1,006 days = 0.00e+00 percentage points |
| V3 20-day moving average | PASS | max abs difference 4.55e-13; first 19 values blank (no look-ahead, no zero fill) |
| V3 5-day moving average | PASS | max abs difference 2.27e-13; first 4 values blank (no look-ahead, no zero fill) |
| V4a symbol filter | PASS | traces ['JPM', 'MSFT'] |
| V4b date filter | PASS | 504 points, 2016-01-04..2016-12-30, expected 504 |
| V4c six-series cap | PASS | 9 symbols selected -> 6 plotted |
| V4d empty selection safe | PASS | no traces, message shown instead of error |
| V5a rolling 30-day volatility | PASS | XOM last value 8.3487 vs manual 8.3487 |
| V5b average volume | PASS | max abs difference 0.00e+00 million shares |
| V6 total return | PASS | max abs difference 0.0000 percentage points (stocks without flagged days) |

Interior gaps found (symbol: missing trading dates between first and last record): {'DHR': 13, 'ES': 10, 'ICE': 1, 'O': 13, 'REGN': 1, 'VRTX': 1, 'WRK': 1, 'BHF': 1}