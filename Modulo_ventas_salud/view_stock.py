import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import html
from .data import load_advanced_stock_data, load_historical_metrics
from .logic import calculate_advanced_inventory_metrics

def render_metric_card(title, value, meta="", delta=None, delta_label="vs mes anterior", tooltip=None, flip_desc=None):
    """
    delta: float or None. Positive = green ▲, Negative = red ▼.
    """
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        color = "#2bb673" if delta >= 0 else "#ef4444"
        delta_html = f'<div class="metric-delta" style="color:{color};">{arrow} {abs(delta):.1f}% {delta_label}</div>'

    inner_content = f"""<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
{delta_html}
<div class="metric-meta">{meta}</div>"""

    if flip_desc:
        import uuid
        chk_id = f"flip_{uuid.uuid4().hex[:8]}"
        card_html = f"""<label class="flip-card-wrapper" for="{chk_id}">
<input type="checkbox" id="{chk_id}">
<div class="flip-card-inner">
<div class="flip-card-front metric-card">
{inner_content}
</div>
<div class="flip-card-back metric-card">
<div class="flip-card-back-title">{title}</div>
<div class="flip-card-back-desc">{html.escape(flip_desc)}</div>
</div>
</div>
</label>"""
    else:
        card_html = f'<div class="metric-card">{inner_content}</div>'

    st.markdown(card_html, unsafe_allow_html=True)

def render_kpis(df_inv, policy_months):
    """Renderiza los KPIs de stock (sin header, sin gráficos)."""
    # Cálculos
    mask_demanda = df_inv['demanda_promedio'] > 0
    avg_service = df_inv[mask_demanda]['nivel_servicio'].mean() * 100 if any(mask_demanda) else 0
    
    quiebres_count = (df_inv['estado_inventario'].isin(['Sin Stock / Quiebre', 'Quiebre (Bajo Seguridad)'])).sum()
    sobre_stock_count = (df_inv['estado_inventario'] == "Sobre Stock").sum()
    overstock_value = df_inv['valor_sobre_stock'].sum()
    obs_stock_count = ((df_inv['stock_actual'] > 0) & (df_inv['demanda_promedio'] == 0)).sum()
    
    # Nuevos KPIs clave
    stock_total = df_inv['stock_actual'].clip(lower=0).sum()
    stock_valorizado = (df_inv['stock_actual'].clip(lower=0) * df_inv['costo_unitario']).sum()
    venta_prom_total = df_inv['demanda_promedio'].sum()
    meses_inv = (stock_total / venta_prom_total) if venta_prom_total > 0 else 0

    # Fila 1: Stock Total, Stock Valorizado, Meses de Inventario + Nivel Servicio
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            title="Stock Total", 
            value=f"{stock_total:,.0f}", 
            meta="Unidades en bodega",
            flip_desc="Mide la cantidad bruta de cajas/unidades físicas contabilizadas en todas las bodegas. No descuenta mermas ni despachos en tránsito."
        )
    with k2:
        render_metric_card("Stock Valorizado", f"${stock_valorizado/1e6:,.1f}M", "Capital total invertido")
    with k3:
        render_metric_card("Meses de Inventario", f"{meses_inv:.1f}", "Stock / Venta Promedio")
    with k4:
        render_metric_card("Nivel Servicio", f"{avg_service:.1f}%", "Cumplimiento de demanda")

    # Fila 2: KPIs operacionales
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Existencia Crítica", f"{quiebres_count}", "En Quiebre de Stock")
    with m2:
        render_metric_card("Sobre-stock (SKU)", f"{sobre_stock_count}", f"> {policy_months+1} meses de Inv.")
    with m3:
        render_metric_card("Inversión en Exceso", f"${overstock_value/1e6:,.1f}M", "Capital inmovilizado")
    with m4:
        render_metric_card("SKU Sin Demanda", f"{obs_stock_count}", "Stock con 0 vtas (6m)")

def get_waterfall_figure(df_inv):
    """Retorna la figura de cascada de salud de bodega."""
    counts = df_inv['estado_inventario'].value_counts().to_dict()
    total = sum(counts.values())
    val_sobre = counts.get("Sobre Stock", 0)
    val_sin_stk = counts.get("Sin Stock / Quiebre", 0)
    val_bajo_seg = counts.get("Quiebre (Bajo Seguridad)", 0)
    val_sin_dem = counts.get("Sin Demanda/Otros", 0)
    val_saludable = counts.get("Saludable", 0)

    fig_water = go.Figure(go.Waterfall(
        name="Salud",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["Total SKUs", "Sobre Stock", "Sin Stock", "Bajo Seg.", "Sin Demanda", "✅ Saludables"],
        textposition="outside",
        text=[f"{total}", f"-{val_sobre}", f"-{val_sin_stk}", f"-{val_bajo_seg}", f"-{val_sin_dem}", f"{val_saludable}"],
        y=[total, -val_sobre, -val_sin_stk, -val_bajo_seg, -val_sin_dem, 0],
        connector={"line":{"color":"#94a3b8", "dash": "dot"}},
        decreasing={"marker":{"color":"#ef4444"}},
        totals={"marker":{"color":"#2bb673"}},
        increasing={"marker":{"color":"#1e293b"}} # El Total SKUs inicial
    ))
    
    fig_water.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=30, b=20),
        height=420,
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        showlegend=False
    )
    
    # Ajuste de Y-axis temporal para que no corte el texto
    fig_water.update_yaxes(range=[0, total * 1.15], showgrid=True, gridcolor='#f1f5f9')
    
    return fig_water

