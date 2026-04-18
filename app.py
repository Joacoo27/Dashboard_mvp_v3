from pathlib import Path

import streamlit as st

import core.charts  # registers Plotly templates at import time
from core.components import (
    render_mode_indicator,
    render_module_nav,
    render_sidebar_brand,
    render_sidebar_section,
    render_top_nav,
)
from core.registry import discover_modules, resolve_active_module, resolve_active_tab
from core.theme import inject_theme


st.set_page_config(
    page_title="Panel de Interwins",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
core.charts.apply_default_template()

MODULE_PACKAGES = [
    "Modulo_ventas_salud",
    "Modulo_financiero",
    "Modulo_comercial",
]


def _query_param(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value


def _resolve_logo_asset() -> Path | None:
    root = Path(__file__).resolve().parent
    preferred = root / "IMPORTACION MOCKUP" / "assets" / "logo_mark.svg"
    if preferred.exists():
        return preferred

    for candidate in (
        root / "assets" / "logo_interwins.png",
        root / "assets" / "logo_interwins.jpg",
    ):
        if candidate.exists():
            return candidate
    return None


def _set_navigation(module_key: str, tab_key: str) -> None:
    st.query_params.clear()
    st.query_params["module"] = module_key
    st.query_params["tab"] = tab_key
    st.rerun()


def main() -> None:
    modules = discover_modules(MODULE_PACKAGES)
    active_module = resolve_active_module(modules, _query_param("module"))
    active_tab = resolve_active_tab(active_module, _query_param("tab"))

    render_sidebar_brand(_resolve_logo_asset())
    render_sidebar_section("🧭 Sección")
    selected_module_key = render_module_nav(modules, active_module.key)
    if selected_module_key != active_module.key:
        selected_module = modules[selected_module_key]
        next_tab = selected_module.default_tab or (selected_module.tabs[0].key if selected_module.tabs else "")
        _set_navigation(selected_module.key, next_tab)

    context = active_module.load_context() if active_module.load_context else {}
    if active_module.render_sidebar:
        maybe_context = active_module.render_sidebar(context)
        if maybe_context is not None:
            context = maybe_context

    top_nav_col, mode_col = st.columns([5.35, 1.65], vertical_alignment="center")
    with top_nav_col:
        selected_tab_key = render_top_nav(active_module, active_tab)
    with mode_col:
        render_mode_indicator()

    if selected_tab_key and active_tab and selected_tab_key != active_tab.key:
        _set_navigation(active_module.key, selected_tab_key)

    if active_tab is None:
        st.info("Este módulo aún no tiene vistas configuradas.")
        return

    active_tab.render(context)


if __name__ == "__main__":
    main()
