"""Week 6 - Track A: analysis tables (Task 3/4) and static visualisations.
Run from project root after 01_prepare_data.py:  python scripts/02_analysis_and_charts.py
Outputs: docs/tables/*.csv, visualisations/*.png (+ .html for interactive copies)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
sys.path.insert(0, str(Path(__file__).parent))
from viz_style import *   # noqa

ROOT = Path(__file__).resolve().parents[1]
TAB, VIZ = ROOT / "docs/tables", ROOT / "visualisations"
TAB.mkdir(parents=True, exist_ok=True); VIZ.mkdir(exist_ok=True)
df = pd.read_parquet(ROOT / "data/processed/sp500_prepared.parquet")
N_DATES = df.date.nunique()

def save(fig, name, w=1100, h=620):
    fig.write_image(VIZ / f"{name}.png", width=w, height=h, scale=2)
    fig.write_html(VIZ / f"{name}.html", include_plotlyjs="cdn")

# ---------------- symbol-level summary (one row per symbol) ----------------
g = df.groupby("symbol")
s = pd.DataFrame({
    "records": g.size(), "first_date": g.date.min(), "last_date": g.date.max(),
    "first_close": g.close.first(), "last_close": g.close.last(),
    "mean_close": g.close.mean(), "median_close": g.close.median(),
    "max_close": g.close.max(), "min_close": g.close.min(),
    "mean_daily_return_pct": g.return_clean_pct.mean(),
    "daily_vol_pct": g.return_clean_pct.std(),
    "avg_volume": g.volume.mean(), "max_volume": g.volume.max(), "min_volume": g.volume.min(),
    "avg_daily_range": g.daily_range.mean(),
    "n_suspect_returns": g.suspect_return_flag.sum()})
s["max_close_date"] = df.loc[g.close.idxmax(), ["symbol", "date"]].set_index("symbol").date
s["min_close_date"] = df.loc[g.close.idxmin(), ["symbol", "date"]].set_index("symbol").date
s["total_return_raw_pct"] = (s.last_close / s.first_close - 1) * 100
# Adjusted total return: chain daily returns with flagged corporate-action/bad-print days set to 0%.
s["total_return_pct"] = (g.return_clean_pct.apply(lambda r: (1 + r.fillna(0) / 100).prod()) - 1) * 100
s["annualised_vol_pct"] = s.daily_vol_pct * np.sqrt(252)
s["complete_history"] = s.records == N_DATES
s["selected"] = s.index.isin(SELECTED)
s.round(4).to_csv(TAB / "symbol_summary_all_505.csv")
full = s[s.complete_history]          # fair comparison set: all 1,007 dates present

# ---------------- Task 3 questions ----------------
cols = ["max_close", "max_close_date"]
s.nlargest(10, "max_close")[cols].to_csv(TAB / "q1_highest_closing_prices.csv")
s.nsmallest(10, "min_close")[["min_close", "min_close_date"]].to_csv(TAB / "q1_lowest_closing_prices.csv")
rc = ["total_return_pct", "total_return_raw_pct", "first_close", "last_close", "n_suspect_returns"]
full.nlargest(10, "total_return_pct")[rc].to_csv(TAB / "q2_top10_total_return.csv")
full.nsmallest(10, "total_return_pct")[rc].to_csv(TAB / "q2_bottom10_total_return.csv")
full.nlargest(10, "annualised_vol_pct")[["annualised_vol_pct", "mean_daily_return_pct"]].to_csv(TAB / "q3_most_volatile.csv")
full.nsmallest(10, "annualised_vol_pct")[["annualised_vol_pct", "mean_daily_return_pct"]].to_csv(TAB / "q3_least_volatile.csv")
s.nlargest(10, "avg_volume")[["avg_volume", "max_volume"]].to_csv(TAB / "q4_highest_avg_volume.csv")
valid = df[~df.suspect_return_flag & df.daily_return_pct.notna()]
cols7 = ["symbol", "date", "close", "daily_change", "daily_return_pct"]
valid.nlargest(10, "daily_return_pct")[cols7].to_csv(TAB / "q7_largest_daily_gains.csv", index=False)
valid.nsmallest(10, "daily_return_pct")[cols7].to_csv(TAB / "q7_largest_daily_losses.csv", index=False)
df[df.daily_return_pct.abs() > 40][cols7 + ["suspect_return_flag"]].to_csv(TAB / "q7_extreme_moves_reviewed.csv", index=False)

# Q6 monthly / yearly pattern: equal-weight market daily return, compounded
mkt = df.groupby("date").return_clean_pct.mean().div(100)
mkt_month = (1 + mkt).groupby([mkt.index.year, mkt.index.month]).prod().sub(1).mul(100)
mkt_month.index.names = ["year", "month"]
mkt_month.rename("equal_weight_return_pct").round(3).to_csv(TAB / "q6_market_monthly_return.csv")
yr = (df[df.symbol.isin(SELECTED)].pivot(index="date", columns="symbol", values="return_clean_pct").div(100))
yearly = (1 + yr).groupby(yr.index.year).prod().sub(1).mul(100)[SELECTED]
yearly.round(2).to_csv(TAB / "q6_selected_yearly_return.csv")

# ---------------- Task 4 comparative table (selected 6) ----------------
cmp = s.loc[SELECTED, ["mean_close", "median_close", "min_close", "min_close_date", "max_close", "max_close_date",
                       "total_return_pct", "total_return_raw_pct", "mean_daily_return_pct", "daily_vol_pct", "annualised_vol_pct",
                       "avg_volume", "max_volume", "min_volume"]]
cmp.round(3).to_csv(TAB / "task4_selected_comparison.csv")
wide = df[df.symbol.isin(SELECTED)].pivot(index="date", columns="symbol", values="return_clean_pct")[SELECTED]
corr = wide.corr(); corr.round(3).to_csv(TAB / "task4_return_correlation.csv")
vol_ret_corr = {sym: df[(df.symbol == sym) & ~df.suspect_return_flag][["volume", "return_clean_pct"]].corr(method="spearman").iloc[0, 1]
                for sym in SELECTED}
pd.Series(vol_ret_corr, name="spearman_volume_vs_return").round(3).to_csv(TAB / "task4_volume_return_corr.csv")
absr = {sym: df[(df.symbol == sym) & ~df.suspect_return_flag].assign(a=lambda x: x.return_clean_pct.abs())[["volume", "a"]].corr(method="spearman").iloc[0, 1]
        for sym in SELECTED}
pd.Series(absr, name="spearman_volume_vs_abs_return").round(3).to_csv(TAB / "task4_volume_absreturn_corr.csv")

# ---------------- Visualisations ----------------
sel = df[df.symbol.isin(SELECTED)]
# 1 normalised price
fig = go.Figure()
for sym in SELECTED:
    d = sel[sel.symbol == sym]
    fig.add_scatter(x=d.date, y=d.close / d.close.iloc[0] * 100, name=sym, mode="lines",
                    line=dict(color=COLOR[sym], width=2), hovertemplate="%{y:.1f}")
fig.update_layout(title="Growth of 100 invested at first close (Jan 2014 = 100)", yaxis_title="Indexed closing price")
save(fig, "01_indexed_price_selected")

# 2 top / bottom total return
tb = pd.concat([full.nlargest(10, "total_return_pct"), full.nsmallest(10, "total_return_pct")]).sort_values("total_return_pct")
fig = go.Figure(go.Bar(x=tb.total_return_pct, y=tb.index, orientation="h",
                       marker=dict(color=[SERIES[0] if v > 0 else SERIES[1] for v in tb.total_return_pct]),
                       hovertemplate="%{y}: %{x:.0f}%<extra></extra>"))
fig.update_layout(title="Highest and lowest total price return, Jan 2014 to Dec 2017 (full-history stocks)",
                  xaxis_title="Total price return (%)", hovermode="closest", height=700)
save(fig, "02_top_bottom_total_return", h=760)

# 3 risk vs return
fig = go.Figure()
others = full[~full.selected]
fig.add_scatter(x=others.annualised_vol_pct, y=others.total_return_pct, mode="markers", name="Other full-history stocks",
                marker=dict(color="#b9b8b2", size=6, opacity=.7), text=others.index,
                hovertemplate="%{text}<br>vol %{x:.1f}% | return %{y:.0f}%<extra></extra>")
for sym in SELECTED:
    fig.add_scatter(x=[s.loc[sym, "annualised_vol_pct"]], y=[s.loc[sym, "total_return_pct"]], mode="markers+text", name=sym,
                    text=[sym], textposition="top center", marker=dict(color=COLOR[sym], size=13, line=dict(color=SURFACE, width=2)),
                    hovertemplate=f"{sym}<br>vol %{{x:.1f}}% | return %{{y:.0f}}%<extra></extra>")
fig.update_layout(title="Risk vs return: annualised volatility against total return", hovermode="closest",
                  xaxis_title="Annualised volatility of daily returns (%)", yaxis_title="Total price return 2014-2017 (%)")
save(fig, "03_risk_vs_return")

# 4 return distribution
fig = go.Figure()
for sym in SELECTED:
    r = sel[sel.symbol == sym].return_clean_pct.dropna()
    fig.add_histogram(x=r, name=sym, opacity=.55, xbins=dict(start=-8, end=8, size=.4), marker_color=COLOR[sym], histnorm="probability")
fig.update_layout(barmode="overlay", title="Distribution of daily percentage returns (selected stocks)",
                  xaxis_title="Daily return (%)", yaxis_title="Share of trading days", hovermode="closest")
save(fig, "04_return_distribution")

# 5 average volume
v = s.loc[SELECTED, "avg_volume"].sort_values()
fig = go.Figure(go.Bar(x=v.values / 1e6, y=v.index, orientation="h", marker_color=[COLOR[i] for i in v.index],
                       hovertemplate="%{y}: %{x:.1f}M shares/day<extra></extra>"))
fig.update_layout(title="Average daily trading volume (millions of shares)", xaxis_title="Shares traded per day (millions)", hovermode="closest")
save(fig, "05_average_volume", h=480)

# 6 correlation heatmap
fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale=SEQ_BLUE, zmin=0, zmax=1,
                           text=corr.round(2).values, texttemplate="%{text}", hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>"))
fig.update_layout(title="Correlation of daily returns, selected stocks", hovermode="closest", yaxis_autorange="reversed")
save(fig, "06_return_correlation", w=800, h=640)

# 7 yearly return grouped bars
fig = go.Figure()
for sym in SELECTED:
    fig.add_bar(x=yearly.index.astype(str), y=yearly[sym], name=sym, marker_color=COLOR[sym], hovertemplate="%{y:.1f}%")
fig.update_layout(barmode="group", title="Calendar-year price return by stock", yaxis_title="Return (%)", bargap=.25)
save(fig, "07_yearly_returns")

# 8 moving averages (AAPL)
d = df[df.symbol == "AAPL"]
fig = go.Figure()
fig.add_scatter(x=d.date, y=d.close, name="Close", line=dict(color="#b9b8b2", width=1.5))
for col, c in [("ma_20", SERIES[1]), ("ma_50", SERIES[0])]:
    fig.add_scatter(x=d.date, y=d[col], name=col.replace("ma_", "") + "-day MA", line=dict(color=c, width=2.5))
fig.update_layout(title="AAPL closing price with 20- and 50-day moving averages", yaxis_title="Price (USD assumed)")
save(fig, "08_moving_averages_aapl")

# 9 volatility rolling (selected)
fig = go.Figure()
for sym in SELECTED:
    d = sel[sel.symbol == sym].set_index("date").return_clean_pct.rolling(30).std() * np.sqrt(252)
    fig.add_scatter(x=d.index, y=d, name=sym, line=dict(color=COLOR[sym], width=2))
fig.update_layout(title="Rolling 30-day annualised volatility", yaxis_title="Annualised volatility (%)")
save(fig, "09_rolling_volatility")
print("done"); print(cmp.round(2).to_string()); print(corr.round(2)); print(pd.Series(vol_ret_corr).round(3)); print(pd.Series(absr).round(3))
for f in ["q1_highest_closing_prices","q2_top10_total_return","q2_bottom10_total_return","q3_most_volatile","q4_highest_avg_volume","q7_largest_daily_gains","q7_largest_daily_losses"]:
    print(f); print(pd.read_csv(TAB/f"{f}.csv").round(2).to_string(index=False))
print(yearly.round(1)); print(len(full), "full-history symbols")
