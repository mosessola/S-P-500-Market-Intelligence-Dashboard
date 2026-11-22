"""Headline statistics used in the executive summary. Run after 02_analysis_and_charts.py."""
import json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_parquet(ROOT / "data/processed/sp500_prepared.parquet")
s = pd.read_csv(ROOT / "docs/tables/symbol_summary_all_505.csv", index_col=0)
full = s[s.complete_history]
r = df.groupby("date").return_clean_pct.mean().fillna(0) / 100
idx = (1 + r).cumprod() * 100
yr = (1 + r).groupby(r.index.year).prod().sub(1).mul(100)
mm = pd.read_csv(ROOT / "docs/tables/q6_market_monthly_return.csv")
tot = df.groupby("symbol").volume.sum().sort_values(ascending=False)
out = {
 "equal_weight_index_end": round(idx.iloc[-1], 1), "equal_weight_yearly_return_pct": yr.round(1).to_dict(),
 "median_total_return_pct": round(full.total_return_pct.median(), 1), "pct_full_history_positive": round((full.total_return_pct > 0).mean() * 100, 1),
 "n_full_history": len(full), "median_ann_vol_pct": round(full.annualised_vol_pct.median(), 1),
 "top10_share_of_volume_pct": round(tot.head(10).sum() / tot.sum() * 100, 1),
 "best_month": mm.loc[mm.equal_weight_return_pct.idxmax()].to_dict(), "worst_month": mm.loc[mm.equal_weight_return_pct.idxmin()].to_dict(),
 "index_worst_drawdown_pct": round(((idx / idx.cummax()) - 1).min() * 100, 1),
 "index_worst_drawdown_date": str((idx / idx.cummax() - 1).idxmin().date()),
 "low_vol_high_return": full[(full.annualised_vol_pct < full.annualised_vol_pct.median()) & (full.total_return_pct > 100)].index.tolist()[:10],
 "corr_return_vol_across_stocks": round(full[["total_return_pct", "annualised_vol_pct"]].corr(method="spearman").iloc[0, 1], 3),
}
(ROOT / "docs/tables/insight_stats.json").write_text(json.dumps(out, indent=2, default=str)); print(json.dumps(out, indent=2, default=str))
