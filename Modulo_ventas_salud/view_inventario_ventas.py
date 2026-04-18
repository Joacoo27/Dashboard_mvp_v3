import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from core.charts import chart_config, get_template, render_chart
from core.components import render_header, render_info_capsule, render_kicker, render_metric_card

from .data import load_advanced_stock_data, load_historical_metrics
from .logic import calculate_advanced_inventory_metrics, get_kpis


@st.cache_data(show_spinner=False)
def load_and_calculate(policy_months: int = 3) -> pd.DataFrame:
    df_inv = load_advanced_stock_data()
    if df_inv.empty:
        return df_inv
    return calculate_advanced_inventory_metrics(df_inv, months_policy=policy_months)


def get_trend_figure(df: pd.DataFrame, metric: str = "venta", label: str = "Ingreso Real") -> go.Figure:
    if df.empty or "fecha" not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            template=get_template(),
            height=420,
            annotations=[dict(text="Sin datos disponibles", showarrow=False, font=dict(size=18))],
        )
        return fig

    if metric not in df.columns:
        metric = "cantidad" if "cantidad" in df.columns else df.columns[1]

    monthly = df.copy()
    monthly["fecha"] = pd.to_datetime(monthly["fecha"])
    monthly["mes"] = monthly["fecha"].dt.to_period("M").dt.to_timestamp()
    monthly = monthly.groupby("mes")[[metric]].sum().reset_index().sort_values("mes")
    monthly["promedio_movil_6m"] = monthly[metric].rolling(window=6, min_periods=1).mean()
    monthly["mes_label"] = monthly["mes"].dt.strftime("%b %Y")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly["mes_label"],
            y=monthly[metric],
            name=label,
            marker_color="#3b82f6",
            hovertemplate="%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["mes_label"],
            y=monthly["promedio_movil_6m"],
            name="Promedio móvil 6m",
            line=dict(color="#ef4444", width=3, dash="dot"),
            mode="lines+markers",
            hovertemplate="%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        template=get_template(),
        height=420,
        margin=dict(l=10, r=10, t=18, b=10),
        xaxis_title="",
        yaxis_title="",
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=12)),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(20,35,59,0.08)")
    return fig


