import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from .logic import get_kpis, get_moving_averages

def render_metric_card(title, value, meta=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_kpis(df):
    """Renderiza solo los KPIs de venta (sin header, sin gráfico)."""
    from .data import get_global_obsolete_count
    kpis = get_kpis(df)
    obs_count = get_global_obsolete_count()

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("Frecuencia Cantidad", f"{kpis.get('Total Cantidad', 0):,}", "Unidades Totales")
    with m2:
        render_metric_card("Venta Valorizada", f"${kpis.get('Total Venta', 0)/1e6:.1f}M", "Total CLP")
    with m3:
        render_metric_card("Costo Total", f"${kpis.get('Costo Total', 0)/1e6:.1f}M", "Costo de Venta")
    with m4:
        render_metric_card("Margen Real", f"${kpis.get('Margen Total', 0)/1e6:.1f}M", "Neto acumulado")
    with m5:
        render_metric_card("SKUs Obsoletos", f"{obs_count}", "Sin vtas en 12 meses")

def get_trend_figure(df, metric='venta', label='Venta ($)'):
    """Retorna la figura de tendencia de ventas (soporta valorizado y unidades)."""
    if df.empty or 'fecha' not in df.columns:
        fig = go.Figure()
        fig.update_layout(template="plotly_white", height=420, annotations=[dict(text="Sin datos disponibles", showarrow=False, font=dict(size=18))])
        return fig
    
    # Asegurar que la métrica existe
    if metric not in df.columns:
        metric = 'cantidad' if 'cantidad' in df.columns else df.columns[1]
    
    daily = df.groupby('fecha')[[metric]].sum().reset_index()
    daily = daily.sort_values('fecha')
    daily['promedio_movil_6m'] = daily[metric].rolling(window=6, min_periods=1).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily['fecha'], y=daily[metric], name=f'{label} Real',
                             line=dict(color='#14233b', width=3.5), mode='lines+markers'))
    fig.add_trace(go.Scatter(x=daily['fecha'], y=daily['promedio_movil_6m'], name='Promedio Móvil 6m',
                             line=dict(color='#ff7f0e', width=4, dash='solid')))
    
    fig.update_layout(
        template="plotly_white", 
        height=420, 
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Mes / Año", 
        yaxis_title=label,
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14)),
        hovermode="x unified"
    )
    return fig

def render(df, master_df=None):
    """Render completo legacy (por si se usa stand-alone)."""
    st.markdown('<div class="header-band">Panel Salud del Inventario</div>', unsafe_allow_html=True)
    render_kpis(df)
    st.markdown('<div class="section-title">Evolución Histórica de Unidades vs Tendencia</div>', unsafe_allow_html=True)
    st.plotly_chart(get_trend_figure(df), use_container_width=True, theme=None)
