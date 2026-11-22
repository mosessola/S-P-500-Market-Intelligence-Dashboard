# Data-quality assessment

Source file: `data/raw/sp500_stock_prices_cleaned.csv` (preserved unchanged). Audit script: `scripts/01_prepare_data.py` → `docs/data_quality_checks.json`.

## 1. What was found

| Check | Brief (Section 4.4) | Supplied file | Finding |
|---|---|---|---|
| Records | 497,472 | **497,464** | 8 fewer rows than the brief describes |
| Columns | 7 | **8** | extra `data_note` column (text flag, empty for 497,449 rows) |
| Symbols / trading dates | 505 / 1,007 | 505 / 1,007 | match |
| Date coverage | 2014–2017 | 2014-01-02 to 2017-12-29 | match |
| Missing open / high / low | 11 / 8 / 8 | **0 / 0 / 0** | already treated before this file was issued (see `data_note`) |
| Duplicate symbol-date pairs | none | 0 | confirmed |
| Zero-volume rows | 4 | **0** | confirmed absent; smallest volume is 101 shares (BHF, 2017-07-28) |
| Non-positive prices | – | 0 | |
| Row order | – | sorted by date then symbol | **re-sorted by symbol then date** before any calculation |
| Incomplete histories | present | **28 symbols** with fewer than 1,007 dates | listed below |
| OHLC logic violations (high < max(open, close) or low > min) | – | 4 rows | all four carry the note "likely split/spin-off" (CHD, SPG, WRK, LNT) |

**The `data_note` column documents 15 repairs made upstream:** 8 rows "high/low expanded to cover open/close", 3 rows "open filled with prior close", 4 rows "OHLC inconsistent, kept". The repair counts (8, 3 and 4) do not map one-to-one onto the brief's missing-value counts (11 open, 8 high, 8 low), so for this file the `data_note` log is the record of what was changed.

**Unresolved discrepancy.** The file has 8 fewer rows than the brief. The 4 zero-volume rows are absent, which is consistent with their removal, but the other 4 missing rows cannot be identified without the original file. Eight symbols also have gaps *inside* their history (missing dates between their first and last record): DHR 13, O 13, ES 10, ICE 1, REGN 1, VRTX 1, WRK 1, BHF 1 (41 symbol-dates). Returns that span a gap are multi-day returns. Action: request the original file from AnalystLab if exact reconciliation is required; analysis conclusions are not sensitive to 8 of 497,464 rows.

## 2. Incomplete stock histories (28 symbols)

477 symbols have all 1,007 dates. The other 28 either listed late (APTV 18 days from 2017-12-05, DWDP 83, BHF 116, BHGE 126, DXC 189, HLT 250, EVHC 271, FTV 377, UA 437, WLTW 502, CSRA 535, HPE 555, HPQ 555, KHC 629, PYPL 629, WRK 635, QRVO 755, CFG 824, SYF 862, INFO 891, NAVI 934, GOOG 949) or have interior gaps (DHR, O, ES, ICE, REGN, VRTX). **Treatment:** rankings of total return and volatility use only the 477 complete-history symbols so that every stock covers the same period; the dashboard and the symbol summary table still include all 505 and show `records` so users can see coverage. The brief also warns that not all 505 symbols were S&P 500 members for the whole period; no membership data was supplied, so none was assumed.

## 3. Extreme price observations

A daily percentage return was calculated for every symbol (sorted by date, per symbol). Ten observations moved by more than 40% in a day, and every move above 25% (39 rows) was reviewed.

| Type | Rows | Treatment |
|---|---|---|
| Probable corporate actions (splits / spin-offs / special dividend): DISCA, DISCK (2014-08-07), BAX (2015-07-01), NI (2015-07-02), EBAY (2015-07-20), ARNC and YUM (2016-11-01), BHGE (2017-07-05) | 8 | flagged `suspect_return_flag`; excluded from return and volatility statistics |
| Probable bad prints: one-day jump that is almost fully reversed the next day (LNT 2016-05-19/20, and 2017-09-14/15 for FLR, MPC, MRO, NWL) | 10 | flagged both days, excluded |
| Rows with an OHLC-inconsistent note (CHD, SPG, WRK; LNT already counted) | 3 | flagged, excluded |
| Genuine large market moves (e.g. AMD +52% on 2016-04-22, VRTX +40% on 2014-06-24, CHK, WMB) | – | **kept** |

Total flagged: 21 rows (`suspect_return_flag`). The raw return stays in `daily_return_pct`; the cleaned return used for statistics is `return_clean_pct`. The "probable corporate action" labels come from the size and timing of the price break plus analyst knowledge of those events; the dataset itself does not state the cause, so they should be treated as likely, not verified. Limits of this review: corporate actions smaller than 25% (for example SPG, WRK) are not detectable from prices alone and remain in the data.

**Effect on total return.** Total return is calculated by compounding daily returns with flagged days set to 0% (`total_return_pct`); the simple first-to-last-close figure is kept as `total_return_raw_pct`. For stocks with no flagged day the two are identical. For the flagged stocks they differ materially (DISCA −74.9% raw vs −49.1% adjusted). For a spin-off this treatment assumes the value distributed to holders roughly equals the price drop, so it is an approximation, not an exact adjusted-price series.

## 4. Corporate actions and adjusted prices

The file has no adjusted-close column. Some splits appear to be already reflected (AAPL's January 2014 prices are on a post-7-for-1-split basis), but the breaks above show that adjustment is incomplete. All prices are therefore treated as unadjusted for dividends and only partly for splits. **Every return in this project is a price return, not a total shareholder return.** Long-horizon returns for dividend-paying stocks are understated.

## 5. Other limitations

- **Currency:** no currency field; prices are assumed to be US dollars (S&P 500 listings). Not verified from source documentation.
- **Volume** is shares traded, not money value or revenue.
- **Sector information** is not in the file, so no sector analysis was attempted.
- **Historical window:** 2014–2017 only. Nothing here describes current market behaviour or predicts future returns.