def get_waterfall_figure(df_inv: pd.DataFrame) -> go.Figure:
    counts = df_inv["estado_inventario"].value_counts().to_dict()
    total = sum(counts.values())
    val_sobre = counts.get("Sobre Stock", 0)
    val_sin_stk = counts.get("Sin Stock / Quiebre", 0)
    val_bajo_seg = counts.get("Quiebre (Bajo Seguridad)", 0)
    val_sin_dem = counts.get("Sin Demanda/Otros", 0)
    val_saludable = counts.get("Saludable", 0)

    fig = go.Figure(
        go.Waterfall(
            name="Salud",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Total SKUs", "Sobre Stock", "Sin Stock", "Bajo Seg.", "Sin Demanda", "✅ Saludables"],
            textposition="outside",
            text=[
                f"{total}",
                f"-{val_sobre}",
                f"-{val_sin_stk}",
                f"-{val_bajo_seg}",
                f"-{val_sin_dem}",
                f"{val_saludable}",
            ],
            y=[total, -val_sobre, -val_sin_stk, -val_bajo_seg, -val_sin_dem, 0],
            connector={"line": {"color": "#94a3b8", "dash": "dot"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#2bb673"}},
            increasing={"marker": {"color": "#1e293b"}},
        )
    )
    fig.update_layout(
        template=get_template(),
        margin=dict(l=10, r=10, t=30, b=20),
        height=420,
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        showlegend=False,
    )
    fig.update_yaxes(range=[0, total * 1.15], showgrid=True, gridcolor="#f1f5f9")
    return fig


def get_stock_evo_figure() -> go.Figure | None:
    df_hist = load_historical_metrics()
    if df_hist.empty or "stock" not in df_hist.columns:
        return None

    df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
    df_evo = df_hist.groupby("fecha").agg({"stock": "sum", "venta": "sum"}).reset_index()
    df_evo = df_evo.sort_values("fecha").tail(12)
    df_evo["mes_label"] = df_evo["fecha"].dt.strftime("%b %Y")
    df_evo["meses_inv"] = df_evo.apply(lambda row: row["stock"] / row["venta"] if row["venta"] > 0 else 0, axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df_evo["mes_label"],
            y=df_evo["stock"],
            name="Stock (Unid.)",
            marker_color="#3b82f6",
            text=df_evo["stock"].apply(lambda value: f"{value/1e3:,.0f}K"),
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_evo["mes_label"],
            y=df_evo["meses_inv"],
            name="Meses de Inv.",
            line=dict(color="#ef4444", width=3),
            mode="lines+markers+text",
            text=df_evo["meses_inv"].apply(lambda value: f"{value:.1f}"),
            textposition="top center",
            textfont=dict(color="#ef4444", size=12),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        template=get_template(),
        height=450,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color="#14233b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=13)),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Unidades en Bodega", showgrid=True, gridcolor="#eee", secondary_y=False)
    fig.update_yaxes(title_text="Meses de Inventario", showgrid=False, secondary_y=True)
    return fig


def render(context: dict) -> None:
    sales_df = context.get("sales_filtered", pd.DataFrame())
    inventory_df = context.get("inventory_df", pd.DataFrame())
    period_label = context.get("period_label", "sin datos")

    if sales_df.empty:
        st.warning("No se pudieron recuperar datos de ventas para la selección actual.")
        return

    render_header(
        "Panel de Venta y Stock",
        f"Visión estratégica de ventas e inventario — corte {period_label}.",
    )

    if inventory_df.empty:
        st.warning("No se pudo cargar la data de inventario.")
        return

    kpis = get_kpis(sales_df)
    venta_total = kpis.get("Total Venta", 0)
    stock_total = inventory_df["stock_actual"].clip(lower=0).sum()
    stock_val = (inventory_df["stock_actual"].clip(lower=0) * inventory_df["costo_unitario"]).sum()
    venta_prom = inventory_df["demanda_promedio"].sum()
    meses_inv = (stock_total / venta_prom) if venta_prom > 0 else 0
    mask_dem = inventory_df["demanda_promedio"] > 0
    nivel_servicio = inventory_df[mask_dem]["nivel_servicio"].mean() * 100 if any(mask_dem) else 0
    quiebres = inventory_df["estado_inventario"].isin(["Sin Stock / Quiebre", "Quiebre (Bajo Seguridad)"]).sum()
    inversion_exceso = inventory_df["valor_sobre_stock"].sum()
    sin_demanda = ((inventory_df["stock_actual"] > 0) & (inventory_df["demanda_promedio"] == 0)).sum()

    metric_help = {
        "Venta Valorizada": "Monto total vendido en el periodo filtrado.",
        "Stock Valorizado": "Capital invertido en inventario disponible.",
        "Meses de Inventario": "Cuántos meses alcanzaría el stock al ritmo promedio de venta.",
        "Nivel de Servicio": "Porcentaje de demanda que puede cubrirse con el stock disponible.",
        "Stock en Unidades": "Cantidad física total de unidades disponibles en bodega.",
        "SKUs en Quiebre": "Cantidad de SKUs sin stock o bajo el nivel de seguridad definido.",
        "Inversión en Exceso": "Capital inmovilizado en stock por sobre la política definida.",
        "SKUs sin Demanda": "Cantidad de SKUs con stock, pero sin venta en la ventana analizada.",
    }

    def pct_delta(curr: float, prev: float) -> float | None:
        if prev and prev != 0:
            return ((curr - prev) / abs(prev)) * 100
        return None

    d_stock_val = d_stock_tot = d_meses = d_venta = None
    hist_df = load_historical_metrics()
    if not hist_df.empty:
        hist_df["fecha"] = pd.to_datetime(hist_df["fecha"])
        monthly = hist_df.groupby("fecha").agg({"stock": "sum", "venta": "sum"}).reset_index().sort_values("fecha")
        if len(monthly) >= 2:
            curr_row, prev_row = monthly.iloc[-1], monthly.iloc[-2]
            avg_cost = inventory_df["costo_unitario"].mean() if not inventory_df.empty else 0
            d_stock_tot = pct_delta(curr_row["stock"], prev_row["stock"])
            d_stock_val = pct_delta(curr_row["stock"] * avg_cost, prev_row["stock"] * avg_cost)
            d_meses = pct_delta(
                curr_row["stock"] / curr_row["venta"] if curr_row["venta"] > 0 else 0,
                prev_row["stock"] / prev_row["venta"] if prev_row["venta"] > 0 else 0,
            )
            d_venta = pct_delta(curr_row["venta"], prev_row["venta"])

    render_kicker("VISIÓN ESTRATÉGICA")
    top_row = st.columns(4)
    with top_row[0]:
        render_metric_card("Venta Valorizada", f"${venta_total/1e6:,.1f}M", "Total acumulado CLP", delta=d_venta, delta_label="vs mes anterior", explanation=metric_help["Venta Valorizada"])
    with top_row[1]:
        render_metric_card("Stock Valorizado", f"${stock_val/1e6:,.1f}M", "Capital invertido", delta=d_stock_val, delta_label="vs mes anterior", explanation=metric_help["Stock Valorizado"])
    with top_row[2]:
        render_metric_card("Meses de Inventario", f"{meses_inv:.1f}", "Cobertura promedio", delta=d_meses, delta_label="vs mes anterior", explanation=metric_help["Meses de Inventario"])
    with top_row[3]:
        render_metric_card("Nivel de Servicio", f"{nivel_servicio:.1f}%", "SKUs con demanda", explanation=metric_help["Nivel de Servicio"])

    st.markdown('<div class="metric-row-gap"></div>', unsafe_allow_html=True)
    render_kicker("ALERTAS OPERACIONALES")
    bottom_row = st.columns(4)
    with bottom_row[0]:
        render_metric_card("Stock en Unidades", f"{stock_total:,.0f}", "Total existencias", delta=d_stock_tot, delta_label="vs mes anterior", explanation=metric_help["Stock en Unidades"])
    with bottom_row[1]:
        render_metric_card("SKUs en Quiebre", f"{quiebres}", "Existencia crítica", explanation=metric_help["SKUs en Quiebre"])
    with bottom_row[2]:
        render_metric_card("Inversión en Exceso", f"${inversion_exceso/1e6:,.1f}M", "Sobre política", explanation=metric_help["Inversión en Exceso"])
    with bottom_row[3]:
        render_metric_card("SKUs sin Demanda", f"{sin_demanda}", "Con stock, sin venta", explanation=metric_help["SKUs sin Demanda"])

    st.markdown('<div class="metrics-divider"></div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.25, 1])
    with left_col:
        render_info_capsule(
            "Evolutivo de Ingresos",
            "Seguimiento mensual de ventas con una referencia de tendencia móvil para lectura ejecutiva.",
            "Barras de venta real y línea punteada de promedio móvil de 6 meses.",
        )
        render_chart(
            get_trend_figure(sales_df, metric="venta", label="Ingreso Real"),
            use_container_width=True,
            theme=None,
            config=chart_config(),
        )
    with right_col:
        render_info_capsule(
            "Análisis de Salud de Bodega",
            "Descompone el mix total de SKUs y muestra cuánto se pierde por sobrestock, quiebres y baja rotación.",
            "Gráfico de cascada con SKUs problemáticos y bloque final saludable.",
        )
        render_chart(
            get_waterfall_figure(inventory_df),
            use_container_width=True,
            theme=None,
            config=chart_config(),
        )

    st.markdown('<div class="metric-row-gap"></div>', unsafe_allow_html=True)
    render_info_capsule(
        "Stock y Cobertura",
        "Evolución del stock físico y de los meses de cobertura para validar consistencia operacional.",
        "Barras de stock en unidades y línea de meses de inventario.",
    )
    stock_evo = get_stock_evo_figure()
    if stock_evo is None:
        st.info("No hay datos históricos de stock disponibles.")
    else:
        render_chart(stock_evo, use_container_width=True, theme=None, config=chart_config())
