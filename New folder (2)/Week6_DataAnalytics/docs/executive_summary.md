# Executive summary: S&P 500 historical performance, 2014–2017

*AnalystLab Africa, Week 6, Track A (Data Analytics). Historical, price-only analysis of 505 symbols and 497,464 daily records. Nothing here is investment advice or a forecast.*

## Findings

1. **The market rose, with one sharp setback.** An equal-weight index of all symbols grew from 100 to 154.7 (+54.7%). Calendar-year moves were +16.9% (2014), −1.1% (2015), +14.0% (2016) and +17.4% (2017). The deepest fall from a peak was −16.4%, bottoming on 11 February 2016.
2. **Individual outcomes varied enormously.** Among the 477 stocks with a complete history the median price return was +47.6% and 80.5% finished higher, yet NVDA rose 1,120% (15.86 to 193.50) while CHK fell 85.1% (26.62 to 3.96).
3. **Share price tells you nothing about performance.** The five highest closing prices were PCLN ($2,049.00 on 8 Aug 2017), AMZN ($1,195.83), GOOGL, GOOG and AZO; none of them is in the top ten by return. The lowest close in the file was CHK at $1.59 on 12 Feb 2016.
4. **Volatility did not buy return.** The median stock had annualised volatility of 22.7%. The most volatile were CHK (72.3%), AMD (62.1%) and FCX (58.7%). Across stocks, higher volatility was weakly associated with *lower* return over this period (Spearman −0.21). Of the six compared stocks, JNJ was calmest (14.1%) and AMZN the most volatile (29.6%).
5. **Trading volume is concentrated and follows the size of a move, not its direction.** BAC averaged 89.4 million shares a day, twice AAPL's 45.2 million; the ten busiest symbols account for 18.3% of all shares traded. For the six compared stocks, volume had almost no rank correlation with the signed daily return (−0.04 to +0.01) but a clear one with the absolute return (0.44 to 0.51).
6. **Diversification was available.** Daily-return correlations among AAPL, MSFT, AMZN, JPM, XOM and JNJ ranged from 0.23 (AMZN–XOM) to 0.50 (JPM–XOM); none was above 0.5.
7. **The data needs care.** 21 daily returns are corporate-action effects or bad prints (for example DISCA's one-day −50.6% is a split, not a loss). Left in, they would have put DISCA and DISCK in the bottom ten stocks (−75%); adjusted, they are about −49%.

## Recommendations

| # | Recommendation | Evidence | How stakeholders can use it |
|---|---|---|---|
| 1 | Compare stocks on percentage return and volatility, never on price level | Finding 3 (top-price stocks absent from top-return list); Finding 2 | Make return/volatility the default sort in research screens and reports |
| 2 | Use volume as an activity and liquidity indicator and as a companion to volatility, not as a directional signal | Finding 5 (signed correlation ≈ 0; absolute-return correlation 0.44–0.51) | Flag unusually high-volume days for review; do not treat high volume as bullish or bearish |
| 3 | Look for combinations of low volatility and moderate correlation when describing risk | Findings 4 and 6 | Use the correlation matrix and risk-return chart to shortlist names for deeper research on risk grounds |
| 4 | Add adjusted prices and a corporate-actions table before the data is reused | Finding 7; 8 probable corporate actions, 10 probable bad prints, no adjusted close | Request an adjusted source from the data owner; until then keep the `suspect_return_flag` column in every analysis |

## Limits to keep in mind

Price returns exclude dividends. Prices are assumed to be US dollars. 28 symbols do not have a full history and are left out of the rankings. The file has 8 fewer rows than the assignment brief describes and the cause is not documented. Past performance in 2014–2017 does not indicate future returns. Details are in `docs/data_quality_assessment.md`.
