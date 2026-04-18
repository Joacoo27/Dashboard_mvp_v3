import streamlit as st
import plotly.graph_objects as go
import html
import pandas as pd
from core.charts import chart_config, get_template
from .logic import get_comercial_kpis, build_commercial_trends
from .ui_helpers import render_header, render_metric_card, render_info_capsule

EXPLANATIONS = {
    "Venta Real": "Ingresos netos generados por la comercialización de productos en el periodo filtrado.",
    "Margen %": "Relación porcentual de ganancia tras descontar el costo de venta (P×Q - C×Q).",
    "Cumplimiento Ppto.": "Porcentaje de la meta de ventas alcanzado respecto al presupuesto inicial.",
    "Variación vs AA": "Crecimiento o decrecimiento porcentual comparado con el mismo periodo del año anterior (YoY).",
    "Unidades Vendidas": "Cantidad física total de productos despachados en el periodo.",
    "Contribución Margen": "Monto absoluto de utilidad bruta aportada por la operación comercial."
}

def format_currency(value):
    if abs(value) >= 1e9: return f"${value/1e9:,.2f}B"
    if abs(value) >= 1e6: return f"${value/1e6:,.1f}M"
    return f"${value:,.0f}"

def render(df):
    if df.empty:
        st.warning("No hay datos cargados para el Módulo Comercial.")
        return

    render_header(
        "Resumen Comercial Ejecutivo",
        "Análisis de ventas, márgenes y cumplimiento de metas vs presupuesto y año anterior."
    )

    kpis = get_comercial_kpis(df)
    
    # Grid de KPIs con Flip-Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            "Venta Real", 
            format_currency(kpis["monto_real"]), 
            "Periodo Seleccionado",
            explanation=EXPLANATIONS["Venta Real"]
        )
    with k2:
        render_metric_card(
            "Margen %", 
            f"{kpis['margen_pct']:.1f}%", 
            "Sobre Venta Neta",
            delta=None, # Podríamos calcular delta vs AA si quisiéramos
            explanation=EXPLANATIONS["Margen %"]
        )
    with k3:
        render_metric_card(
            "Cumplimiento Ppto.", 
            f"{kpis['cumplimiento_ppto']:.1f}%", 
            "vs Meta definida",
            explanation=EXPLANATIONS["Cumplimiento Ppto."]
        )
    with k4:
        render_metric_card(
            "Variación vs AA", 
            f"{kpis['variacion_aa']:+.1f}%", 
            "Crecimiento YoY",
            explanation=EXPLANATIONS["Variación vs AA"]
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráfico de Tendencia
    st.markdown('<div class="dashboard-nav-gap"></div>', unsafe_allow_html=True)
    render_info_capsule(
        "Evolución Comercial (Venta vs Presupuesto)",
        "Seguimiento mensual del desempeño real contra la meta establecida.",
        "Muestra barras para lo Real y una línea punteada para el Presupuesto."
    )
    
    df_evo = build_commercial_trends(df)
    if not df_evo.empty:
        fig = go.Figure()
        
        # Venta Real
        fig.add_trace(go.Bar(
            x=df_evo['mes_label'], y=df_evo['monto_real'],
            name='Venta Real', marker_color='#3b82f6',
            hovertemplate='%{y:$.2s}'
        ))
        
        # Presupuesto
        fig.add_trace(go.Scatter(
            x=df_evo['mes_label'], y=df_evo['monto_ppto'],
            name='Presupuesto', mode='lines+markers',
            line=dict(color='#ef4444', width=3, dash='dash'),
            hovertemplate='%{y:$.2s}'
        ))

        fig.update_layout(
            template=get_template(), height=420,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            hovermode="x unified",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True, theme=None, config=chart_config())

    # Sección Inferior: Análisis por Dimensión
    st.markdown("<br>", unsafe_allow_html=True)
    l_col, r_col = st.columns(2)
    
    with l_col:
        render_info_capsule(
            "Ventas por Categoría", 
            "Desglose del monto real vendido agrupado por categoría de producto.",
            "Permite identificar las líneas de negocio líderes en facturación."
        )
        cat_data = df.groupby('categoria_producto')['monto_real'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_cat = go.Figure(go.Bar(
            x=cat_data['monto_real'], y=cat_data['categoria_producto'],
            orientation='h', marker_color='#1e293b'
        ))
        fig_cat.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), template=get_template())
        st.plotly_chart(fig_cat, use_container_width=True, theme=None, config=chart_config())

    with r_col:
        render_info_capsule(
            "Ventas por Vendedor", 
            "Ranking de desempeño por ejecutivo comercial.",
            "Muestra los 10 vendedores con mayor monto neto acumulado."
        )
        vend_data = df.groupby('vendedor_nombre')['monto_real'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_vend = go.Figure(go.Bar(
            x=vend_data['monto_real'], y=vend_data['vendedor_nombre'],
            orientation='h', marker_color='#2bb673'
        ))
        fig_vend.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), template=get_template())
        st.plotly_chart(fig_vend, use_container_width=True, theme=None, config=chart_config())
