import plotly.graph_objects as go
import streamlit as st

from core.charts import chart_config, get_template, render_chart
from .logic import format_currency, format_percent, format_ratio
from .logic import build_balance_snapshot
from .ui_helpers import render_header, render_metric_card


def render(bundle: dict[str, object]) -> None:
    df_contable = bundle["contable"]
    reference_contable = bundle.get("reference_contable", df_contable)
    filters = bundle.get("meta", {}).get("active_filters", {})

    render_header(
        "EEFF Integral",
        "Lectura de balance y ratios principales sobre el mismo modelo contable del reporte financiero.",
    )

    snapshot = build_balance_snapshot(df_contable, reference_contable, filters)
    cards = snapshot["cards"]

    from .ui_helpers import render_info_capsule

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Activos", format_currency(cards["activos"]), "Corte más reciente", explanation="Total de recursos económicos controlados por la empresa.")
    with k2:
        render_metric_card("Pasivos", format_currency(cards["pasivos"]), "Corte más reciente", explanation="Representa las deudas y obligaciones financieras de la entidad.")
    with k3:
        render_metric_card("Patrimonio", format_currency(cards["patrimonio"]), "Corte más reciente", explanation="Capital propio y resultados acumulados pertenecientes a los socios.")
    with k4:
        render_metric_card("Capital de Trabajo", format_currency(cards["capital_trabajo"]), "Activo - Pasivo Corriente", explanation="Recursos disponibles para la operación diaria tras cubrir deudas inmediatas.")

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        render_info_capsule(
            "Composición del Balance",
            "Muestra el desglose de los principales componentes del balance a la fecha de corte.",
            "Visualización horizontal de Activos, Pasivos y Patrimonio."
        )
        components = snapshot["components"]
        if components.empty:
            st.info("No hay datos de balance para la selección actual.")
        else:
            fig = go.Figure(
                go.Bar(
                    x=components["Monto"],
                    y=components["Componente"],
                    orientation="h",
                    marker_color=["#3b82f6", "#1d4ed8", "#ef4444", "#f97316", "#2bb673"],
                )
            )
            fig.update_layout(
                template=get_template(),
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(255,255,255,1)",
                plot_bgcolor="rgba(255,255,255,1)",
                font=dict(color="#14233b"),
            )
            render_chart(fig, use_container_width=True, theme=None, config=chart_config())

    with right_col:
        render_info_capsule(
            "Ratios Financieros",
            "Indicadores clave de liquidez, solvencia y rentabilidad sobre el balance.",
            "Métricas calculadas: Liquidez, Leverage, Endeudamiento, ROA y ROE."
        )
        ratios = snapshot["ratios"].copy()
        if ratios.empty:
            st.info("No hay ratios disponibles.")
        else:
            ratio_formatters = {
                "Liquidez Corriente": format_ratio,
                "Leverage": format_ratio,
                "Endeudamiento": format_percent,
                "ROA": format_percent,
                "ROE": format_percent,
            }
            ratios["Valor"] = ratios.apply(
                lambda row: ratio_formatters.get(row["Ratio"], format_ratio)(row["Valor"]),
                axis=1,
            )
            st.dataframe(ratios, width="stretch", hide_index=True)

        if cards.get("fecha_corte") is not None:
            st.caption(f"Fecha de corte utilizada: {cards['fecha_corte'].date()}")
