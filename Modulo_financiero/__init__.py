import pandas as pd
import streamlit as st

from core.components import render_sidebar_divider, render_sidebar_section
from core.registry import ModuleSpec, TabSpec

from .data import load_all_data
from .view_balance import render as render_balance
from .view_eerr import render as render_eerr
from .view_resumen import render as render_resumen


@st.cache_data(show_spinner=False)
def _load_financial_context() -> dict:
    return load_all_data()


def load_context() -> dict:
    return _load_financial_context()


def render_sidebar(context: dict) -> dict:
    render_sidebar_divider()
    render_sidebar_section("🔄 Datos en Caché")
    if st.sidebar.button("Actualizar Parquet Financiero", key="fin_refresh", use_container_width=True):
        with st.spinner("Sincronizando con base de datos..."):
            import Modulo_financiero.consolidar_parquets as consolidar

            consolidar.actualizar_todo()
            _load_financial_context.clear()
            st.cache_data.clear()
        st.rerun()

    render_sidebar_divider()
    render_sidebar_section("🎯 Filtros Financieros")

    active_filters: dict[str, list[str]] = {}
    contable = context.get("contable", pd.DataFrame())
    if not contable.empty:
        for column, filter_key, label in [
            ("centro_costo", "centros_costo", "Centro de costo"),
            ("Nivel_2_CC", "niveles_2_cc", "Nivel 2 CC"),
            ("Nivel_3_CC", "niveles_3_cc", "Nivel 3 CC"),
            ("Nombre_Proyecto", "proyectos", "Proyecto"),
        ]:
            if column in contable.columns:
                options = sorted(contable[column].dropna().astype(str).unique())
                selected = st.sidebar.multiselect(label, options, key=f"fin_{filter_key}")
                if selected:
                    active_filters[filter_key] = selected

    context.setdefault("meta", {})["active_filters"] = active_filters
    return context


def get_module() -> ModuleSpec:
    return ModuleSpec(
        key="financiero",
        label="Financiero",
        sidebar_label="Financiera",
        icon="💰",
        order=20,
        tabs=[
            TabSpec("resumen_fin", "Resumen Ejecutivo", render_resumen, "📊"),
            TabSpec("eerr", "Estado de Resultados", render_eerr, "📑"),
            TabSpec("balance", "Balance", render_balance, "⚖️"),
        ],
        load_context=load_context,
        render_sidebar=render_sidebar,
        default_tab="resumen_fin",
    )
