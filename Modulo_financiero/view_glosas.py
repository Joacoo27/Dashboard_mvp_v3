import streamlit as st

from .logic import format_currency, build_glosas_summary
from .ui_helpers import render_header, render_metric_card, render_info_capsule


def render(bundle: dict[str, object]) -> None:
    df = bundle.get("contable", None)
    if df is None or df.empty:
        st.info("No hay datos contables disponibles.")
        return

    filters = bundle.get("meta", {}).get("active_filters", {})

    render_header(
        "Glosas Consolidadas",
        "Resumen de registros contables, comprobantes y glosas por cuenta y período.",
    )

    search_term = st.text_input("Buscar por cuenta o glosa", value="").strip()
    if search_term:
        mask = (
            df["cuenta_contable"].fillna("").astype(str).str.upper().str.contains(search_term.upper())
            | df.get("Glosas_Consolidadas", df["cuenta_contable"]).fillna("").astype(str).str.upper().str.contains(search_term.upper())
        )
        filtered = df[mask]
    else:
        filtered = df

    summary = build_glosas_summary(filtered)

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card(
            "Registros Contables",
            f"{summary['total_registros']:,}",
            "Total movimientos",
            explanation="Suma de Cantidad_Registros_Contables en la selección actual.",
        )
    with k2:
        render_metric_card(
            "Debe",
            format_currency(summary["movimiento_debe"]),
            "Suma del detalle",
            explanation="Sumatoria de todos los débitos en el período.",
        )
    with k3:
        render_metric_card(
            "Haber",
            format_currency(summary["movimiento_haber"]),
            "Suma del detalle",
            explanation="Sumatoria de todos los créditos en el período.",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        render_info_capsule(
            "Detalle por Cuenta",
            "Glosas consolidadas por cuenta contable y período.",
            "Grano: anio + mes + cuenta_contable.",
        )
        if filtered.empty:
            st.info("No hay datos para la selección actual.")
        else:
            show_cols = [c for c in [
                "anio", "mes", "cuenta_contable", "pcdesc_4",
                "Cantidad_Registros_Contables", "Cantidad_Comprobantes",
                "Cantidad_Glosas", "Glosas_Consolidadas",
                "Cantidad_Usuarios", "Usuarios_Contables",
            ] if c in filtered.columns]
            st.dataframe(filtered[show_cols], width="stretch", hide_index=True)

    with right_col:
        render_info_capsule(
            "Cuentas con más movimiento",
            "Top 10 cuentas por cantidad de registros contables.",
        )
        st.dataframe(summary["top_cuentas"], width="stretch", hide_index=True)