def get_stock_evo_figure():
    """Retorna la figura del evolutivo de stock con eje dual: barras de stock + línea de meses de inventario."""
    from plotly.subplots import make_subplots
    
    df_hist = load_historical_metrics()
    if df_hist.empty or 'stock' not in df_hist.columns:
        return None
    
    df_hist['fecha'] = pd.to_datetime(df_hist['fecha'])
    
    # Agregar stock y venta totales por mes
    df_evo = df_hist.groupby('fecha').agg({'stock': 'sum', 'venta': 'sum'}).reset_index()
    df_evo = df_evo.sort_values('fecha').tail(12)
    df_evo['mes_label'] = df_evo['fecha'].dt.strftime('%b %Y')
    
    # Calcular Meses de Inventario por mes (stock / venta)
    df_evo['meses_inv'] = df_evo.apply(
        lambda r: r['stock'] / r['venta'] if r['venta'] > 0 else 0, axis=1
    )
    
    # Gráfico con doble eje
    fig_evo = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Eje 1: Barras de Stock (unidades)
    fig_evo.add_trace(
        go.Bar(
            x=df_evo['mes_label'], y=df_evo['stock'],
            name='Stock (Unid.)',
            marker_color='#3b82f6',
            text=df_evo['stock'].apply(lambda x: f'{x/1e3:,.0f}K'),
            textposition='outside'
        ),
        secondary_y=False
    )
    
    # Eje 2: Línea de Meses de Inventario
    fig_evo.add_trace(
        go.Scatter(
            x=df_evo['mes_label'], y=df_evo['meses_inv'],
            name='Meses de Inv.',
            line=dict(color='#ef4444', width=3),
            mode='lines+markers+text',
            text=df_evo['meses_inv'].apply(lambda x: f'{x:.1f}'),
            textposition='top center',
            textfont=dict(color='#ef4444', size=12)
        ),
        secondary_y=True
    )
    
    fig_evo.update_layout(
        template='plotly_white', height=450,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=13)),
        hovermode='x unified'
    )
    fig_evo.update_yaxes(title_text='Unidades en Bodega', showgrid=True, gridcolor='#eee', secondary_y=False)
    fig_evo.update_yaxes(title_text='Meses de Inventario', showgrid=False, secondary_y=True)
    
    return fig_evo

def load_and_calculate(policy_months=3):
    """Carga y calcula métricas de inventario, retorna el DataFrame."""
    df_inv = load_advanced_stock_data()
    if df_inv.empty:
        return df_inv
    return calculate_advanced_inventory_metrics(df_inv, months_policy=policy_months)

def render(global_df=None):
    """Render completo legacy (por si se usa stand-alone)."""
    st.markdown('<div class="header-band">Panel de Inteligencia y Sobre Stock</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuración Logística")
    policy_months = st.sidebar.slider("Política de Inventario (Meses)", 1, 12, 3)
    
    with st.spinner("Calculando sobre-stock y quiebres..."):
        df_inv = load_and_calculate(policy_months)

    if df_inv.empty:
        st.warning("No se pudo cargar la data de inventario.")
        return

    render_kpis(df_inv, policy_months)
    
    # --- GRÁFICOS ---
    st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-top: 20px; margin-bottom: 10px;">
    <div class="section-title" style="margin-bottom: 0;">Análisis de Salud de Bodega</div>
    <div class="capsule-wrapper">
        <input type="checkbox" id="capsule_salud" class="capsule-checkbox">
        <label for="capsule_salud" class="capsule-btn" data-tooltip-text="🔍 Ver metodología">i</label>
        <div class="capsule-content">
            <label for="capsule_salud" class="capsule-close">×</label>
            <div class="capsule-title">📊 Salud de Bodega (Waterfall)</div>
            <div class="capsule-text">
                Este gráfico de cascada descompone el <b>Total de SKUs</b> restando las categorías problemáticas:<br><br>
                • <b>Sobre Stock:</b> SKUs que superan la política definida.<br>
                • <b>Sin Stock:</b> SKUs con 0 existencia.<br>
                • <b>Bajo Seguridad:</b> SKUs bajo el nivel crítico.<br>
                • <b>Sin Demanda:</b> SKUs con stock pero 0 ventas (12m).<br><br>
                El bloque final representa los SKUs en estado <b>Saludable</b>.
            </div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
    st.plotly_chart(get_waterfall_figure(df_inv), use_container_width=True, theme=None)
    
    st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-top: 20px; margin-bottom: 10px;">
    <div class="section-title" style="margin-bottom: 0;">Evolución Histórica del Stock y Cobertura</div>
    <div class="capsule-wrapper">
        <input type="checkbox" id="capsule_evo" class="capsule-checkbox">
        <label for="capsule_evo" class="capsule-btn" data-tooltip-text="📈 Ver análisis">i</label>
        <div class="capsule-content">
            <label for="capsule_evo" class="capsule-close">×</label>
            <div class="capsule-title">📈 Stock vs Cobertura</div>
            <div class="capsule-text">
                Analiza la eficiencia del almacenamiento en el tiempo:<br><br>
                • <b>Barras Azules:</b> Representan la cantidad física total en bodega.<br>
                • <b>Línea Roja:</b> Representa los Meses de Inventario (Cobertura).<br><br>
                <b>Objetivo:</b> Mantener la línea roja estable dentro de la política, independientemente de si las barras crecen (por mayor venta) o disminuyen.
            </div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
    fig_evo = get_stock_evo_figure()
    if fig_evo:
        st.plotly_chart(fig_evo, use_container_width=True, theme=None)
    else:
        st.info('No hay datos históricos de stock disponibles.')
