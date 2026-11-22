"""Week 6 - Track A: data inspection, cleaning and feature engineering.

Reads  data/raw/sp500_stock_prices_cleaned.csv   (never modified)
Writes data/processed/sp500_prepared.parquet     (analysis dataset)
       docs/data_quality_checks.json              (machine-readable audit)
Run from the project root:  python scripts/01_prepare_data.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/sp500_stock_prices_cleaned.csv"
OUT = ROOT / "data/processed/sp500_prepared.parquet"
AUDIT = ROOT / "docs/data_quality_checks.json"

# Single-day moves reviewed by hand. These are almost certainly corporate actions
# (spin-offs / splits) or a bad print, NOT real price performance. Identified from the
# price discontinuity itself; the cause is analyst knowledge and is not in the dataset.
CORP_ACTION_ROWS = [
    ("NI", "2015-07-02"), ("EBAY", "2015-07-20"), ("DISCK", "2014-08-07"),
    ("DISCA", "2014-08-07"), ("BAX", "2015-07-01"),
    ("ARNC", "2016-11-01"), ("YUM", "2016-11-01"), ("BHGE", "2017-07-05"),
]
# Reversal rule: a >20% move that is almost fully undone the next trading day is treated as a
# bad print (e.g. LNT 2016-05-19/20). Both days are flagged.
REVERSAL_MIN_MOVE, REVERSAL_NET_MAX = 20, 10
MA_WINDOWS = (5, 10, 20, 50)

df = pd.read_csv(RAW, low_memory=False, parse_dates=["date"])
audit = {"rows": len(df), "columns": list(df.columns)}

# ---- inspection --------------------------------------------------------------
audit["symbols"] = int(df.symbol.nunique())
audit["trading_dates"] = int(df.date.nunique())
audit["date_min"], audit["date_max"] = str(df.date.min().date()), str(df.date.max().date())
audit["missing_by_column"] = {c: int(v) for c, v in df.isna().sum().items()}
audit["duplicate_symbol_date"] = int(df.duplicated(["symbol", "date"]).sum())
audit["zero_volume_rows"] = int((df.volume == 0).sum())
audit["nonpositive_price_rows"] = int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())
audit["originally_sorted_by_symbol_date"] = bool(
    df.equals(df.sort_values(["symbol", "date"]).reset_index(drop=True)))
audit["data_note_counts"] = df.data_note.value_counts().to_dict()
bad = (df.high < df[["open", "close", "low"]].max(axis=1)) | (df.low > df[["open", "close", "high"]].min(axis=1))
audit["ohlc_inconsistent_rows"] = int(bad.sum())

# ---- ordering (required before any per-symbol calculation) ------------------
df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
counts = df.groupby("symbol").size()
audit["symbols_with_incomplete_history"] = int((counts < audit["trading_dates"]).sum())

# ---- engineered fields (always grouped by symbol) ---------------------------
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month
df["quarter"] = df.date.dt.quarter
g = df.groupby("symbol", sort=False)
df["daily_change"] = g.close.diff()
df["daily_return_pct"] = g.close.pct_change() * 100
df["daily_range"] = df.high - df.low
df["intraday_return_pct"] = (df.close / df.open - 1) * 100

# Returns that are corporate-action artefacts or bad prints are excluded from return and
# volatility statistics; the raw return is kept in daily_return_pct for transparency.
key = set(CORP_ACTION_ROWS)
df["suspect_return_flag"] = [(s, str(d.date())) in key for s, d in zip(df.symbol, df.date)]
nxt = g.daily_return_pct.shift(-1)
rev = (df.daily_return_pct.abs() > REVERSAL_MIN_MOVE) & (np.sign(nxt) == -np.sign(df.daily_return_pct)) \
      & (((1 + df.daily_return_pct / 100) * (1 + nxt / 100) - 1).abs() * 100 < REVERSAL_NET_MAX)
df["suspect_return_flag"] |= rev | rev.groupby(df.symbol).shift(1, fill_value=False)
df["suspect_return_flag"] |= df.data_note.fillna("").str.startswith("OHLC inconsistent")
df["return_clean_pct"] = df.daily_return_pct.where(~df.suspect_return_flag)

for w in MA_WINDOWS:
    df[f"ma_{w}"] = g.close.transform(lambda s, w=w: s.rolling(w, min_periods=w).mean())

audit["suspect_return_rows"] = int(df.suspect_return_flag.sum())
audit["suspect_rows_list"] = (df.loc[df.suspect_return_flag, ["symbol", "date", "daily_return_pct"]]
    .assign(date=lambda x: x.date.dt.strftime("%Y-%m-%d")).round(2).to_dict("records"))
audit["extreme_moves_over_40pct"] = (
    df.loc[df.daily_return_pct.abs() > 40, ["symbol", "date", "daily_return_pct", "suspect_return_flag"]]
      .assign(date=lambda x: x.date.dt.strftime("%Y-%m-%d")).round(2).to_dict("records"))
audit["new_columns"] = [c for c in df.columns if c not in
                        ["symbol", "date", "open", "high", "low", "close", "volume", "data_note"]]

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUT, index=False)
AUDIT.write_text(json.dumps(audit, indent=2, default=str))
print(json.dumps({k: v for k, v in audit.items() if k != "extreme_moves_over_40pct"}, indent=2, default=str))
print("saved", OUT, df.shape)
