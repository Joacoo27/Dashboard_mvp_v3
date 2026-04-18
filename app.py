import streamlit as st
import pandas as pd
import os
from Modulo_ventas_salud.data import load_data
from Modulo_ventas_salud.logic import process_dataframe, filter_data_v2, get_kpis
import Modulo_ventas_salud.view_salud as view_salud # Importamos la Slide 1
import Modulo_ventas_salud.view_stock as view_stock # Importamos la Slide 2
import Modulo_ventas_salud.view_indice as view_indice # Importamos la Slide 3
import Modulo_ventas_salud.view_glosario as view_glosario # Importamos la Slide 4

# --- Configuración Global ---
st.set_page_config(
    page_title="Panel de Interwins",
    page_icon="📊",
    layout="wide",
)

# --- CSS Estándar (Compartido por todas las slides) ---
st.markdown(
    """
    <style>
    :root {
        --ink: #14233b;
        --brand: #1e3a8a;
        --title-navy: #0A1261;
        --bg: #fcfbf7;
        --panel-bg: #fffdf8;
        --accent: #3b82f6;
        --surface: rgba(255, 255, 255, 0.96);
        --surface-soft: rgba(255, 255, 255, 0.82);
        --border-soft: rgba(30, 58, 138, 0.12);
        --border-strong: rgba(59, 130, 246, 0.55);
        --shadow-soft: 0 10px 30px rgba(20, 35, 59, 0.05);
        --shadow-strong: 0 18px 38px rgba(20, 35, 59, 0.10);
        --focus-ring: 0 0 0 3px rgba(59, 130, 246, 0.16);
        --radius-sm: 14px;
        --radius-md: 18px;
        --radius-lg: 22px;
    }
    html, body, [class*="css"] {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        scrollbar-color: rgba(59, 130, 246, 0.48) rgba(226, 234, 247, 0.76);
        scrollbar-width: thin;
    }
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(226, 234, 247, 0.72);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(59, 130, 246, 0.42), rgba(30, 58, 138, 0.48));
        border: 3px solid rgba(248, 250, 253, 0.96);
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, rgba(59, 130, 246, 0.58), rgba(30, 58, 138, 0.62));
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.07), transparent 28%),
            radial-gradient(circle at top right, rgba(30, 58, 138, 0.05), transparent 22%),
            var(--bg);
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.07), transparent 28%),
            radial-gradient(circle at top right, rgba(30, 58, 138, 0.05), transparent 22%),
            var(--panel-bg) !important;
    }
    .block-container { padding-top: 1.35rem; max-width: 1550px; }
    .dashboard-nav-gap {
        height: 0.35rem;
    }
    [data-testid="stHeader"] {
        background: rgba(248, 250, 253, 0.94);
        border-bottom: 1px solid rgba(30, 58, 138, 0.08);
        backdrop-filter: blur(12px);
    }
    [data-testid="stHeader"] *,
    [data-testid="stToolbar"] * {
        color: var(--ink) !important;
    }
    [data-testid="stHeader"] button {
        appearance: none;
        -webkit-appearance: none;
        border-radius: 999px !important;
        border: 1px solid rgba(30, 58, 138, 0.12) !important;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(245, 249, 255, 0.96)) !important;
        box-shadow: 0 10px 24px rgba(20, 35, 59, 0.06) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }
    [data-testid="stHeader"] button:hover {
        transform: translateY(-1px);
        border-color: rgba(59, 130, 246, 0.35) !important;
        box-shadow: 0 14px 28px rgba(20, 35, 59, 0.10) !important;
    }
    [data-testid="stHeader"] button:focus-visible {
        outline: none;
        box-shadow: var(--focus-ring), 0 10px 24px rgba(20, 35, 59, 0.06) !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1261 0%, #0A1261 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0.35rem;
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 0.97rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1 {
        font-size: clamp(1.5rem, 2vw, 1.9rem);
        letter-spacing: -0.03em;
        margin-bottom: 0.35rem;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h3 {
        font-size: 1.02rem;
        letter-spacing: -0.01em;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] legend {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.12);
    }
    .sidebar-image-placeholder {
        width: 100%;
        height: 72px;
        border: 1.5px dashed rgba(255, 255, 255, 0.36);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.1rem 0 1rem;
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.82);
        font-size: 0.86rem;
        font-weight: 700;
        text-align: center;
        padding: 0.75rem;
        box-sizing: border-box;
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="collapsedControl"] {
        appearance: none;
        -webkit-appearance: none;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(245, 249, 255, 0.96));
        color: var(--ink) !important;
        font-weight: 700;
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-sm);
        min-height: 2.85rem;
        padding: 0.55rem 1rem;
        box-shadow: var(--shadow-soft);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }
    [data-testid="stSidebar"] .stButton > button *,
    [data-testid="collapsedControl"] * {
        color: var(--ink) !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="collapsedControl"]:hover {
        transform: translateY(-1px);
        border-color: var(--border-strong);
        box-shadow: var(--shadow-strong);
    }
    [data-testid="stSidebar"] .stButton > button:focus-visible,
    [data-testid="collapsedControl"]:focus-visible {
        outline: none;
        box-shadow: var(--focus-ring), var(--shadow-soft);
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="input"],
    [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"] {
        appearance: none;
        -webkit-appearance: none;
        min-height: 3rem;
        border-radius: var(--radius-sm);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 250, 255, 0.96));
        border: 1px solid var(--border-soft);
        box-shadow: var(--shadow-soft);
        transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div:hover,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="input"]:hover,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"]:hover {
        border-color: rgba(59, 130, 246, 0.32);
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div:focus-within,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="input"]:focus-within,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"]:focus-within {
        border-color: var(--border-strong);
        box-shadow: var(--focus-ring), var(--shadow-soft);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] .stMultiSelect input[role="combobox"],
    [data-testid="stSidebar"] input[data-testid="stDateInputField"] {
        appearance: none;
        -webkit-appearance: none;
        background: transparent !important;
        color: var(--ink) !important;
        font-size: 0.82rem !important; /* Reducido para evitar truncamiento */
        font-weight: 600;
        padding-left: 0.5rem !important;
    }
    [data-testid="stSidebar"] input[data-testid="stDateInputField"]::placeholder,
    [data-testid="stSidebar"] .stMultiSelect input[role="combobox"]::placeholder {
        color: #7a8aa8;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] *,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] *,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"] * {
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] div,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] span,
    [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"] span {
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
        background: rgba(59, 130, 246, 0.11) !important;
        border: 1px solid rgba(59, 130, 246, 0.18) !important;
        border-radius: 999px !important;
        color: var(--ink) !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] * {
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] svg,
    [data-testid="stSidebar"] .stDateInput svg {
        fill: var(--ink);
        width: 14px !important; /* Icono más pequeño para dar espacio */
    }
    /* Estilos para el botón de formulario en sidebar */
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
        background: rgba(59, 130, 246, 0.85) !important;
        color: white !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button:hover {
        background: #3b82f6 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    [data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.7rem;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"] {
        position: relative;
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-sm);
        padding: 0.52rem 0.82rem;
        box-shadow: 0 6px 18px rgba(30, 58, 138, 0.04);
        transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, transform 0.18s ease;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        transform: translateY(-1px);
        border-color: rgba(59, 130, 246, 0.55);
        box-shadow: 0 10px 24px rgba(59, 130, 246, 0.08);
    }
    [data-testid="stRadio"] label[data-baseweb="radio"] p {
        color: var(--ink) !important;
        font-weight: 600;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"] input[type="radio"] {
        position: absolute;
        opacity: 0;
        inset: 0;
        pointer-events: none;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        width: 1.1rem;
        min-width: 1.1rem;
        height: 1.1rem;
        border-radius: 50%;
        background: #fff;
        border: 1.5px solid rgba(20, 35, 59, 0.22);
        box-shadow: inset 0 0 0 3px #fff;
        transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child > div {
        width: 0.46rem;
        height: 0.46rem;
        border-radius: 50%;
        background: var(--accent);
        transform: scale(0);
        opacity: 0;
        transition: transform 0.18s ease, opacity 0.18s ease;
    }
    [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(59, 130, 246, 0.09);
        border-color: rgba(59, 130, 246, 0.65);
        box-shadow: 0 12px 28px rgba(59, 130, 246, 0.10);
    }
    [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) > div:first-child {
        border-color: var(--accent);
        background: rgba(59, 130, 246, 0.10);
        box-shadow: inset 0 0 0 3px rgba(255, 255, 255, 0.95);
    }
    [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) > div:first-child > div {
        transform: scale(1);
        opacity: 1;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        padding: 4px 12px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: rgba(59, 130, 246, 0.35) !important;
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.2) !important;
    }
    [data-testid="stMain"] .stButton > button[kind="secondary"] {
        appearance: none;
        -webkit-appearance: none;
        background: rgba(255, 255, 255, 0.98) !important;
        color: #111827 !important;
        border: 1px solid rgba(20, 35, 59, 0.14) !important;
        border-radius: 14px !important;
        height: 3.2rem !important;
        min-height: 3.2rem !important;
        padding: 0.45rem 1rem !important;
        font-weight: 900 !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 12px 28px rgba(20, 35, 59, 0.06) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease !important;
    }
    [data-testid="stMain"] .stButton > button[kind="secondary"]:hover {
        transform: translateY(-1px);
        border-color: rgba(20, 35, 59, 0.24) !important;
        box-shadow: 0 14px 30px rgba(20, 35, 59, 0.10) !important;
    }
    [data-testid="stMain"] .stButton > button[kind="primary"] {
        appearance: none;
        -webkit-appearance: none;
        background: #0A1261 !important;
        color: #ffffff !important;
        border: 1px solid rgba(10, 18, 97, 0.95) !important;
        border-radius: 14px !important;
        height: 3.2rem !important;
        min-height: 3.2rem !important;
        padding: 0.45rem 1rem !important;
        font-weight: 900 !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 16px 34px rgba(10, 18, 97, 0.22) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
    }
    [data-testid="stMain"] .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 18px 38px rgba(10, 18, 97, 0.28) !important;
    }
    [data-testid="stMain"] .stButton > button[kind="primary"]:focus-visible,
    [data-testid="stMain"] .stButton > button[kind="secondary"]:focus-visible {
        outline: none !important;
        box-shadow: var(--focus-ring), 0 12px 28px rgba(20, 35, 59, 0.08) !important;
    }
    [data-testid="stSlider"] {
        padding-top: 0.1rem;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] {
        padding: 0.1rem 0 0.25rem;
    }
    [data-testid="stSlider"] [role="slider"] {
        width: 1.2rem !important;
        height: 1.2rem !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, var(--accent), var(--brand)) !important;
        border: 2px solid rgba(255, 255, 255, 0.98) !important;
        box-shadow: 0 10px 22px rgba(30, 58, 138, 0.18) !important;
    }
    [data-testid="stSlider"] [role="slider"]:focus-visible {
        outline: none !important;
        box-shadow: var(--focus-ring), 0 10px 22px rgba(30, 58, 138, 0.18) !important;
    }
    [data-testid="stSlider"] [role="slider"] > div {
        background: linear-gradient(135deg, var(--ink), var(--brand)) !important;
        border-radius: 999px !important;
        padding: 0.12rem 0.45rem !important;
        min-width: 1.8rem;
        box-shadow: 0 10px 24px rgba(20, 35, 59, 0.16);
    }
    [data-testid="stSlider"] [role="slider"] > div p {
        color: #fff !important;
        font-weight: 700;
        font-size: 0.82rem;
    }
    [data-testid="stSlider"] [role="slider"] ~ div {
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.22), rgba(30, 58, 138, 0.12)) !important;
        border-radius: 999px !important;
        box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.10);
    }
    [data-testid="stSliderTickBar"] p {
        color: #7283a2 !important;
        font-weight: 700;
        font-size: 0.8rem;
    }
    [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.98);
        border: 1px solid rgba(30, 58, 138, 0.08);
        border-radius: 22px;
        box-shadow: 0 16px 40px rgba(20, 35, 59, 0.06);
        padding: 12px 14px 6px;
        overflow: hidden;
    }
    [data-testid="stPlotlyChart"] > div,
    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .plot-container,
    [data-testid="stPlotlyChart"] .svg-container {
        background: transparent !important;
    }
    [data-testid="stPlotlyChart"] .modebar {
        background: rgba(255, 255, 255, 0.85) !important;
        border-radius: 999px !important;
        box-shadow: 0 8px 20px rgba(20, 35, 59, 0.08);
    }
    [data-testid="stPlotlyChart"] .modebar-btn path,
    [data-testid="stPlotlyChart"] .modebar-btn svg {
        fill: var(--ink) !important;
    }
    
    .header-band {
        background: #0A1261;
        color: white;
        padding: 24px 35px;
        border-radius: 12px;
        font-size: clamp(1.7rem, 2.2vw, 2.2rem);
        font-weight: 800;
        width: 100%;
        box-sizing: border-box;
        min-height: 4.5rem;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        text-align: left;
        box-shadow: 0 10px 30px rgba(20, 35, 59, 0.14);
        border-left: 6px solid var(--accent);
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 24px 22px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        width: 100%;
        height: 184px;
        min-height: 184px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 0.45rem;
        position: relative;
        overflow: visible;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-sizing: border-box;
    }
    .flip-card-wrapper input[type="checkbox"]:not(:checked) ~ .flip-card-inner .metric-card:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 12px 40px rgba(0,0,0,0.08); 
        border-color: var(--accent); 
    }
    .metric-card:focus,
    .metric-card:focus-visible { outline: none; }
    .metric-card > div {
        width: 100%;
    }
    .metric-title {
        color: #64748b;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        min-height: 2.4rem;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .metric-value {
        color: var(--ink);
        font-size: clamp(2.1rem, 2.7vw, 3.2rem);
        line-height: 1.05;
        font-weight: 800;
        min-height: 3.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }
    .metric-delta {
        font-size: 13px;
        font-weight: 700;
        min-height: 1.15rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .metric-meta {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        min-height: 1.15rem;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .metric-help {
        position: absolute;
        top: 14px;
        right: 14px;
        width: 19px;
        height: 19px;
        border-radius: 50%;
        background: rgba(10, 18, 97, 0.08);
        border: 1px solid rgba(10, 18, 97, 0.18);
        color: #0A1261;
        font-size: 11px;
        font-weight: 800;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: help;
        z-index: 3;
        transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }
    .metric-help:hover,
    .metric-help:focus-visible {
        background: rgba(10, 18, 97, 0.14);
        border-color: rgba(10, 18, 97, 0.30);
        transform: translateY(-1px);
        outline: none;
    }
    .metric-help::after {
        content: attr(data-tooltip);
        position: absolute;
        top: calc(100% + 9px);
        right: 0;
        width: 230px;
        padding: 0.7rem 0.8rem;
        border-radius: 12px;
        background: rgba(20, 35, 59, 0.98);
        color: #ffffff;
        font-size: 12px;
        font-weight: 600;
        line-height: 1.4;
        text-transform: none;
        letter-spacing: 0;
        box-shadow: 0 14px 30px rgba(20, 35, 59, 0.20);
        opacity: 0;
        visibility: hidden;
        transform: translateY(-4px);
        transition: opacity 0.18s ease, transform 0.18s ease, visibility 0.18s ease;
        pointer-events: none;
        text-align: left;
    }
    .metric-help::before {
        content: "";
        position: absolute;
        top: calc(100% + 3px);
        right: 7px;
        width: 10px;
        height: 10px;
        background: rgba(20, 35, 59, 0.98);
        transform: rotate(45deg);
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.18s ease, visibility 0.18s ease;
    }
    .metric-help:hover::after,
    .metric-help:hover::before,
    .metric-help:focus-visible::after,
    .metric-help:focus-visible::before {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }
    .control-help-row {
        display: flex;
        align-items: center;
        gap: 0;
        width: fit-content;
        padding-top: 0.15rem;
    }
    .sidebar-inline-help {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-top: 0.15rem;
    }
    [data-testid="stSidebar"] .sidebar-inline-help .metric-help {
        position: static;
        top: auto;
        right: auto;
    }
    .metric-row-gap {
        height: 1.8rem;
    }
    .metrics-divider {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, rgba(20, 35, 59, 0.03), rgba(20, 35, 59, 0.24), rgba(20, 35, 59, 0.03));
        margin: 0.35rem 0 0.3rem;
    }
    .chart-controls-gap-top {
        height: 0;
    }
    .chart-controls-gap-bottom {
        height: 0;
    }
    .chart-control-row {
        min-height: 1.4rem;
        display: flex;
        align-items: flex-start;
    }
    .chart-control-row--empty {
        width: 100%;
    }
    .chart-title-row {
        min-height: 2.8rem;
        display: flex;
        align-items: flex-end;
    }
    .chart-section-title {
        background: transparent;
        color: #111827;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        display: inline-block;
        padding: 0;
        border: 0;
        box-shadow: none;
        line-height: 1.1;
    }
    .minor-band-title {
        background: rgba(240, 244, 252, 0.95);
        color: #14233b;
        font-size: 19px;
        font-weight: 800;
        padding: 0.8rem 1rem;
        border-radius: 16px;
        border-left: 5px solid var(--accent);
        box-shadow: 0 12px 28px rgba(20, 35, 59, 0.06);
        line-height: 1.15;
    }
    .breakdown-table-wrap {
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid rgba(20, 35, 59, 0.08);
        border-radius: 18px;
        box-shadow: 0 14px 34px rgba(20, 35, 59, 0.06);
        overflow: hidden;
    }
    .breakdown-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.98rem;
        color: #14233b;
    }
    .breakdown-table thead th {
        background: #eef2ff;
        color: #0A1261;
        text-align: left;
        font-weight: 800;
        padding: 0.95rem 1rem;
        border-bottom: 1px solid rgba(20, 35, 59, 0.10);
    }
    .breakdown-table tbody td {
        padding: 0.9rem 1rem;
        border-bottom: 1px solid rgba(20, 35, 59, 0.08);
        font-weight: 600;
    }
    .breakdown-table tbody tr:last-child td {
        border-bottom: 0;
    }
    .breakdown-table tbody tr:nth-child(even) {
        background: rgba(238, 242, 255, 0.45);
    }
    .breakdown-table td:last-child,
    .breakdown-table th:last-child,
    .breakdown-table td:nth-child(2),
    .breakdown-table th:nth-child(2) {
        text-align: right;
        white-space: nowrap;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(10, 18, 97, 0.14) !important;
        border-radius: 18px !important;
        background: rgba(255, 255, 255, 0.98) !important;
        box-shadow: 0 14px 34px rgba(20, 35, 59, 0.08) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        background: #0A1261 !important;
        color: #ffffff !important;
        border-radius: 18px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #101a7a !important;
    }
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    [data-testid="stExpanderDetails"] {
        background: rgba(255, 255, 255, 0.98) !important;
        color: #14233b !important;
        border-top: 1px solid rgba(10, 18, 97, 0.08) !important;
    }
    [data-testid="stExpanderDetails"] p,
    [data-testid="stExpanderDetails"] li,
    [data-testid="stExpanderDetails"] strong,
    [data-testid="stExpanderDetails"] span,
    [data-testid="stExpanderDetails"] div {
        color: #14233b !important;
    }
    [data-testid="stExpanderDetails"] code {
        background: rgba(10, 18, 97, 0.06) !important;
        color: #0A1261 !important;
        border: 1px solid rgba(10, 18, 97, 0.10) !important;
    }
    .section-title {
        color: #111827;
        font-size: 22px;
        font-weight: 800;
        margin: 1.5rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.01em;
    }
    .metric-explanation {
        color: #e2e8f0;
        font-size: 13.5px;
        line-height: 1.5;
        text-align: center;
        padding: 0 10px;
        margin-top: 10px;
        font-weight: 500;
    }
    /* Estilos para EE.RR (Estado de Resultados) */
    .eerr-report-shell {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(10, 18, 97, 0.05);
        border: 1px solid rgba(10, 18, 97, 0.04);
        margin-top: 20px;
    }
    .eerr-title {
        font-size: 26px;
        font-weight: 900;
        color: #0A1261;
        margin-bottom: 8px;
        letter-spacing: -0.03em;
    }
    .eerr-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 30px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .eerr-table-scroll {
        overflow-x: auto;
        border-radius: 14px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .eerr-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .eerr-table thead th {
        background: #f8fafc;
        padding: 14px 10px;
        text-align: right;
        color: #475569;
        font-weight: 800;
        border-bottom: 2px solid #e2e8f0;
    }
    .eerr-table thead th:first-child { text-align: left; padding-left: 20px; }
    .eerr-table tbody td {
        padding: 12px 10px;
        text-align: right;
        border-bottom: 1px solid #f1f5f9;
        font-weight: 600;
        color: #1e293b;
    }
    .eerr-table tbody td:first-child {
        text-align: left;
        padding-left: 20px;
        color: #0c1e4c;
        font-weight: 700;
    }
    .eerr-subtotal { background: #f1f5f9; }
    .eerr-subtotal td { font-weight: 800 !important; color: #0A1261 !important; border-top: 1px solid #e2e8f0; }
    .eerr-negative { color: #ef4444 !important; }
    .eerr-spacer td { height: 15px; border: none !important; }

    @media (max-width: 1200px) {
        .metric-card {
            height: 168px;
            min-height: 168px;
            padding: 20px;
        }
        .metric-title {
            font-size: 12px;
            min-height: 2.2rem;
        }
        .metric-meta,
        .metric-delta {
            font-size: 12px;
        }
    }    /* --- FLIP CARD INTERACTIVE KPI --- */
    .flip-card-wrapper {
        display: block;
        width: 100%;
        height: 184px; /* Debe coincidir con metric-card */
        perspective: 1200px;
        cursor: pointer;
        position: relative;
        z-index: 10;
        margin: 0;
        padding: 0;
    }
    .flip-card-wrapper input[type="checkbox"] {
        display: none;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
        transform-style: preserve-3d;
    }
    .flip-card-wrapper input[type="checkbox"]:checked ~ .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 16px;
    }
    .flip-card-front {
        transform: rotateY(0deg);
        z-index: 2;
    }
    .flip-card-back {
        transform: rotateY(180deg);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        z-index: 1;
        background: #0A1261 !important; 
        color: white !important;
        padding: 24px 22px;
        box-sizing: border-box;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
    }
    .flip-card-back-title {
        color: #60a5fa !important;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    .flip-card-back-desc {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 14px;
        line-height: 1.5;
        font-weight: 500;
    }    /* --- INFO CAPSULE (POP-UP) --- */
    @keyframes pulse-blue {
        0% { box-shadow: 0 0 0 0 rgba(96, 165, 250, 0.6); }
        70% { box-shadow: 0 0 0 10px rgba(96, 165, 250, 0); }
        100% { box-shadow: 0 0 0 0 rgba(96, 165, 250, 0); }
    }
    .capsule-wrapper {
        position: relative;
        display: inline-block;
    }
    .capsule-checkbox {
        display: none;
    }
    .capsule-btn {
        background: #0A1261 !important;
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white !important;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 900;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        user-select: none;
        box-shadow: 0 4px 12px rgba(10, 18, 97, 0.3);
        animation: pulse-blue 2s infinite;
        position: relative;
        z-index: 10;
    }
    .capsule-btn:hover {
        background: #3b82f6 !important; /* Azul más brillante al hover */
        transform: scale(1.25) rotate(10deg);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        animation: none;
    }
    .capsule-btn:hover::before {
        content: attr(data-tooltip-text);
        position: absolute;
        bottom: 38px;
        left: 50%;
        transform: translateX(-50%) translateY(10px);
        background: #1e293b;
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.25s ease;
        pointer-events: none;
        box-shadow: 0 10px 25px rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .capsule-btn:hover::before {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translateX(-50%) translateY(0) !important;
    }
    .capsule-content {
        position: absolute;
        top: 35px;
        right: 0;
        width: min(320px, calc(100vw - 32px));
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(10, 18, 97, 0.15);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 50px rgba(10, 18, 97, 0.2);
        z-index: 9999;
        opacity: 0;
        visibility: hidden;
        transform: translateY(-10px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .capsule-checkbox:checked ~ .capsule-content {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }
    .capsule-title {
        color: #0A1261;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .capsule-text {
        color: #475569;
        font-size: 13px;
        line-height: 1.5;
        font-weight: 500;
    }
    .capsule-close {
        position: absolute;
        top: 12px;
        right: 12px;
        font-size: 18px;
        color: #94a3b8;
        cursor: pointer;
    }
    @media (max-width: 992px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .header-band {
            padding: 20px 22px;
            min-height: auto;
            border-radius: 18px;
        }
        .chart-title-row,
        .chart-control-row {
            min-height: auto;
        }
        .metric-row-gap {
            height: 1rem;
        }
        .capsule-content {
            right: auto;
            left: 0;
        }
        [data-testid="stSidebar"] {
            min-width: min(92vw, 360px) !important;
            max-width: min(92vw, 360px) !important;
        }
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
            min-height: 3rem;
            white-space: normal;
        }
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.75rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        [data-testid="stMainBlockContainer"] {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.75rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        .header-band {
            padding: 18px 18px;
            font-size: clamp(1.35rem, 6vw, 1.8rem);
            border-left-width: 5px;
            margin-bottom: 18px;
        }
        .section-title,
        .chart-section-title,
        .minor-band-title {
            font-size: clamp(1.1rem, 5vw, 1.35rem);
            line-height: 1.2;
        }
        .metric-card,
        .flip-card-wrapper,
        .flip-card-front,
        .flip-card-back {
            height: auto;
            min-height: 152px;
        }
        .metric-card,
        .flip-card-back {
            padding: 18px 16px;
        }
        .metric-title {
            min-height: auto;
            font-size: 11px;
            letter-spacing: 0.08em;
        }
        .metric-value {
            font-size: clamp(1.7rem, 8vw, 2.3rem);
            min-height: auto;
            white-space: normal;
            overflow-wrap: anywhere;
            text-align: center;
        }
        .metric-meta,
        .metric-delta,
        .metric-explanation,
        .flip-card-back-desc,
        .capsule-text {
            font-size: 12px;
        }
        [data-testid="stPlotlyChart"] {
            border-radius: 18px;
            padding: 10px 10px 2px;
        }
        [data-testid="stPlotlyChart"] .modebar {
            display: none !important;
        }
        .breakdown-table,
        .eerr-table {
            font-size: 0.82rem;
        }
        .breakdown-table thead th,
        .breakdown-table tbody td,
        .eerr-table thead th,
        .eerr-table tbody td {
            padding: 0.7rem 0.65rem;
        }
        .eerr-report-shell {
            padding: 1rem;
            border-radius: 18px;
        }
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span {
            font-size: 0.95rem !important;
        }
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"],
        [data-testid="stSidebar"] .stDateInput [data-baseweb="base-input"] {
            min-height: 2.85rem;
        }
    }
    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        .header-band {
            padding: 16px 14px;
            border-radius: 16px;
        }
        .chart-section-title,
        .section-title {
            font-size: 1.05rem;
        }
        .metric-card,
        .flip-card-back {
            padding: 16px 14px;
            border-radius: 14px;
        }
        .metric-help {
            top: 10px;
            right: 10px;
        }
        .metric-help::after {
            width: min(220px, calc(100vw - 48px));
            right: -4px;
        }
        .capsule-content {
            left: 50%;
            right: auto;
            transform: translateX(-50%) translateY(-10px);
        }
        .capsule-checkbox:checked ~ .capsule-content {
            transform: translateX(-50%) translateY(0);
        }
        .capsule-btn:hover::before {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def modulo_ventas_stock():
    # 1. Carga de Datos Única
    with st.spinner("Cargando Master Data..."):
        raw_df = load_data()
        df = process_dataframe(raw_df)

    if df.empty:
        st.error("Error: No se pudieron recuperar datos de la base de datos.")
        return

    # 2. Navegación Principal
    views = ["Inventario y Ventas", "Índice de Salud Master"]
    if "vision" not in st.session_state or st.session_state.vision not in views:
        st.session_state.vision = views[0]
    vision = st.session_state.vision

    st.sidebar.title("Interwins Status inventario")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Datos en Caché")
    if st.sidebar.button("Actualizar desde BD"):
        with st.spinner("Consolidando datos a Parquet..."):
            import Modulo_ventas_salud.consolidar_parquets as consolidar_parquets
            consolidar_parquets.actualizar_todo()
            st.success("¡Parquet actualizado con éxito!")
            st.rerun()

    st.sidebar.markdown("---")
    # 3. Filtros Globales (Afectan a cualquier Slide)
    st.sidebar.subheader("🎯 Filtros Globales")
    
    # Cargar maestro de productos para filtros enriquecidos
    from Modulo_ventas_salud.data import load_maestro_productos
    df_maestro = load_maestro_productos()
    
    if not df_maestro.empty:
        # Extraer código base de codigo_producto (antes del ' - ')
        df['codigo_base'] = df['codigo_producto'].str.split(' - ').str[0].str.strip().str.upper()
        
        # Enriquecer df con datos del maestro
        df = df.merge(df_maestro, left_on='codigo_base', right_on='codigo', how='left')
        df['familia'] = df['familia'].fillna('Sin información')
        df['proveedor'] = df['proveedor'].fillna('Sin información')
        df['tiering'] = df['tiering'].fillna('Sin información')
        df['tecnologia'] = df['tecnologia'].fillna('Sin información')
        
        # Filtros del maestro
        all_familias = sorted(df['familia'].unique())
        sel_familias = st.sidebar.multiselect("Familia", all_familias)
        
        all_proveedores = sorted(df['proveedor'].unique())
        sel_proveedores = st.sidebar.multiselect("Proveedor", all_proveedores)
        
        all_tiering = sorted(df['tiering'].unique())
        sel_tiering = st.sidebar.multiselect("Tiering", all_tiering)
        
        all_tecnologia = sorted(df['tecnologia'].unique())
        sel_tecnologia = st.sidebar.multiselect("Tecnología", all_tecnologia)
    
    all_products = sorted(df['codigo_producto'].unique())
    sel_products = st.sidebar.multiselect("Buscador de SKUs", all_products)
    
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    with st.sidebar.form("fechas_form"):
        st.markdown('<p style="font-size:14px; font-weight:bold; margin-bottom: 5px;">Rango Temporal</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Desde", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("Hasta", max_date, min_value=min_date, max_value=max_date)
        
        submitted_fechas = st.form_submit_button("✅ Aplicar Fechas", use_container_width=True)
        
    sel_dates = [start_date, end_date]
    
    # Aplicar filtros
    if len(sel_dates) == 2 and start_date <= end_date:
        f_df = filter_data_v2(df, sorted(df['canal'].unique()), sel_dates, sel_products)
    else:
        f_df = df.copy()
    
    # Aplicar filtros del maestro
    if not df_maestro.empty:
        if sel_familias:
            f_df = f_df[f_df['familia'].isin(sel_familias)]
        if sel_proveedores:
            f_df = f_df[f_df['proveedor'].isin(sel_proveedores)]
        if sel_tiering:
            f_df = f_df[f_df['tiering'].isin(sel_tiering)]
        if sel_tecnologia:
            f_df = f_df[f_df['tecnologia'].isin(sel_tecnologia)]

    st.markdown('<div class="dashboard-nav-gap"></div>', unsafe_allow_html=True)
    nav_col_1, nav_col_2, nav_spacer = st.columns([1.5, 1.8, 4])
    with nav_col_1:
        if st.button(
            "Inventario y Ventas",
            key="nav_panel_venta_stock",
            type="primary" if vision == "Inventario y Ventas" else "secondary",
            use_container_width=True,
        ):
            st.session_state.vision = "Inventario y Ventas"
            st.rerun()
    with nav_col_2:
        if st.button(
            "Índice de Salud Master",
            key="nav_panel_indice_salud",
            type="primary" if vision == "Índice de Salud Master" else "secondary",
            use_container_width=True,
        ):
            st.session_state.vision = "Índice de Salud Master"
            st.rerun()

    # 4. Router de Slides
    if vision == "Inventario y Ventas":
        # --- VISTA UNIFICADA ---
        st.markdown('<div class="header-band">Panel de Venta y Stock</div>', unsafe_allow_html=True)
        
        # Sidebar de stock (política de inventario)
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Configuración Logística")
        policy_label_col, policy_help_col = st.sidebar.columns([0.88, 0.12])
        with policy_label_col:
            st.markdown("**Política de Inventario (Meses)**")
        with policy_help_col:
            st.markdown(
                '<div class="sidebar-inline-help"><span class="metric-help" tabindex="0" data-tooltip="Este parámetro define el umbral de meses de cobertura considerado normal. Si lo subes, la app tolera más stock antes de clasificarlo como exceso; si lo bajas, detectará sobrestock con mayor sensibilidad.">i</span></div>',
                unsafe_allow_html=True,
            )
        policy_months = st.sidebar.slider("Política de Inventario (Meses)", 1, 12, 3, label_visibility="collapsed")
        
        # Cargar datos de stock
        with st.spinner("Sincronizando Stock y Ventas..."):
            df_inv = view_stock.load_and_calculate(policy_months)
        
        if not df_inv.empty:
            # --- Cálculos para KPIs curadas ---
            kpis = get_kpis(f_df)
            venta_total = kpis.get('Total Venta', 0)
            
            stock_total = df_inv['stock_actual'].clip(lower=0).sum()
            stock_val = (df_inv['stock_actual'].clip(lower=0) * df_inv['costo_unitario']).sum()
            venta_prom = df_inv['demanda_promedio'].sum()
            meses_inv = (stock_total / venta_prom) if venta_prom > 0 else 0
            
            mask_dem = df_inv['demanda_promedio'] > 0
            ns = df_inv[mask_dem]['nivel_servicio'].mean() * 100 if any(mask_dem) else 0
            
            quiebres = (df_inv['estado_inventario'].isin(['Sin Stock / Quiebre', 'Quiebre (Bajo Seguridad)'])).sum()
            inv_exceso = df_inv['valor_sobre_stock'].sum()
            sin_demanda = ((df_inv['stock_actual'] > 0) & (df_inv['demanda_promedio'] == 0)).sum()
            
            # --- Deltas MoM desde evolutivo ---
            def pct_delta(curr, prev):
                """Calcula delta % entre período actual y anterior. None si no hay dato."""
                if prev and prev != 0:
                    return ((curr - prev) / abs(prev)) * 100
                return None
            
            from Modulo_ventas_salud.data import load_historical_metrics
            df_hist = load_historical_metrics()
            d_stock_val = d_stock_tot = d_meses = d_venta = None
            
            if not df_hist.empty:
                df_hist['fecha'] = pd.to_datetime(df_hist['fecha'])
                df_evo_mes = df_hist.groupby('fecha').agg({'stock':'sum','venta':'sum'}).reset_index().sort_values('fecha')
                
                if len(df_evo_mes) >= 2:
                    curr_row = df_evo_mes.iloc[-1]
                    prev_row = df_evo_mes.iloc[-2]
                    
                    curr_stock  = curr_row['stock']
                    prev_stock  = prev_row['stock']
                    curr_venta  = curr_row['venta']
                    prev_venta  = prev_row['venta']
                    
                    # Stock valorizado (aproximar con costo_unitario promedio)
                    avg_cost = df_inv['costo_unitario'].mean() if not df_inv.empty else 0
                    d_stock_tot = pct_delta(curr_stock, prev_stock)
                    d_stock_val = pct_delta(curr_stock * avg_cost, prev_stock * avg_cost)
                    
                    curr_venta_prom = curr_stock / curr_venta if curr_venta > 0 else 0
                    prev_venta_prom = prev_stock / prev_venta if prev_venta > 0 else 0
                    d_meses = pct_delta(curr_venta_prom, prev_venta_prom)
                    d_venta = pct_delta(curr_venta, prev_venta)
            
            # --- FILA 1: Visión Estratégica ---
            st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
    <div class="chart-section-title" style="margin-bottom: 0;">Métricas de Salud y Rendimiento</div>
    <div class="capsule-wrapper">
        <div class="capsule-btn" style="width: 24px; height: 24px; font-size: 13px;" data-tooltip-text="💡 Clic en tarjetas para definiciones">i</div>
    </div>
</div>""", unsafe_allow_html=True)
            metric_help = {
                "Venta Valorizada": "Monto total vendido en el periodo filtrado. Un valor mayor indica más ingresos generados por el mix seleccionado.",
                "Stock Valorizado": "Capital invertido en inventario disponible. Un valor alto puede ser positivo o indicar sobreinversión según la demanda.",
                "Meses de Inventario": "Cuántos meses alcanzaría el stock actual al ritmo promedio de venta. Valores altos sugieren exceso; valores bajos, riesgo de quiebre.",
                "Nivel Servicio": "Porcentaje de demanda que puede cubrirse con el stock disponible. Mientras más alto, mejor cumplimiento hacia clientes.",
                "Stock Total": "Cantidad física total de unidades en bodega para el mix filtrado.",
                "Quiebres de Stock": "Número de SKUs sin stock o bajo el nivel de seguridad. Más alto implica mayor riesgo de no cumplir la demanda.",
                "Inversión en Exceso": "Capital inmovilizado en stock por sobre la política definida. Ayuda a detectar sobrestock.",
                "SKU Sin Demanda": "Cantidad de productos con stock, pero sin ventas en la ventana de análisis. Puede indicar obsolescencia o baja rotación.",
            }
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                view_stock.render_metric_card("Venta Valorizada", f"${venta_total/1e6:,.1f}M", "Total acumulado CLP", delta=d_venta, tooltip=metric_help["Venta Valorizada"], flip_desc=metric_help["Venta Valorizada"])
            with k2:
                view_stock.render_metric_card("Stock Valorizado", f"${stock_val/1e6:,.1f}M", "Capital invertido", delta=d_stock_val, tooltip=metric_help["Stock Valorizado"], flip_desc=metric_help["Stock Valorizado"])
            with k3:
                view_stock.render_metric_card("Meses de Inventario", f"{meses_inv:.1f}", "Stock / Venta Promedio", delta=d_meses, tooltip=metric_help["Meses de Inventario"], flip_desc=metric_help["Meses de Inventario"])
            with k4:
                view_stock.render_metric_card("Nivel Servicio", f"{ns:.1f}%", "Cumplimiento de demanda", tooltip=metric_help["Nivel Servicio"], flip_desc=metric_help["Nivel Servicio"])
            
            # --- FILA 2: Alertas Operacionales ---
            st.markdown('<div class="metric-row-gap"></div>', unsafe_allow_html=True)
            a1, a2, a3, a4 = st.columns(4)
            with a1:
                view_stock.render_metric_card("Stock Total", f"{stock_total:,.0f}", "Unidades en bodega", delta=d_stock_tot, tooltip=metric_help["Stock Total"], flip_desc=metric_help["Stock Total"])
            with a2:
                view_stock.render_metric_card("Quiebres de Stock", f"{quiebres}", "SKUs sin existencia", tooltip=metric_help["Quiebres de Stock"], flip_desc=metric_help["Quiebres de Stock"])
            with a3:
                view_stock.render_metric_card("Inversión en Exceso", f"${inv_exceso/1e6:,.1f}M", "Capital inmovilizado", tooltip=metric_help["Inversión en Exceso"], flip_desc=metric_help["Inversión en Exceso"])
            with a4:
                view_stock.render_metric_card("SKU Sin Demanda", f"{sin_demanda}", "Stock con 0 vtas (6m)", tooltip=metric_help["SKU Sin Demanda"], flip_desc=metric_help["SKU Sin Demanda"])

            st.markdown('<div class="metrics-divider"></div>', unsafe_allow_html=True)
            
            # --- GRÁFICOS lado a lado (Tendencia | Torta) ---
            st.markdown('<div class="chart-controls-gap-top"></div>', unsafe_allow_html=True)
            control_left, control_right = st.columns([1.2, 1])
            with control_left:
                toggle_col, help_col, _ = st.columns([0.44, 0.03, 0.53])
                with toggle_col:
                    modo_venta = st.radio("Visualizar ventas en:", ["Valorizado ($)", "Unidades"], horizontal=True, index=0)
                with help_col:
                    st.markdown(f"""
<div class="capsule-wrapper">
    <input type="checkbox" id="capsule_vnt" class="capsule-checkbox">
    <label for="capsule_vnt" class="capsule-btn" data-tooltip-text="🔍 Ver guía">i</label>
    <div class="capsule-content">
        <label for="capsule_vnt" class="capsule-close">×</label>
        <div class="capsule-title">💡 Guía de Visualización</div>
        <div class="capsule-text">
            <b>Valorizado ($):</b> Muestra la tendencia en montos de dinero para análisis de facturación.<br><br>
            <b>Unidades:</b> Analiza el volumen físico (cajas/unidades) para temas de logística y abastecimiento.
        </div>
    </div>
</div>""", unsafe_allow_html=True)
            with control_right:
                st.markdown('<div class="chart-control-row chart-control-row--empty"></div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-controls-gap-bottom"></div>', unsafe_allow_html=True)

            title_left, title_right = st.columns([1.2, 1])
            with title_left:
                capsule_vnt_html = f"""
<div style="display: flex; align-items: center; gap: 10px;">
    <div class="chart-section-title" style="margin-bottom: 0;">Evolución Histórica de Venta ({"$" if modo_venta == "Valorizado ($)" else "Unid."})</div>
    <div class="capsule-wrapper">
        <input type="checkbox" id="capsule_tendencia" class="capsule-checkbox">
        <label for="capsule_tendencia" class="capsule-btn" data-tooltip-text="📈 Ver tendencia">i</label>
        <div class="capsule-content">
            <label for="capsule_tendencia" class="capsule-close">×</label>
            <div class="capsule-title">📈 Tendencia de Ventas</div>
            <div class="capsule-text">
                Visualiza el comportamiento histórico de la demanda filtrada.<br><br>
                • <b>Línea Azul:</b> Representa el valor real (Ventas o Unidades).<br>
                • <b>Línea Naranja:</b> Promedio móvil que ayuda a suavizar la volatilidad y detectar la tendencia real del negocio.
            </div>
        </div>
    </div>
</div>"""
                st.markdown(f'<div class="chart-title-row">{capsule_vnt_html}</div>', unsafe_allow_html=True)
            with title_right:
                capsule_salud_html = """
<div style="display: flex; align-items: center; gap: 10px;">
    <div class="chart-section-title" style="margin-bottom: 0;">Análisis de Salud de Bodega</div>
    <div class="capsule-wrapper">
        <input type="checkbox" id="capsule_salud_main" class="capsule-checkbox">
        <label for="capsule_salud_main" class="capsule-btn" data-tooltip-text="🔍 Ver metodología">i</label>
        <div class="capsule-content" style="left: -150px;">
            <label for="capsule_salud_main" class="capsule-close">×</label>
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
</div>"""
                st.markdown(f'<div class="chart-title-row">{capsule_salud_html}</div>', unsafe_allow_html=True)

            col_trend, col_pie = st.columns([1.2, 1])
            with col_trend:
                if modo_venta == "Valorizado ($)":
                    st.plotly_chart(
                        view_salud.get_trend_figure(f_df, metric='venta', label='Venta ($)'),
                        use_container_width=True,
                        theme=None,
                    )
                else:
                    st.plotly_chart(
                        view_salud.get_trend_figure(f_df, metric='cantidad', label='Unidades'),
                        use_container_width=True,
                        theme=None,
                    )
            with col_pie:
                st.plotly_chart(view_stock.get_waterfall_figure(df_inv), use_container_width=True, theme=None)
            
            # --- EVOLUTIVO DE STOCK (ancho completo) ---
            capsule_evo_html = """
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
    <div class="chart-section-title" style="margin-bottom: 0;">Evolución Histórica del Stock y Cobertura</div>
    <div class="capsule-wrapper">
        <input type="checkbox" id="capsule_evo_main" class="capsule-checkbox">
        <label for="capsule_evo_main" class="capsule-btn" data-tooltip-text="📈 Ver análisis">i</label>
        <div class="capsule-content" style="left: -100px;">
            <label for="capsule_evo_main" class="capsule-close">×</label>
            <div class="capsule-title">📈 Stock vs Cobertura</div>
            <div class="capsule-text">
                Analiza la eficiencia del almacenamiento en el tiempo:<br><br>
                • <b>Barras Azules:</b> Cantidad física en bodega.<br>
                • <b>Línea Roja:</b> Meses de Inventario (Cobertura).<br><br>
                <b>Objetivo:</b> Mantener la línea roja estable dentro de la política para evitar excesos o quiebres.
            </div>
        </div>
    </div>
</div>"""
            st.markdown(capsule_evo_html, unsafe_allow_html=True)
            fig_evo = view_stock.get_stock_evo_figure()
            if fig_evo:
                st.plotly_chart(fig_evo, use_container_width=True, theme=None)
            else:
                st.info('No hay datos históricos de stock disponibles.')
        else:
            st.warning("No se pudo cargar la data de inventario.")
            
    elif vision == "Índice de Salud Master":
        view_indice.render(f_df)

