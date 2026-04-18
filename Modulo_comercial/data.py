import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Configuración de rutas
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent
CACHE_DIR = PROJECT_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

COMERCIAL_PARQUET = CACHE_DIR / "comercial_cache.parquet"

def load_environment():
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

def load_data():
    """Carga la data comercial desde el caché local en formato Parquet."""
    if COMERCIAL_PARQUET.exists():
        df = pd.read_parquet(COMERCIAL_PARQUET)
        # Aseguramos tipos de datos para cálculos correctos
        if not df.empty and 'fecha_periodo' in df.columns:
            df['fecha_periodo'] = pd.to_datetime(df['fecha_periodo'])
        return df
    return pd.DataFrame()
