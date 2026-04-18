import pandas as pd
import streamlit as st

from core.components import render_sidebar_divider, render_sidebar_section
from core.registry import ModuleSpec, TabSpec

from .data import load_data
from .logic import filter_comercial_data
from .view_resumen import render as render_resumen


@st.cache_data(show_spinner=False)
def _load_commercial_context() -> pd.DataFrame:
    return load_data()


def load_context() -> dict:
    return {"commercial_df": _load_commercial_context()}


def render_sidebar(context: dict) -> dict:
    render_sidebar_divider()
    render_sidebar_section("🔄 Sincronización")
    if st.sidebar.button("Actualizar Data Comercial", key="com_refresh", use_container_width=True):
        with st.spinner("Descargando data comercial..."):
            import Modulo_comercial.consolidar_parquets as consolidar

            if consolidar.actualizar_todo():
                _load_commercial_context.clear()
                st.cache_data.clear()
                st.rerun()
            st.error("Error al conectar con la base de datos.")

    render_sidebar_divider()
    render_sidebar_section("🎯 Filtros Comerciales")

    df = context.get("commercial_df", pd.DataFrame())
    active_filters: dict[str, list[str]] = {}
    if not df.empty:
        for column, label in [
            ("vendedor_nombre", "Vendedores"),
            ("categoria_producto", "Categorías"),
            ("marca", "Marcas"),
        ]:
            if column in df.columns:
                selected = st.sidebar.multiselect(
                    label,
                    sorted(df[column].dropna().unique()),
                    key=f"com_{column}",
                )
                if selected:
                    active_filters[column] = selected

    context["commercial_filtered_df"] = filter_comercial_data(df, active_filters)
    return context


def _render_resumen_tab(context: dict) -> None:
    render_resumen(context.get("commercial_filtered_df", context.get("commercial_df", pd.DataFrame())))


def get_module() -> ModuleSpec:
    return ModuleSpec(
        key="comercial",
        label="Comercial",
        sidebar_label="Comercial",
        icon="🤝",
        order=30,
        tabs=[
            TabSpec("resumen_com", "Resumen Ejecutivo", _render_resumen_tab, "📊"),
        ],
        load_context=load_context,
        render_sidebar=render_sidebar,
        default_tab="resumen_com",
    )
