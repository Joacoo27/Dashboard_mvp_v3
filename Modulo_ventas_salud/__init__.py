from __future__ import annotations

import pandas as pd
import streamlit as st

from core.components import (
    render_sidebar_divider,
    render_sidebar_section,
)
from core.registry import ModuleSpec, TabSpec

from .data import load_data, load_maestro_productos
from .logic import filter_data_v2, process_dataframe
from .view_indice_salud_master import render as render_health_index
from .view_inventario_ventas import load_and_calculate, render as render_inventory_tab


SHORT_MONTH_NAMES = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}


@st.cache_data(show_spinner=False)
def _load_operational_context() -> tuple[pd.DataFrame, pd.DataFrame]:
    sales_df = process_dataframe(load_data())
    maestro_df = load_maestro_productos()
    return sales_df, maestro_df


def _build_period_label(df: pd.DataFrame) -> str:
    if df.empty or "fecha" not in df.columns:
        return "sin datos"
    max_date = pd.to_datetime(df["fecha"]).max()
    return f"{SHORT_MONTH_NAMES.get(max_date.month, max_date.strftime('%b'))}-{max_date.year}"


def _enrich_with_master(df: pd.DataFrame, maestro_df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or maestro_df.empty:
        return df.copy()

    enriched = df.copy()
    enriched["codigo_base"] = (
        enriched["codigo_producto"].astype(str).str.split(" - ").str[0].str.strip().str.upper()
    )
    merged = enriched.merge(maestro_df, left_on="codigo_base", right_on="codigo", how="left")
    for column in ("familia", "proveedor", "tiering", "tecnologia"):
        if column in merged.columns:
            merged[column] = merged[column].fillna("Sin información")
    return merged


def load_context() -> dict:
    sales_df, maestro_df = _load_operational_context()
    return {
        "sales_df": sales_df,
        "maestro_df": maestro_df,
        "period_label": _build_period_label(sales_df),
    }


def render_sidebar(context: dict) -> dict:
    sales_df = context.get("sales_df", pd.DataFrame())
    maestro_df = context.get("maestro_df", pd.DataFrame())

    render_sidebar_divider()
    render_sidebar_section("🔄 Datos en Caché")
    if st.sidebar.button("Actualizar desde BD", key="operacional_refresh", use_container_width=True):
        with st.spinner("Consolidando datos a Parquet..."):
            import Modulo_ventas_salud.consolidar_parquets as consolidar_parquets

            consolidar_parquets.actualizar_todo()
            _load_operational_context.clear()
            st.cache_data.clear()
        st.rerun()

    render_sidebar_divider()
    render_sidebar_section("🎯 Filtros Globales")

    enriched_df = _enrich_with_master(sales_df, maestro_df)

    familias = sorted(enriched_df["familia"].dropna().unique()) if "familia" in enriched_df.columns else []
    proveedores = sorted(enriched_df["proveedor"].dropna().unique()) if "proveedor" in enriched_df.columns else []
    tiering_options = sorted(enriched_df["tiering"].dropna().unique()) if "tiering" in enriched_df.columns else []
    tecnologia_options = sorted(enriched_df["tecnologia"].dropna().unique()) if "tecnologia" in enriched_df.columns else []
    all_products = sorted(enriched_df["codigo_producto"].dropna().unique()) if "codigo_producto" in enriched_df.columns else []

    st.sidebar.markdown('<div class="iw-sidebar-field-label">Familia</div>', unsafe_allow_html=True)
    sel_familias = st.sidebar.pills(
        "Familia",
        familias,
        selection_mode="multi",
        key="operacional_familias",
        label_visibility="collapsed",
        width="stretch",
    )

    st.sidebar.markdown('<div class="iw-sidebar-field-label">Proveedor</div>', unsafe_allow_html=True)
    proveedor = st.sidebar.selectbox(
        "Proveedor",
        ["Todos", *proveedores],
        key="operacional_proveedor",
        label_visibility="collapsed",
    )

    st.sidebar.markdown('<div class="iw-sidebar-field-label">Tiering</div>', unsafe_allow_html=True)
    tiering = st.sidebar.selectbox(
        "Tiering",
        ["Todos", *tiering_options],
        key="operacional_tiering",
        label_visibility="collapsed",
    )

    with st.sidebar.expander("Filtros avanzados", expanded=False):
        selected_products = st.multiselect("Buscador de SKUs", all_products, key="operacional_skus")
        selected_tecnologia = st.multiselect("Tecnología", tecnologia_options, key="operacional_tecnologia")

        min_date = pd.to_datetime(enriched_df["fecha"]).min().date() if not enriched_df.empty else pd.Timestamp.today().date()
        max_date = pd.to_datetime(enriched_df["fecha"]).max().date() if not enriched_df.empty else pd.Timestamp.today().date()
        date_cols = st.columns(2)
        with date_cols[0]:
            start_date = st.date_input("Desde", min_date, min_value=min_date, max_value=max_date, key="operacional_desde")
        with date_cols[1]:
            end_date = st.date_input("Hasta", max_date, min_value=min_date, max_value=max_date, key="operacional_hasta")

    render_sidebar_divider()
    render_sidebar_section("⚙️ Configuración Logística")
    st.sidebar.markdown(
        (
            '<div class="iw-sidebar-inline-label">'
            '<span>Política de Inventario (Meses)</span>'
            '<span class="metric-help" tabindex="0" '
            'data-tooltip="Este parámetro define el umbral de meses de cobertura considerado normal.">i</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    policy_months = st.sidebar.slider(
        "Política de Inventario (Meses)",
        min_value=1,
        max_value=12,
        value=3,
        key="operacional_policy_months",
        label_visibility="collapsed",
    )

    selected_products = locals().get("selected_products", [])
    selected_tecnologia = locals().get("selected_tecnologia", [])
    start_date = locals().get("start_date", pd.to_datetime(enriched_df["fecha"]).min().date() if not enriched_df.empty else pd.Timestamp.today().date())
    end_date = locals().get("end_date", pd.to_datetime(enriched_df["fecha"]).max().date() if not enriched_df.empty else pd.Timestamp.today().date())

    if not enriched_df.empty:
        filtered_df = filter_data_v2(
            enriched_df,
            sorted(enriched_df["canal"].dropna().unique()),
            [start_date, end_date],
            selected_products,
        )
        if sel_familias:
            filtered_df = filtered_df[filtered_df["familia"].isin(sel_familias)]
        if proveedor != "Todos":
            filtered_df = filtered_df[filtered_df["proveedor"] == proveedor]
        if tiering != "Todos":
            filtered_df = filtered_df[filtered_df["tiering"] == tiering]
        if selected_tecnologia:
            filtered_df = filtered_df[filtered_df["tecnologia"].isin(selected_tecnologia)]
    else:
        filtered_df = enriched_df.copy()

    with st.spinner("Sincronizando Stock y Ventas..."):
        inventory_df = load_and_calculate(policy_months)

    context.update(
        {
            "sales_filtered": filtered_df,
            "inventory_df": inventory_df,
            "policy_months": policy_months,
            "period_label": _build_period_label(filtered_df if not filtered_df.empty else sales_df),
        }
    )
    return context
def _render_health_tab(context: dict) -> None:
    render_health_index(context)


def get_module() -> ModuleSpec:
    return ModuleSpec(
        key="operacional",
        label="Ventas y Stock",
        sidebar_label="Operacional",
        icon="📦",
        order=10,
        tabs=[
            TabSpec("inventario", "Inventario y Ventas", render_inventory_tab, "📈"),
            TabSpec("indice_salud", "Índice de Salud Master", _render_health_tab, "🩺"),
        ],
        load_context=load_context,
        render_sidebar=render_sidebar,
        default_tab="inventario",
    )
