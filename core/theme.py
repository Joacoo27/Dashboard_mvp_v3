"""Theme loader — called ONCE at the top of app.py."""
from pathlib import Path
import streamlit as st

_ASSETS = Path(__file__).parent / "assets"


@st.cache_resource
def _load_base_css() -> str:
    tokens = (_ASSETS / "colors_and_type.css").read_text(encoding="utf-8")
    components = (_ASSETS / "components.css").read_text(encoding="utf-8")
    return tokens + "\n" + components


TOKENS = {
    "navy":    "#0A1261",
    "accent":  "#3b82f6",
    "ink":     "#14233b",
    "brand":   "#1e3a8a",
    "success": "#2bb673",
    "danger":  "#ef4444",
    "warning": "#f59e0b",
    "slate":   "#64748b",
    "grid":    "#e2e8f0",
}


def inject_theme() -> None:
    """Load the Interwins design system CSS in light mode only."""
    css = _load_base_css()
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def theme_toggle() -> None:
    """Left as a no-op to keep compatibility with older imports."""
    return None


def get_tokens() -> dict:
    return TOKENS
