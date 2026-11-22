# KPI definition sheet

All calculations are per symbol, on rows sorted by date. `return_clean_pct` is the daily return with the 21 flagged corporate-action / bad-print rows blanked (see `data_quality_assessment.md`).

| # | KPI | Definition / formula | Unit | Source fields | Where shown | Validated by |
|---|---|---|---|---|---|---|
| 1 | Stock symbols | count of distinct `symbol` | count | symbol | Page 1 | V1b |
| 2 | Trading records | count of rows | count | all | Page 1 | V1a |
| 3 | Date range | min and max `date` | date | date | Page 1 | V1 |
| 4 | Average closing price | mean of `close` over selected symbols and dates | USD (assumed) | close | Page 1 | V1d |
| 5 | Daily price change | `close(t) − close(t−1)` | USD | close | table / Q7 | V2 |
| 6 | Daily percentage return | `(close(t) / close(t−1) − 1) × 100` | % | close | Page 3 | V2 |
| 7 | Daily trading range | `high − low` | USD | high, low | Page 2 | – |
| 8 | Moving average (n) | mean of the last n closes, n ∈ {5, 10, 20, 50}; blank until n observations exist | USD | close | Page 2 | V3 |
| 9 | Mean daily return | mean of `return_clean_pct` | % | close | Page 3 | – |
| 10 | Daily volatility | sample standard deviation (ddof = 1) of `return_clean_pct` | % | close | Page 3 | V5a |
| 11 | Annualised volatility | daily volatility × √252 | % | close | Page 3 / rankings | V5a |
| 12 | Rolling 30-day volatility | 30-day rolling std of returns × √252 | % | close | Page 3 | V5a |
| 13 | Total price return | product of (1 + daily clean return) − 1 over the period; equals last/first close − 1 when no row is flagged | % | close | rankings | V6 |
| 14 | Average daily volume | mean of `volume` | shares | volume | Page 4 | V5b |
| 15 | Highest / lowest volume | max and min `volume` with date | shares | volume | Page 4 table | – |
| 16 | Volume–return relationship | Spearman rank correlation of `volume` with (a) daily return, (b) absolute daily return; flagged rows excluded | −1…1 | volume, close | Page 4 table | – |
| 17 | Return correlation | Pearson correlation of daily returns between two stocks | −1…1 | close | Notebook / chart 06 | – |

Spearman was chosen for volume because volume is highly skewed. Annualisation uses 252 trading days. "Selected stocks" for the comparison are AAPL, MSFT, AMZN, JPM, XOM and JNJ, chosen because they have all 1,007 trading dates and cover technology, retail, banking, energy and healthcare.