def modulo_financiero():
    from Modulo_financiero.data import load_all_data
    from Modulo_financiero.view_resumen import render as render_resumen
    from Modulo_financiero.view_eerr import render as render_eerr
    
    with st.spinner("Cargando Estados Financieros..."):
        bundle = load_all_data()

    # Navegación del Módulo Financiero
    vistas = ["Resumen Ejecutivo", "Estado de Resultados"]
    if "vision_fin" not in st.session_state:
        st.session_state.vision_fin = vistas[0]
    
    # Navegación horizontal superior (Buenas Prácticas)
    st.markdown('<div class="dashboard-nav-gap"></div>', unsafe_allow_html=True)
    cols = st.columns([1, 1, 6])
    for i, v in enumerate(vistas):
        with cols[i]:
            if st.button(v, key=f"nav_fin_{i}", use_container_width=True, 
                         type="primary" if st.session_state.vision_fin == v else "secondary"):
                st.session_state.vision_fin = v
                st.rerun()

    st.sidebar.title("Interwins Módulo Financiero")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Datos en Caché")
    if st.sidebar.button("Actualizar Parquet Financiero"):
        with st.spinner("Sincronizando con base de datos..."):
            import Modulo_financiero.consolidar_parquets as consolidar
            consolidar.actualizar_todo()
            st.success("¡Datos financieros actualizados!")
            st.rerun()

    # Filtros del Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtros Financieros")
    
    active_filters = {}
    
    if not bundle["contable"].empty:
        df_c = bundle["contable"]
        
        # Centro de Costo
        all_cc1 = sorted(df_c["centro_costo"].dropna().astype(str).unique()) if "centro_costo" in df_c.columns else []
        sel_cc1 = st.sidebar.multiselect("Centro de Costo", all_cc1)
        if sel_cc1: active_filters["centros_costo"] = sel_cc1
        
        # Nivel 2 CC
        all_cc2 = sorted(df_c["Nivel_2_CC"].dropna().astype(str).unique()) if "Nivel_2_CC" in df_c.columns else []
        sel_cc2 = st.sidebar.multiselect("Nivel 2 CC", all_cc2)
        if sel_cc2: active_filters["niveles_2_cc"] = sel_cc2
            
        # Nivel 3 CC
        all_cc3 = sorted(df_c["Nivel_3_CC"].dropna().astype(str).unique()) if "Nivel_3_CC" in df_c.columns else []
        sel_cc3 = st.sidebar.multiselect("Nivel 3 CC", all_cc3)
        if sel_cc3: active_filters["niveles_3_cc"] = sel_cc3
            
        # Proyecto
        all_proy = sorted(df_c["Nombre_Proyecto"].dropna().astype(str).unique()) if "Nombre_Proyecto" in df_c.columns else []
        sel_proy = st.sidebar.multiselect("Proyecto", all_proy)
        if sel_proy: active_filters["proyectos"] = sel_proy

    if "meta" not in bundle:
        bundle["meta"] = {}
    bundle["meta"]["active_filters"] = active_filters

    # Render de Vistas
    if st.session_state.vision_fin == "Resumen Ejecutivo":
        render_resumen(bundle)
    elif st.session_state.vision_fin == "Estado de Resultados":
        render_eerr(bundle)
    else:
        st.info(f"La vista '{st.session_state.vision_fin}' está siendo adaptada al nuevo diseño.")

