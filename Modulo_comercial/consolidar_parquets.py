import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from .data import COMERCIAL_PARQUET, get_db_config

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
    except Exception as e:
        print(f"Error creando engine: {e}")
        return None

def fetch_comercial_data():
    """Filtra y descarga la data de la tabla biwiser_fact_comercial."""
    engine = get_sqlalchemy_engine()
    if not engine:
        return None
    
    query = "SELECT * FROM biwiser_fact_comercial ORDER BY fecha_periodo DESC"
    
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error en query comercial: {e}")
        return None

def actualizar_todo():
    """Descarga data de BD y sobreescribe el caché local."""
    df = fetch_comercial_data()
    if df is not None and not df.empty:
        df.to_parquet(COMERCIAL_PARQUET, index=False)
        print(f"Cache comercial actualizado: {len(df)} filas.")
        return True
    return False

if __name__ == "__main__":
    actualizar_todo()
