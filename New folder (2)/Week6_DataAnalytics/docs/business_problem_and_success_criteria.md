# Business problem and success criteria (common Tasks 1 and 3)

**Problem.** A simulated financial research team needs a way to inspect 505 stock symbols over four years of daily data without hand-building charts for each one. The questions are: which stocks returned most, which were most volatile, how trading volume behaved, and how the stocks compare. Raw price alone is misleading ($2,049 for PCLN says nothing about performance), so the work is built on percentage returns and volatility.

**Why it matters.** Analysts use historical comparisons to frame research and risk discussions. Errors in the data (splits and spin-offs shown as 50% crashes) would mislead those discussions, so data checks are part of the deliverable.

**Intended users.** Financial researchers and market analysts. **Decisions supported:** which stocks deserve closer research, how to describe risk and liquidity, which data needs fixing before wider use. **Not supported:** investment recommendations or forecasts.

**Limitations.** Historical (2014–2017) price-only data, unadjusted for dividends and incompletely for corporate actions, currency assumed USD, 28 symbols with incomplete histories. See `data_quality_assessment.md`.

## Success criteria and results

| # | Measurable criterion | Result |
|---|---|---|
| 1 | At least 3 headline calculations reconcile with an independent recalculation | 14 of 14 checks pass (`validation/validation_evidence.md`) |
| 2 | Dashboard has the 4 required pages, stock and date filters work, filters return only the selected data | all 4 pages built; V4a–V4d pass |
| 3 | At least 5 analysis questions answered, at least 5 stocks compared, at least 5 visualisations | 7 questions, 6 stocks, 9 charts |
| 4 | Every data-quality issue found is documented with its treatment | 28 incomplete histories, 21 flagged returns, 8-row shortfall, unadjusted prices all documented |
| 5 | Findings state historical, price-only scope and make no forecasts | stated on the dashboard header and in the executive summary |
