import pandas as pd
import psycopg2
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Configuración de rutas
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent
CACHE_DIR = PROJECT_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

VENTAS_PARQUET = CACHE_DIR / "ventas_cache.parquet"
STOCK_PARQUET = CACHE_DIR / "stock_cache.parquet"
EVOLUTIVO_PARQUET = CACHE_DIR / "evolutivo_cache.parquet"
MAESTRO_PARQUET = CACHE_DIR / "maestro_cache.parquet"

def load_environment():
    # Permitimos .env tanto en la carpeta del proyecto como en su carpeta padre.
    load_dotenv(PROJECT_DIR / ".env")
    load_dotenv(BASE_DIR / ".env")

def get_db_config():
    load_environment()
    return {
        "host": os.getenv('HOST_DATABASE'),
        "database": os.getenv('NAME_DATABASE'),
        "user": os.getenv('USER_DATABASE'),
        "password": os.getenv('PASW_DATABASE'),
        "port": os.getenv('PORT_DATABASE'),
    }

def get_connection():
    config = get_db_config()
    try:
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"]
        )
        return conn
    except: return None

@st.cache_resource
def get_sqlalchemy_engine():
    config = get_db_config()
    try:
        db_url = URL.create(
            "postgresql+psycopg2",
            username=config["user"],
            password=config["password"],
            host=config["host"],
            port=int(config["port"]) if config["port"] else None,
            database=config["database"],
        )
        return create_engine(db_url, pool_pre_ping=True)
    except:
        return None

def load_data():
    """Solo lectura desde Parquet para Dashboard"""
    if VENTAS_PARQUET.exists():
        return pd.read_parquet(VENTAS_PARQUET)
    return pd.DataFrame()

def load_advanced_stock_data():
    """Solo lectura desde Parquet para Dashboard"""
    if STOCK_PARQUET.exists():
        return pd.read_parquet(STOCK_PARQUET)
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_historical_metrics():
    """Solo lectura desde Parquet para Dashboard"""
    if EVOLUTIVO_PARQUET.exists():
        return pd.read_parquet(EVOLUTIVO_PARQUET)
    return pd.DataFrame()

def load_maestro_productos():
    """Carga el maestro de productos (filtros: familia, proveedor, tiering, tecnología)"""
    if MAESTRO_PARQUET.exists():
        return pd.read_parquet(MAESTRO_PARQUET)
    return pd.DataFrame()

def get_global_obsolete_count():
    # Esta métrica es ligera, pero igual la ideal es sacarla de Parquet si se puede
    # Por ahora la dejamos como fallback rápido o podemos integrarla en el consolidado
    df = load_data()
    if df.empty: return 0
    try:
        # Aproximación desde el parquet de ventas
        df['fecha'] = pd.to_datetime(df['fecha'])
        last_sales = df.groupby('codigo_producto')['fecha'].max()
        max_date = last_sales.max()
        obsolete_limit = max_date - timedelta(days=360)
        return len(last_sales[last_sales <= obsolete_limit])
    except: return 0
