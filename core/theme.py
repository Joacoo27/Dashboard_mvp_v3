"""Theme loader — called ONCE at the top of app.py."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as _components

_ASSETS = Path(__file__).parent / "assets"


@st.cache_resource
def _load_base_css() -> str:
    tokens = (_ASSETS / "colors_and_type.css").read_text(encoding="utf-8")
    components = (_ASSETS / "components.css").read_text(encoding="utf-8")
    return tokens + "\n" + components


@st.cache_resource
def _load_dark_css() -> str:
    p = _ASSETS / "dark_overrides.css"
    return p.read_text(encoding="utf-8") if p.exists() else ""


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
    """Load the Interwins design system CSS and apply dark/light mode."""
    is_dark = st.session_state.get("iw_dark_mode", False)

    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(f"<style>{_load_base_css()}</style>", unsafe_allow_html=True)

    # Siempre inyectar el bloque de dark CSS (vacío en modo claro) para que
    # el árbol de widgets sea idéntico en ambos modos y el toggle no pierda estado.
    dark_css = _load_dark_css() if is_dark else ""
    st.markdown(f"<style>{dark_css}</style>", unsafe_allow_html=True)

    # Propaga data-theme al documento padre para activar overrides de variables CSS
    theme = "dark" if is_dark else "light"
    _components.html(
        f"""<script>
        (function(){{
            var t = "{theme}";
            try {{ window.parent.document.documentElement.setAttribute("data-theme", t); }} catch(e) {{}}
        }})();
        </script>""",
        height=0,
        scrolling=False,
    )


def theme_toggle() -> None:
    """Left as a no-op to keep compatibility with older imports."""
    return None


def get_tokens() -> dict:
    return TOKENS
