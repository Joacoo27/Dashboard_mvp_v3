import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.charts import chart_config, get_template
from core.components import render_header, render_info_capsule

from .data import load_advanced_stock_data, load_historical_metrics
from .logic import calculate_advanced_inventory_metrics, calculate_evolutionary_kpis, get_health_index_summary


def render(context: dict | None = None) -> None:
    context = context or {}

    render_header(
        "Índice de Salud Master",
        "Score integral de inventario: servicio, disponibilidad, eficiencia y obsolescencia.",
    )

    with st.spinner("Consolidando métricas de salud..."):
        df_inv = context.get("inventory_df")
        if df_inv is None or df_inv.empty:
            df_inv = load_advanced_stock_data()
            df_inv = calculate_advanced_inventory_metrics(df_inv)

        summary = get_health_index_summary(df_inv)
        final_score = summary["Final Score"]
        details_df = summary["Details"]

    left_col, right_col = st.columns([1, 1.8])

    with left_col:
        render_info_capsule(
            "Salud Actual",
            "Resume la calidad global del inventario en un score de 0 a 100.",
            "Promedio ponderado de Nivel de Servicio, Obsolescencia, Disponibilidad y Eficiencia.",
        )

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=final_score,
                domain={"x": [0, 1], "y": [0, 1]},
                number={"font": {"size": 54, "color": "#0A1261", "family": "Inter, sans-serif"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748b"},
                    "bar": {"color": "#0A1261", "thickness": 0.25},
                    "bgcolor": "white",
                    "borderwidth": 1,
                    "bordercolor": "#e2e8f0",
                    "steps": [
                        {"range": [0, 50], "color": "#ff4b4b"},
                        {"range": [50, 80], "color": "#ffa500"},
                        {"range": [80, 100], "color": "#2bb673"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(
            template=get_template(),
            height=300,
            margin=dict(t=20, b=0, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_gauge, use_container_width=True, theme=None, config=chart_config())

    with right_col:
        render_info_capsule(
            "Desglose por Dimensión",
            "Cada pilar contribuye con un 25% al score final.",
            "Se muestran valor real y aporte de cada dimensión al índice maestro.",
        )

        cards = st.columns(4)
        for idx, row in details_df.iterrows():
            with cards[idx]:
                val_pct = row["Valor Real (%)"]
                contrib = row["Contribución (25%)"]
                color = "#22c55e" if val_pct >= 80 else "#f97316" if val_pct >= 50 else "#ef4444"
                st.markdown(
                    f"""
                    <div style="background:white;padding:16px;border-radius:16px;border:1px solid rgba(0,0,0,0.05);box-shadow:0 4px 12px rgba(0,0,0,0.02);height:100%;">
                        <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:8px;letter-spacing:.05em;">{row["Dimensión"]}</div>
                        <div style="font-size:22px;font-weight:900;color:#1e293b;margin-bottom:4px;">{val_pct:.1f}%</div>
                        <div style="font-size:12px;font-weight:700;color:{color};">+{contrib:.1f} pts</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        df_hist = load_historical_metrics()
        df_evo = calculate_evolutionary_kpis(df_hist)
        if not df_evo.empty:
            main_dim = "Nivel de Servicio"
            trend_3m = df_evo[main_dim].iloc[-3:].pct_change().sum() * 100
            trend_status = "favorable" if trend_3m > 0 else "de cuidado"
            weakest_dim = details_df.loc[details_df["Valor Real (%)"].idxmin(), "Dimensión"]
            st.markdown(
                f"""
                <div style="background:#f8fafc;padding:18px;border-radius:16px;border-left:4px solid #3b82f6;margin-top:18px;">
                    <div style="font-size:11px;font-weight:800;color:#3b82f6;text-transform:uppercase;margin-bottom:4px;">Insight Estratégico</div>
                    <div style="font-size:14px;color:#334155;line-height:1.45;">
                        El <b>Nivel de Servicio</b> proyecta una tendencia <b>{trend_status}</b> ({abs(trend_3m):.1f}%).
                        La prioridad operativa hoy está en <b>{weakest_dim}</b> para elevar el score global.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    df_hist = load_historical_metrics()
    df_evo = calculate_evolutionary_kpis(df_hist)
    if df_evo.empty:
        st.warning("No hay suficientes datos históricos para visualizar la evolución estratégica.")
        return

    main_dim = "Nivel de Servicio"
    curr_val = df_evo[main_dim].iloc[-1]
    avg_12m = df_evo[main_dim].mean()
    diff_avg = curr_val - avg_12m
    trend_3m = df_evo[main_dim].iloc[-3:].pct_change().sum() * 100
    trend_status = "creciente" if trend_3m > 0 else "decreciente"
    trend_icon = "📈" if trend_3m > 0 else "📉"

    st.markdown(
        f"""
        <div style="margin-top:8px;margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div class="minor-band-title" style="margin-bottom:0;">Análisis Evolutivo Estratégico</div>
                <div style="background:rgba(59,130,246,.1);color:#3b82f6;padding:4px 12px;border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(59,130,246,.2);">INSIGHT AUTOMÁTICO</div>
            </div>
            <div style="font-size:15px;color:#334155;line-height:1.5;">
                El <b>Nivel de Servicio</b> actual ({curr_val:.1f}%) se encuentra
                <b>{abs(diff_avg):.1f} pts {"debajo" if diff_avg < 0 else "sobre"}</b> del promedio anual,
                con una tendencia <b>{trend_status}</b> en el último trimestre.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_left, hero_right = st.columns([3, 1])
    with hero_right:
        color_stat = "#ef4444" if curr_val < 85 else "#3b82f6"
        label_stat = "BAJO OBJETIVO" if curr_val < 85 else "EN META"
        st.markdown(
            f"""
            <div style="text-align:right;background:white;padding:25px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.03);border:1px solid rgba(0,0,0,0.02);height:100%;display:flex;flex-direction:column;justify-content:center;">
                <div style="font-size:13px;font-weight:700;color:#94a3b8;letter-spacing:.05em;margin-bottom:5px;">{main_dim.upper()}</div>
                <div style="font-size:48px;font-weight:900;color:#0A1261;line-height:1;">{curr_val:.1f}%</div>
                <div style="margin-top:15px;">
                    <span style="background:{color_stat}15;color:{color_stat};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:800;border:1px solid {color_stat}30;">{label_stat}</span>
                </div>
                <div style="margin-top:10px;font-size:12px;color:#64748b;font-weight:600;">
                    {trend_icon} {abs(trend_3m):.1f}% vs Q anterior
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with hero_left:
        fig_hero = go.Figure()
        fig_hero.add_shape(
            type="line",
            x0=0,
            x1=len(df_evo) - 1,
            y0=90,
            y1=90,
            line=dict(color="rgba(239, 68, 68, 0.4)", width=2, dash="dash"),
        )
        fig_hero.add_trace(
            go.Scatter(
                x=df_evo["mes_label"],
                y=df_evo[main_dim],
                mode="lines",
                line=dict(color="#3b82f6", width=4),
                fill="tozeroy",
                fillcolor="rgba(59,130,246,0.08)",
                name="Servicio",
                hovertemplate="%{y:.1f}%<extra></extra>",
            )
        )
        max_idx = df_evo[main_dim].idxmax()
        fig_hero.add_trace(
            go.Scatter(
                x=[df_evo.loc[max_idx, "mes_label"]],
                y=[df_evo.loc[max_idx, main_dim]],
                mode="markers+text",
                text=["MAX"],
                textposition="top center",
                marker=dict(color="#22c55e", size=10, line=dict(color="white", width=2)),
            )
        )
        fig_hero.add_trace(
            go.Scatter(
                x=[df_evo["mes_label"].iloc[-1]],
                y=[df_evo[main_dim].iloc[-1]],
                mode="markers",
                marker=dict(color="#0A1261", size=12, line=dict(color="white", width=3)),
            )
        )
        fig_hero.update_layout(
            template=get_template(),
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94a3b8")),
            yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(0,0,0,0.03)", ticksuffix="%", tickfont=dict(size=11, color="#94a3b8")),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_hero, use_container_width=True, theme=None, config=chart_config())

    st.markdown('<div style="margin-top:30px;margin-bottom:20px;font-size:16px;font-weight:800;color:#1e293b;letter-spacing:-0.02em;">Diagnóstico Operativo de Salud</div>', unsafe_allow_html=True)
    dims_support = [column for column in df_evo.columns if column not in ["mes", "mes_label", main_dim]]
    cols = st.columns(len(dims_support))
    for idx, dim in enumerate(dims_support):
        with cols[idx]:
            curr_dim = df_evo[dim].iloc[-1]
            avg_dim = df_evo[dim].mean()
            diff_dim = curr_dim - avg_dim
            status_color = "#22c55e" if diff_dim >= 0 else "#f97316"
            status_label = "SOBRE MEDIA" if diff_dim >= 0 else "BAJO MEDIA"

            st.markdown(
                f"""
                <div style="background:white;padding:20px;border-radius:18px;box-shadow:0 4px 20px rgba(0,0,0,0.02);border:1px solid rgba(0,0,0,0.03);margin-bottom:10px;">
                    <div style="font-size:12px;font-weight:700;color:#64748b;margin-bottom:5px;">{dim.upper()}</div>
                    <div style="display:flex;align-items:baseline;gap:8px;">
                        <span style="font-size:24px;font-weight:900;color:#1e293b;">{curr_dim:.1f}%</span>
                        <span style="font-size:10px;font-weight:800;color:{status_color};text-transform:uppercase;">● {status_label}</span>
                    </div>
                    <div style="margin-top:15px;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig_spark = px.line(df_evo, x="mes_label", y=dim, color_discrete_sequence=["#94a3b8"])
            fig_spark.update_traces(line=dict(width=2), hoverinfo="skip")
            fig_spark.update_layout(
                template=get_template(),
                height=60,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_spark, use_container_width=True, theme=None, config=chart_config())
