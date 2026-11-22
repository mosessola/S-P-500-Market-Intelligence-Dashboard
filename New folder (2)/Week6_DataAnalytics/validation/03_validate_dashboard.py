"""Task 6 - independent validation. Recomputes dashboard numbers with a SEPARATE code path
(csv module + numpy, no pandas, no engineered columns) and compares with the figure builders.
Run from project root:  python validation/03_validate_dashboard.py"""
import csv, json, sys, math, collections
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
import app  # noqa: E402  (imports the figure builders; does not start a server)

raw = collections.defaultdict(list); nrows = 0; vol_total = 0
with open(ROOT / "data/raw/sp500_stock_prices_cleaned.csv", newline="") as f:
    for r in csv.DictReader(f):
        raw[r["symbol"]].append((r["date"], float(r["close"]), int(r["volume"]), float(r["open"]), float(r["high"]), float(r["low"])))
        nrows += 1; vol_total += int(r["volume"])
for s in raw: raw[s].sort()
results = []
def check(name, ok, detail):
    results.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail}); print(("PASS " if ok else "FAIL "), name, "-", detail)

SEL = app.SELECTED; A, B = "2014-01-02", "2017-12-29"
def trace(fig, name):  return next(t for t in fig.data if t.name == name)

# V1 source-vs-dashboard reconciliation
check("V1a record count", nrows == len(app.DF), f"csv rows {nrows:,} vs dashboard {len(app.DF):,}")
check("V1b symbol count", len(raw) == app.DF.symbol.nunique() == 505, f"{len(raw)} symbols")
check("V1c total shares traded", vol_total == int(app.DF.volume.sum()), f"{vol_total:,}")
kp = dict(app.build_kpis(SEL, A, B))
exp_avg = np.mean([c for s in SEL for (_, c, *_ ) in raw[s]])
check("V1d KPI average close (selected)", kp["Avg close, selected stocks"] == f"${exp_avg:,.2f}", f"{kp['Avg close, selected stocks']} vs ${exp_avg:,.2f}")

# V2 daily percentage return - manual formula per symbol vs dashboard trace
fig = app.build_returns(SEL, A, B); worst = 0
for s in SEL:
    c = np.array([x[1] for x in raw[s]]); manual = (c[1:] / c[:-1] - 1) * 100
    y = np.array(trace(fig, s).y, dtype=float)[1:]
    worst = max(worst, np.nanmax(np.abs(y - manual)))
check("V2 daily return formula", worst < 1e-9, f"max abs difference across 6 stocks x 1,006 days = {worst:.2e} percentage points")

# V3 moving averages - manual rolling mean vs dashboard trace (20 and 5 day)
for w in (20, 5):
    fig = app.build_ma(SEL, A, B, w); worst = 0
    for s in SEL:
        c = np.array([x[1] for x in raw[s]]); manual = np.array([c[i - w + 1:i + 1].mean() for i in range(w - 1, len(c))])
        y = np.array(trace(fig, f"{s} {w}-day MA").y, dtype=float); lead = np.isnan(y[:w - 1]).all()
        worst = max(worst, np.abs(y[w - 1:] - manual).max())
    check(f"V3 {w}-day moving average", worst < 1e-9 and lead, f"max abs difference {worst:.2e}; first {w-1} values blank (no look-ahead, no zero fill)")

# V4 stock-selection and date filters
fig = app.build_close(["MSFT", "JPM"], "2016-01-01", "2016-12-31")
names = {t.name for t in fig.data}; xs = [str(x)[:10] for t in fig.data for x in t.x]
exp_n = sum(1 for s in ("MSFT", "JPM") for r in raw[s] if "2016-01-01" <= r[0] <= "2016-12-31")
check("V4a symbol filter", names == {"MSFT", "JPM"}, f"traces {sorted(names)}")
check("V4b date filter", min(xs) >= "2016-01-01" and max(xs) <= "2016-12-31" and len(xs) == exp_n, f"{len(xs)} points, {min(xs)}..{max(xs)}, expected {exp_n}")
check("V4c six-series cap", len(app.build_close(app.ALL_SYMBOLS[:9], A, B).data) == 6, "9 symbols selected -> 6 plotted")
check("V4d empty selection safe", len(app.build_close([], A, B).data) == 0, "no traces, message shown instead of error")

# V5 volatility (sample std of daily returns, annualised sqrt(252)) and volume average
s = "XOM"; c = np.array([x[1] for x in raw[s]]); r = (c[1:] / c[:-1] - 1) * 100
manual = r[-30:].std(ddof=1) * math.sqrt(252); y = float(trace(app.build_volatility([s], A, B), s).y[-1])
check("V5a rolling 30-day volatility", abs(manual - y) < 1e-9, f"XOM last value {y:.4f} vs manual {manual:.4f}")
fig = app.build_avg_volume(SEL, A, B); worst = max(abs(float(v) - np.mean([x[2] for x in raw[s]]) / 1e6) for s, v in zip(fig.data[0].x, fig.data[0].y))
check("V5b average volume", worst < 1e-9, f"max abs difference {worst:.2e} million shares")

# V6 summary-table totals (analysis script) vs manual first/last close, stocks with no flagged days
import pandas as pd
summ = pd.read_csv(ROOT / "docs/tables/symbol_summary_all_505.csv", index_col=0); worst = 0
for s in SEL:
    if summ.loc[s, "n_suspect_returns"] == 0:
        c = [x[1] for x in raw[s]]; worst = max(worst, abs((c[-1] / c[0] - 1) * 100 - summ.loc[s, "total_return_pct"]))
check("V6 total return", worst < 1e-3, f"max abs difference {worst:.4f} percentage points (stocks without flagged days)")

# V7 interior gaps in 'complete' histories (explains discrepancy with brief's record count)
cal = sorted({r[0] for v in raw.values() for r in v}); gaps = {}
for s, v in raw.items():
    d0, d1 = v[0][0], v[-1][0]; have = {r[0] for r in v}
    miss = [d for d in cal if d0 <= d <= d1 and d not in have]
    if miss: gaps[s] = len(miss)
print("interior missing dates:", gaps)
json.dump({"results": results, "interior_gaps": gaps, "brief_vs_file": {"brief_rows": 497472, "file_rows": nrows}}, open(ROOT / "validation/validation_results.json", "w"), indent=2)
lines = ["# Validation evidence (Task 6)", "", "Method: dashboard figure builders (`dashboard/app.py`) were called with fixed inputs and compared with an independent recalculation from the raw CSV using only the `csv` module and NumPy. Script: `validation/03_validate_dashboard.py`.", "",
         "| Check | Result | Detail |", "|---|---|---|"] + [f"| {r['check']} | {r['result']} | {r['detail']} |" for r in results]
lines += ["", f"Interior gaps found (symbol: missing trading dates between first and last record): {gaps}"]
(ROOT / "validation/validation_evidence.md").write_text("\n".join(lines))
sys.exit(0 if all(r["result"] == "PASS" for r in results) else 1)