def modulo_comercial():
    from Modulo_comercial.data import load_data
    from Modulo_comercial.logic import filter_comercial_data
    from Modulo_comercial.view_resumen import render as render_resumen
    
    with st.spinner("Cargando métricas comerciales..."):
        df_com = load_data()

    st.sidebar.title("Interwins Módulo Comercial")
    st.sidebar.markdown("---")
    
    # Sincronización
    st.sidebar.subheader("🔄 Sincronización")
    if st.sidebar.button("Actualizar Data Comercial"):
        with st.spinner("Descargando data de ventas..."):
            import Modulo_comercial.consolidar_parquets as consolidar
            if consolidar.actualizar_todo():
                st.success("¡Data comercial actualizada!")
                st.rerun()
            else:
                st.error("Error al conectar con la base de datos.")

    # Filtros
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros Comerciales")
    active_filters = {}
    
    if not df_com.empty:
        # Vendedores
        vendedores = sorted(df_com["vendedor_nombre"].dropna().unique())
        sel_vend = st.sidebar.multiselect("Vendedores", vendedores)
        if sel_vend: active_filters["vendedor_nombre"] = sel_vend
        
        # Categorías
        categorias = sorted(df_com["categoria_producto"].dropna().unique())
        sel_cat = st.sidebar.multiselect("Categorías", categorias)
        if sel_cat: active_filters["categoria_producto"] = sel_cat
        
        # Marcas
        marcas = sorted(df_com["marca"].dropna().unique())
        sel_marca = st.sidebar.multiselect("Marcas", marcas)
        if sel_marca: active_filters["marca"] = sel_marca

    # Aplicar Filtros
    df_filtered = filter_comercial_data(df_com, active_filters)
    
    # Navegación del Módulo
    vistas = ["Resumen Ejecutivo", "Análisis por Canal", "Análisis de Margen"]
    if "vision_com" not in st.session_state:
        st.session_state.vision_com = vistas[0]
        
    st.markdown('<div class="dashboard-nav-gap"></div>', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 4])
    for i, v in enumerate(vistas):
        with cols[i]:
            if st.button(v, key=f"nav_com_{i}", use_container_width=True, 
                         type="primary" if st.session_state.vision_com == v else "secondary"):
                st.session_state.vision_com = v
                st.rerun()

    if st.session_state.vision_com == "Resumen Ejecutivo":
        render_resumen(df_filtered)
    else:
        st.info(f"La vista '{st.session_state.vision_com}' está en desarrollo.")

def main():
    # Logo robusto: Buscamos diferentes extensiones (jpg, png, etc.)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = None
    for ext in [".jpg", ".png", ".jpeg", ".webp"]:
        p = os.path.join(script_dir, "assets", f"logo_interwins{ext}")
        if os.path.exists(p):
            logo_path = p
            break
    
    if logo_path:
        st.sidebar.image(logo_path, width=220)
    else:
        st.sidebar.markdown('<div class="sidebar-image-placeholder">Logo Interwins</div>', unsafe_allow_html=True)
        
    st.sidebar.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True)

    # --- Selección de Módulos ---
    modulos = ["Ventas y Stock", "Financiero", "Comercial"]
    modulo_activo = st.sidebar.radio("Módulo", modulos, key="modulo_selector", label_visibility="collapsed")
    
    st.sidebar.markdown("---")

    if modulo_activo == "Ventas y Stock":
        modulo_ventas_stock()
    elif modulo_activo == "Financiero":
        modulo_financiero()
    elif modulo_activo == "Comercial":
        modulo_comercial()


if __name__ == "__main__":
    main()
