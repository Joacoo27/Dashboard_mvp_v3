"""Plotly template for Interwins. Import this module once at app startup."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

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


def get_template(dark: bool | None = None) -> str:
    if dark is None:
        dark = st.session_state.get("iw_dark_mode", False)
    return "interwins_dark" if dark else "interwins"


def apply_default_template(dark: bool | None = None) -> None:
    if dark is None:
        dark = st.session_state.get("iw_dark_mode", False)
    pio.templates.default = get_template(dark)


def chart_config(**overrides) -> dict:
    return {**DEFAULT_CHART_CONFIG, **overrides}


def render_chart(fig: go.Figure, **kwargs) -> None:
    """st.plotly_chart wrapper — applies dark/light theme directly to the figure."""
    is_dark = st.session_state.get("iw_dark_mode", False)
    if is_dark:
        fig.update_layout(
            paper_bgcolor="rgba(27,29,42,0)",
            plot_bgcolor="rgba(27,29,42,0)",
            font=dict(color="#eef1f7"),
            legend=dict(font=dict(color="#eef1f7"), bgcolor="rgba(27,29,42,0.9)", bordercolor="#363a4b"),
        )
        fig.update_xaxes(tickfont=dict(color="#8d93a4"), gridcolor="#363a4b", zerolinecolor="#363a4b")
        fig.update_yaxes(tickfont=dict(color="#8d93a4"), gridcolor="#363a4b", zerolinecolor="#363a4b")
        if any(getattr(t, "type", None) == "indicator" for t in fig.data):
            fig.update_traces(
                selector=dict(type="indicator"),
                number_font_color="#eef1f7",
                gauge_bgcolor="rgba(42,45,62,0.9)",
                gauge_bordercolor="#363a4b",
            )
    st.plotly_chart(fig, **kwargs)
