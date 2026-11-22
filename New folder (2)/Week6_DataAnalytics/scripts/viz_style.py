"""Shared chart style: validated categorical palette (light surface) + Plotly template."""
import plotly.graph_objects as go
import plotly.io as pio

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]  # fixed slot order
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
SEQ_BLUE = [[0, "#cde2fb"], [0.5, "#3987e5"], [1, "#0d366b"]]
SELECTED = ["AAPL", "MSFT", "AMZN", "JPM", "XOM", "JNJ"]       # complete 1,007-day histories
COLOR = {s: SERIES[i] for i, s in enumerate(SELECTED)}          # colour follows the entity

pio.templates["analystlab"] = go.layout.Template(layout=go.Layout(
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13, color=INK),
    paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, colorway=SERIES,
    xaxis=dict(gridcolor=GRID, linecolor=GRID, zeroline=False, tickfont=dict(color=INK2)),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, zeroline=False, tickfont=dict(color=INK2)),
    title=dict(font=dict(size=17), x=0.01, xanchor="left"),
    legend=dict(orientation="h", y=-0.18, x=0, font=dict(color=INK2)),
    margin=dict(l=60, r=30, t=70, b=70), hovermode="x unified"))
pio.templates.default = "analystlab"
