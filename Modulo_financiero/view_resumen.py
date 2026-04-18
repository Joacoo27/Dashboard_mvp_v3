import plotly.graph_objects as go
import streamlit as st

from core.charts import chart_config, get_template, render_chart
from .logic import format_currency, format_percent, format_ratio
from .logic import build_resumen_dashboard, build_resumen_trends
from .ui_helpers import render_header, render_metric_card


EXPLANATIONS = {
    "Crecimiento de Ingresos": "Variación porcentual de la facturación neta comparada con el mismo período del año anterior.",
    "EBITDA": "Beneficio antes de intereses, impuestos, depreciaciones y amortizaciones. Refleja la rentabilidad operativa pura del negocio.",
    "Margen Bruto": "Porcentaje de utilidad sobre la facturación tras descontar el costo directo de ventas (COGS).",
    "Margen Operacional": "Ratio que mide cuánto beneficio obtiene la empresa por cada peso de venta, tras descontar gastos de administración y ventas.",
    "Caja / Liquidez": "Ratio de disponibilidad inmediata de efectivo frente a obligaciones. Indica la capacidad de pago a corto plazo.",
    "ROA": "Rentabilidad sobre Activos. Mide la eficiencia en el uso de los recursos totales de la empresa.",
    "ROE": "Rentabilidad sobre Patrimonio. Mide el retorno para los accionistas sobre su capital invertido.",
    "Resultado del Ejercicio": "Utilidad neta final del período tras descontar todos los costos, gastos e impuestos."
}

def _render_summary_card(card: dict[str, object]) -> None:
    value_type = card.get("value_type")
    meta = card.get("meta", "")
    title = card["title"]
    
    if card.get("extra_meta_type") == "currency":
        meta = f"Caja al cierre: {format_currency(card.get('extra_meta_value', 0.0))}"

    if value_type == "percent":
        value = format_percent(card["value"])
        delta = card.get("delta", 0.0) * 100
    elif value_type == "ratio":
        value = format_ratio(card["value"])
        delta = None
    else:
        value = format_currency(card["value"])
        delta = card.get("delta")
        delta = delta * 100 if delta is not None else None

    render_metric_card(
        title,
        value,
        meta,
        delta=delta,
        delta_label=card.get("delta_label", "vs referencia"),
        explanation=EXPLANATIONS.get(title, "Métrica clave del reporte financiero.")
    )


def render(bundle: dict[str, object]) -> None:
    df_contable = bundle["contable"]
    reference_contable = bundle.get("reference_contable", df_contable)
    filters = bundle.get("meta", {}).get("active_filters", {})

    from .ui_helpers import render_info_capsule
    render_header(
        "Resumen Ejecutivo",
        "Tarjetas del mes actual y evolutivos principales del reporte financiero.",
    )

    summary = build_resumen_dashboard(df_contable, reference_contable, filters)
    trend_data = build_resumen_trends(df_contable, reference_contable, filters)
    trend_df = trend_data["trend"]

    st.markdown(
        f'<div class="summary-kicker">Corte actual: {summary["period_label"]}</div>',
        unsafe_allow_html=True,
    )

    top_row = st.columns(4)
    for column, card in zip(top_row, summary["cards"][:4]):
        with column:
            _render_summary_card(card)

    bottom_row = st.columns(4)
    for column, card in zip(bottom_row, summary["cards"][4:]):
        with column:
            _render_summary_card(card)

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns(2)

    with left_col:
        render_info_capsule(
            "Evolutivo de Ingresos",
            "Muestra la trayectoria de los ingresos reales comparados con el presupuesto definido.",
            "Ingreso Real (Barras) vs Ingreso Presupuesto (Línea Roja)."
        )
        if trend_df.empty:
            st.info("No hay datos contables para construir el evolutivo de ingresos.")
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=trend_df["mes_label"],
                    y=trend_df["ingresos_real"],
                    name="Ingreso Real",
                    marker_color="#3b82f6",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=trend_df["mes_label"],
                    y=trend_df["ingresos_ppto"],
                    name="Ingreso Presupuesto",
                    line=dict(color="#ef4444", width=3, dash="dash"),
                    mode="lines",
                )
            )
            fig.update_layout(
                template=get_template(),
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                hovermode="x unified",
                legend=dict(orientation="h", x=0.5, xanchor="center", y=1.12),
                paper_bgcolor="rgba(255,255,255,1)",
                plot_bgcolor="rgba(255,255,255,1)",
                font=dict(color="#14233b"),
            )
            render_chart(fig, use_container_width=True, theme=None, config=chart_config())

    with right_col:
        render_info_capsule(
            "Evolutivo de Margen Bruto",
            "Muestra la evolución monetaria y porcentual del margen bruto mensual.",
            "Margen Bruto (Barras) vs % Margen (Línea con marcadores)."
        )
        if trend_df.empty:
            st.info("No hay datos contables para construir el evolutivo de margen bruto.")
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=trend_df["mes_label"],
                    y=trend_df["margen_bruto_real"],
                    name="Margen Bruto",
                    marker_color="#2bb673",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=trend_df["mes_label"],
                    y=trend_df["margen_bruto_pct"] * 100,
                    name="% Margen Bruto",
                    line=dict(color="#0A1261", width=3),
                    mode="lines+markers",
                    yaxis="y2",
                )
            )
            fig.update_layout(
                template=get_template(),
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                hovermode="x unified",
                legend=dict(orientation="h", x=0.5, xanchor="center", y=1.12),
                paper_bgcolor="rgba(255,255,255,1)",
                plot_bgcolor="rgba(255,255,255,1)",
                font=dict(color="#14233b"),
                yaxis2=dict(overlaying="y", side="right", title="%", range=[0, 105]),
            )
            render_chart(fig, use_container_width=True, theme=None, config=chart_config())
