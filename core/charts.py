"""Plotly template for Interwins. Import this module once at app startup."""
import plotly.graph_objects as go
import plotly.io as pio

_NAVY   = "#0A1261"
_ACCENT = "#3b82f6"
_INK    = "#14233b"
_SLATE  = "#64748b"
_GRID   = "#e2e8f0"
_GREEN  = "#2bb673"
_RED    = "#ef4444"
_AMBER  = "#f59e0b"

DEFAULT_CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

pio.templates["interwins"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=_INK, size=12),
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        colorway=[_ACCENT, _RED, _GREEN, _AMBER, "#60a5fa", _NAVY],
        xaxis=dict(
            gridcolor=_GRID, zerolinecolor=_GRID,
            tickfont=dict(color=_SLATE), linecolor=_GRID,
        ),
        yaxis=dict(
            gridcolor=_GRID, zerolinecolor=_GRID,
            tickfont=dict(color=_SLATE), linecolor=_GRID,
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=_GRID, borderwidth=1,
            font=dict(color=_INK),
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        hovermode="x unified",
    )
)

pio.templates["interwins_dark"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color="#eef1f7", size=12),
        paper_bgcolor="rgba(42,45,62,0)",
        plot_bgcolor="rgba(42,45,62,0)",
        colorway=[_ACCENT, _RED, _GREEN, _AMBER, "#60a5fa", "#dbe2ff"],
        xaxis=dict(
            gridcolor="#363a4b", zerolinecolor="#363a4b",
            tickfont=dict(color="#8d93a4"), linecolor="#363a4b",
        ),
        yaxis=dict(
            gridcolor="#363a4b", zerolinecolor="#363a4b",
            tickfont=dict(color="#8d93a4"), linecolor="#363a4b",
        ),
        legend=dict(
            bgcolor="rgba(42,45,62,0.9)",
            bordercolor="#363a4b", borderwidth=1,
            font=dict(color="#eef1f7"),
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        hovermode="x unified",
    )
)


def get_template(dark: bool = False) -> str:
    return "interwins_dark" if dark else "interwins"


def apply_default_template(dark: bool = False) -> None:
    pio.templates.default = get_template(dark)


def chart_config(**overrides) -> dict:
    return {**DEFAULT_CHART_CONFIG, **overrides}
