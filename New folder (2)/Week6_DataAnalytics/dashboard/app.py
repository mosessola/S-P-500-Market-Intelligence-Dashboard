"""S&P 500 Market Intelligence Dashboard (Track A) - Plotly Dash.

Run from project root:   python dashboard/app.py      then open http://127.0.0.1:8050
Pages (URL):  /overview  /price  /returns  /volume
Figure builders are plain functions (build_*) so validation scripts can call them without a server.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, dash_table

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from viz_style import SERIES, SELECTED, COLOR, SURFACE, INK, INK2, GRID, SEQ_BLUE  # noqa: E402

DF = pd.read_parquet(ROOT / "data/processed/sp500_prepared.parquet")
ALL_SYMBOLS = sorted(DF.symbol.unique())
DMIN, DMAX = DF.date.min(), DF.date.max()
N_DATES = DF.date.nunique()
MAX_COMPARE = 6   # categorical palette is validated for 6 adjacent slots; never cycle colours


# ------------------------------------------------------------------ helpers
def pick(symbols, start, end):
    """Filter used by every page: symbol selection + date range."""
    syms = list(symbols or [])[:MAX_COMPARE]
    d = DF[DF.symbol.isin(syms) & (DF.date >= pd.Timestamp(start)) & (DF.date <= pd.Timestamp(end))]
    return d, syms


def colors_for(syms):
    """Colour follows the entity: known stocks keep their slot, others take the next free slot."""
    free = [c for c in SERIES if c not in {COLOR[s] for s in syms if s in COLOR}]
    out = {}
    for s in syms:
        out[s] = COLOR[s] if s in COLOR else free.pop(0)
    return out


def style(fig, title, ytitle=None, h=380, hover="x unified"):
    fig.update_layout(title=title, yaxis_title=ytitle, height=h, hovermode=hover, template="analystlab")
    return fig


def empty(msg="No data for this selection"):
    fig = go.Figure(); fig.add_annotation(text=msg, showarrow=False, font=dict(size=15, color=INK2))
    return style(fig, "", h=300)


# ------------------------------------------------------------------ Page 1: overview
def build_kpis(symbols, start, end):
    d, syms = pick(symbols, start, end)
    sel_avg = d.close.mean() if len(d) else np.nan
    return [("Stock symbols", f"{DF.symbol.nunique():,}"), ("Trading records", f"{len(DF):,}"),
            ("Date range", f"{DMIN:%d %b %Y} – {DMAX:%d %b %Y}"),
            ("Avg close, selected stocks", f"${sel_avg:,.2f}" if len(d) else "–")]


def build_symbol_distribution():
    c = DF.groupby("symbol").size()
    bins = pd.cut(c, [0, 250, 500, 750, 1006, N_DATES], labels=["< 250", "250–500", "500–750", "751–1,006", "Complete (1,007)"])
    b = bins.value_counts().sort_index()
    fig = go.Figure(go.Bar(x=b.index.astype(str), y=b.values, marker_color=SERIES[0],
                           hovertemplate="%{x} days: %{y} symbols<extra></extra>"))
    return style(fig, "Symbols by number of trading days available", "Number of symbols", hover="closest")


def build_market_index(start, end):
    d = DF[(DF.date >= pd.Timestamp(start)) & (DF.date <= pd.Timestamp(end))]
    r = d.groupby("date").return_clean_pct.mean().fillna(0) / 100
    idx = (1 + r).cumprod() * 100
    vol = d.groupby("date").volume.sum() / 1e9
    fig = go.Figure()
    fig.add_scatter(x=idx.index, y=idx, name="Equal-weight index (start = 100)", line=dict(color=SERIES[0], width=2.5))
    fig.update_yaxes(title="Index level")
    return style(fig, "General market overview: equal-weight index of all symbols"), vol


def build_market_volume(vol):
    m = vol.resample("ME").sum()
    fig = go.Figure(go.Bar(x=m.index, y=m.values, marker_color=SERIES[0], hovertemplate="%{y:.1f}bn shares<extra></extra>"))
    return style(fig, "Total shares traded per month, all symbols (billions)", "Billion shares")


# ------------------------------------------------------------------ Page 2: price
def build_close(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s]
        fig.add_scatter(x=x.date, y=x.close, name=s, line=dict(color=cm[s], width=2))
    return style(fig, "Closing price", "Price (USD assumed)")


def build_ohlc(symbols, start, end):
    d, syms = pick(symbols, start, end)
    if d.empty: return empty()
    s = syms[0]; x = d[d.symbol == s]
    fig = go.Figure(go.Candlestick(x=x.date, open=x.open, high=x.high, low=x.low, close=x.close, name=s,
                                   increasing_line_color=SERIES[0], decreasing_line_color=SERIES[1]))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return style(fig, f"Open / high / low / close – {s} (first selected symbol)", "Price (USD assumed)")


def build_ohlc_means(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    t = d.groupby("symbol")[["open", "high", "low", "close"]].mean().loc[syms]
    fig = go.Figure()
    for col, lab in [("open", "Open"), ("high", "High"), ("low", "Low"), ("close", "Close")]:
        fig.add_bar(x=t.index, y=t[col], name=lab, marker_color=SERIES[["open", "high", "low", "close"].index(col)])
    fig.update_layout(barmode="group", bargap=.25)
    return style(fig, "Average open, high, low and close for the selected period", "Average price (USD)", hover="closest")


def build_daily_move(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s]
        fig.add_scatter(x=x.date, y=x.daily_range, name=s, line=dict(color=cm[s], width=1.5))
    return style(fig, "Daily trading range (high − low)", "USD per share")


def build_ma(symbols, start, end, window):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s]
        fig.add_scatter(x=x.date, y=x.close, name=f"{s} close", line=dict(color=cm[s], width=1, dash="dot"), opacity=.6)
        fig.add_scatter(x=x.date, y=x[f"ma_{window}"], name=f"{s} {window}-day MA", line=dict(color=cm[s], width=2.5))
    return style(fig, f"Closing price with {window}-day moving average", "Price (USD assumed)")


# ------------------------------------------------------------------ Page 3: returns & volatility
def build_returns(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s]
        fig.add_scatter(x=x.date, y=x.return_clean_pct, name=s, line=dict(color=cm[s], width=1))
    return style(fig, "Daily percentage return (corporate-action days excluded)", "Return (%)")


def build_avg_return(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    m = d.groupby("symbol").return_clean_pct.mean().loc[syms]
    fig = go.Figure(go.Bar(x=m.index, y=m.values, marker_color=[cm[s] for s in m.index],
                           hovertemplate="%{x}: %{y:.3f}% per day<extra></extra>"))
    return style(fig, "Average daily return", "Mean daily return (%)", h=340, hover="closest")


def build_distribution(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        r = d[d.symbol == s].return_clean_pct.dropna()
        fig.add_histogram(x=r, name=s, opacity=.55, marker_color=cm[s], xbins=dict(start=-8, end=8, size=.4), histnorm="probability")
    fig.update_layout(barmode="overlay")
    return style(fig, "Return distribution (shown from −8% to +8%)", "Share of days", h=340, hover="closest")


def build_volatility(symbols, start, end, window=30):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s].set_index("date").return_clean_pct.rolling(window).std() * np.sqrt(252)
        fig.add_scatter(x=x.index, y=x, name=s, line=dict(color=cm[s], width=2))
    return style(fig, f"Rolling {window}-day annualised volatility", "Volatility (%)")


def volatility_table(symbols, start, end):
    d, syms = pick(symbols, start, end)
    if d.empty: return []
    g = d.groupby("symbol")
    t = pd.DataFrame({"Mean daily return %": g.return_clean_pct.mean(), "Daily std dev %": g.return_clean_pct.std(),
                      "Annualised volatility %": g.return_clean_pct.std() * np.sqrt(252),
                      "Best day %": g.return_clean_pct.max(), "Worst day %": g.return_clean_pct.min(),
                      "Trading days": g.size()}).loc[syms].round(3).reset_index().rename(columns={"symbol": "Symbol"})
    return t.to_dict("records")


# ------------------------------------------------------------------ Page 4: volume
def build_volume_trend(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[d.symbol == s].set_index("date").volume.resample("ME").mean() / 1e6
        fig.add_scatter(x=x.index, y=x, name=s, line=dict(color=cm[s], width=2))
    return style(fig, "Average daily volume by month", "Millions of shares")


def build_avg_volume(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    m = d.groupby("symbol").volume.mean().loc[syms] / 1e6
    fig = go.Figure(go.Bar(x=m.index, y=m.values, marker_color=[cm[s] for s in m.index],
                           hovertemplate="%{x}: %{y:.1f}M shares/day<extra></extra>"))
    return style(fig, "Average daily volume", "Millions of shares", h=340, hover="closest")


def build_volume_vs_move(symbols, start, end):
    d, syms = pick(symbols, start, end); cm = colors_for(syms)
    if d.empty: return empty()
    fig = go.Figure()
    for s in syms:
        x = d[(d.symbol == s) & ~d.suspect_return_flag].dropna(subset=["return_clean_pct"])
        fig.add_scatter(x=x.volume / 1e6, y=x.return_clean_pct.abs(), mode="markers", name=s,
                        marker=dict(color=cm[s], size=6, opacity=.55, line=dict(color=SURFACE, width=.5)),
                        hovertemplate="%{x:.1f}M shares | |return| %{y:.2f}%<extra></extra>")
    fig.update_xaxes(title="Volume (millions of shares)", type="log")
    return style(fig, "Volume vs size of daily price move (log volume axis)", "Absolute daily return (%)", h=340, hover="closest")


def volume_extremes(symbols, start, end):
    d, syms = pick(symbols, start, end)
    if d.empty: return []
    rows = []
    for s in syms:
        x = d[d.symbol == s]
        hi, lo = x.loc[x.volume.idxmax()], x.loc[x.volume.idxmin()]
        rows.append({"Symbol": s, "Highest volume": f"{int(hi.volume):,}", "High date": f"{hi.date:%Y-%m-%d}",
                     "Lowest volume": f"{int(lo.volume):,}", "Low date": f"{lo.date:%Y-%m-%d}",
                     "Spearman: volume vs |return|": round(x[~x.suspect_return_flag].assign(a=lambda z: z.return_clean_pct.abs())[["volume", "a"]].corr(method="spearman").iloc[0, 1], 3)})
    return rows


# ------------------------------------------------------------------ layout
CSS = {"fontFamily": "Inter, Segoe UI, Arial, sans-serif", "background": SURFACE, "color": INK, "padding": "18px 28px", "minHeight": "100vh"}
CARD = {"border": f"1px solid {GRID}", "borderRadius": "8px", "padding": "6px", "background": SURFACE}
GRID2 = {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))", "gap": "14px", "marginTop": "14px"}
TBL = dict(style_header={"fontWeight": "600", "background": "#f1f0ec", "border": f"1px solid {GRID}"},
           style_cell={"padding": "6px 10px", "fontFamily": "inherit", "fontSize": 13, "border": f"1px solid {GRID}", "textAlign": "right"},
           style_cell_conditional=[{"if": {"column_id": "Symbol"}, "textAlign": "left"}])

app = Dash(__name__, suppress_callback_exceptions=True, title="S&P 500 Market Intelligence")
server = app.server


def g(fid):
    return html.Div(dcc.Graph(id=fid, config={"displaylogo": False}), style=CARD)


def nav():
    links = [("/overview", "1 Market Overview"), ("/price", "2 Price Performance"), ("/returns", "3 Returns & Volatility"), ("/volume", "4 Trading Volume")]
    return html.Div([dcc.Link(t, href=h, id=f"nav{i}", style={"padding": "8px 14px", "border": f"1px solid {GRID}", "borderRadius": "6px",
                                                              "marginRight": "8px", "textDecoration": "none", "color": INK, "fontSize": 14})
                     for i, (h, t) in enumerate(links)], style={"margin": "10px 0 14px"})


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.H2("S&P 500 Market Intelligence Dashboard", style={"margin": 0}),
    html.Div("Historical daily prices, 2014–2017. Descriptive only: past performance does not predict future returns. Prices are price-only (no dividends) and currency is assumed USD.",
             style={"color": INK2, "fontSize": 13, "marginTop": 4}),
    nav(),
    html.Div([
        html.Div([html.Label("Stock symbols (up to 6 compared)", style={"fontSize": 13, "color": INK2}),
                  dcc.Dropdown(id="symbols", options=ALL_SYMBOLS, value=SELECTED, multi=True, clearable=False)], style={"flex": "3", "minWidth": 320}),
        html.Div([html.Label("Date range", style={"fontSize": 13, "color": INK2}), html.Br(),
                  dcc.DatePickerRange(id="dates", min_date_allowed=DMIN, max_date_allowed=DMAX, start_date=DMIN, end_date=DMAX,
                                      display_format="YYYY-MM-DD")], style={"flex": "2", "minWidth": 300}),
        html.Div([html.Label("Moving-average window", style={"fontSize": 13, "color": INK2}),
                  dcc.Dropdown(id="ma", options=[5, 10, 20, 50], value=20, clearable=False)], style={"flex": "1", "minWidth": 160}),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "alignItems": "flex-end"}),
    html.Div(id="notice", style={"color": INK2, "fontSize": 12, "marginTop": 6}),
    html.Div(id="page"),
], style=CSS)


def page_layout(path):
    if path == "/price":
        return html.Div([g("p2_close"), html.Div([g("p2_ohlc"), g("p2_ohlcmeans"), g("p2_range"), g("p2_ma")], style=GRID2)], style={"marginTop": "14px"})
    if path == "/returns":
        return html.Div([g("p3_ret"), html.Div([g("p3_avg"), g("p3_dist")], style=GRID2), g("p3_vol"),
                         html.H4("Return and volatility summary (selected period)"), dash_table.DataTable(id="p3_table", **TBL)], style={"marginTop": "14px"})
    if path == "/volume":
        return html.Div([g("p4_trend"), html.Div([g("p4_avg"), g("p4_scatter")], style=GRID2),
                         html.H4("Highest and lowest volume observations"), dash_table.DataTable(id="p4_table", **TBL)], style={"marginTop": "14px"})
    return html.Div([html.Div(id="kpis", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(210px, 1fr))", "gap": "12px"}),
                     html.Div([g("p1_index"), g("p1_vol")], style=GRID2), html.Div([g("p1_dist")], style=GRID2)], style={"marginTop": "14px"})


@app.callback(Output("page", "children"), Input("url", "pathname"))
def render_page(path):
    return page_layout(path or "/overview")


@app.callback(Output("notice", "children"), Input("symbols", "value"))
def notice(symbols):
    n = len(symbols or [])
    return f"Only the first {MAX_COMPARE} symbols are plotted so colours stay distinguishable ({n} selected)." if n > MAX_COMPARE else ""



@app.callback(Output("kpis", "children"), Output("p1_index", "figure"), Output("p1_vol", "figure"), Output("p1_dist", "figure"),
              Input("symbols", "value"), Input("dates", "start_date"), Input("dates", "end_date"))
def page1(sym, a, b):
    kp = [html.Div([html.Div(k, style={"fontSize": 12, "color": INK2}), html.Div(v, style={"fontSize": 22, "fontWeight": 600})], style={**CARD, "padding": "12px 16px"})
          for k, v in build_kpis(sym, a, b)]
    idx, vol = build_market_index(a, b)
    return kp, idx, build_market_volume(vol), build_symbol_distribution()


@app.callback(Output("p2_close", "figure"), Output("p2_ohlc", "figure"), Output("p2_ohlcmeans", "figure"), Output("p2_range", "figure"), Output("p2_ma", "figure"),
              Input("symbols", "value"), Input("dates", "start_date"), Input("dates", "end_date"), Input("ma", "value"))
def page2(sym, a, b, ma):
    return build_close(sym, a, b), build_ohlc(sym, a, b), build_ohlc_means(sym, a, b), build_daily_move(sym, a, b), build_ma(sym, a, b, ma)


@app.callback(Output("p3_ret", "figure"), Output("p3_avg", "figure"), Output("p3_dist", "figure"), Output("p3_vol", "figure"), Output("p3_table", "data"),
              Input("symbols", "value"), Input("dates", "start_date"), Input("dates", "end_date"))
def page3(sym, a, b):
    return build_returns(sym, a, b), build_avg_return(sym, a, b), build_distribution(sym, a, b), build_volatility(sym, a, b), volatility_table(sym, a, b)


@app.callback(Output("p4_trend", "figure"), Output("p4_avg", "figure"), Output("p4_scatter", "figure"), Output("p4_table", "data"),
              Input("symbols", "value"), Input("dates", "start_date"), Input("dates", "end_date"))
def page4(sym, a, b):
    return build_volume_trend(sym, a, b), build_avg_volume(sym, a, b), build_volume_vs_move(sym, a, b), volume_extremes(sym, a, b)


if __name__ == "__main__":
    app.run(debug=False, port=8050)
