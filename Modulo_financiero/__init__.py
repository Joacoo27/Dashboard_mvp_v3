import pandas as pd
import streamlit as st
from datetime import datetime

from core.components import render_sidebar_divider, render_sidebar_section
from core.registry import ModuleSpec, TabSpec

from .data import load_all_data, CONTABLE_PARQUET
from .view_balance import render as render_balance
from .view_eerr import render as render_eerr
from .view_resumen import render as render_resumen


@st.cache_data(show_spinner=False)
def _load_financial_context() -> dict:
    return load_all_data()


def load_context() -> dict:
    return _load_financial_context()


def _parquet_last_updated() -> str | None:
    if CONTABLE_PARQUET.exists():
        ts = datetime.fromtimestamp(CONTABLE_PARQUET.stat().st_mtime)
        return ts.strftime("%d/%m/%Y %H:%M")
    return None


def render_sidebar(context: dict) -> dict:
    render_sidebar_divider()
    render_sidebar_section("🔄 Datos en Caché")

    last_updated = _parquet_last_updated()
    if last_updated:
        st.sidebar.caption(f"Última actualización: {last_updated}")
    else:
        st.sidebar.caption("Sin caché — usando datos demo")

    if st.sidebar.button("Actualizar Parquet Financiero", key="fin_refresh", use_container_width=True):
        try:
            with st.spinner("Sincronizando con base de datos..."):
                import Modulo_financiero.consolidar_parquets as consolidar
                filas = consolidar.actualizar_todo()
                _load_financial_context.clear()
                st.cache_data.clear()
            st.toast(f"Parquet actualizado — {filas:,} filas", icon="✅")
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Error al actualizar: {exc}")

    context.setdefault("meta", {})["active_filters"] = {}
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
