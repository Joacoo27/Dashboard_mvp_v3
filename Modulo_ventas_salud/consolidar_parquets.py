import pandas as pd
import sys
from pathlib import Path
import os
from datetime import datetime

# Importar desde el mismo directorio
from .data import get_sqlalchemy_engine, VENTAS_PARQUET, STOCK_PARQUET, EVOLUTIVO_PARQUET, MAESTRO_PARQUET, BASE_DIR, PROJECT_DIR


def resolve_sales_sql_path():
    """Busca la query de ventas primero dentro del proyecto y luego en la ruta legacy."""
    candidates = [
        PROJECT_DIR / "sql_scripts" / "transaccional_mensual.sql",
        BASE_DIR / "sql_scripts" / "transaccional_mensual.sql",
    ]
    for path in candidates:
        if path.exists():
            return path
    searched = "\n".join(f" - {path}" for path in candidates)
    raise FileNotFoundError(
        "No se encontró el archivo transaccional_mensual.sql en ninguna de estas rutas:\n"
        f"{searched}"
    )

def actualizar_todo():
    print("🚀 Iniciando Consolidación Maestra (Review de Lógica y Nombres)...")
    engine = get_sqlalchemy_engine()
    if not engine:
        print("❌ Error: No se pudo conectar a la Base de Datos.")
        return

    try:
        # 1. Ventas (Slide 1: Panel de Venta)
        # Nombres estándar: fecha, codigo_producto, cantidad (unidades), venta (monto), costo, margen
        print("📥 Procesando Ventas...")
        sql_path = resolve_sales_sql_path()
        print(f"   ↳ SQL ventas: {sql_path}")
        with open(sql_path, 'r', encoding='utf-8') as f: query_vta = f.read()
        df_vta = pd.read_sql(query_vta.replace('%', '%%'), engine)
        # Aseguramos tipos
        df_vta['fecha'] = pd.to_datetime(df_vta['fecha'])
        df_vta.to_parquet(VENTAS_PARQUET)

        # 2. Nueva Query de Stock Consolidado (Enviada por el usuario)
        # Trae: fecha, codigo_producto, cantidad (stock), costo_unitario
        print("📥 Procesando Stock y Costos Reales...")
        QUERY_STOCK_NUEVA = """
        WITH stock_raw AS (
            SELECT s.codigo_bodega, split_part(s.codigo_producto, '-C', 1) AS codigo_producto, s.stock, s.costo_unitario, s.fecha_stock
            FROM stock AS s WHERE s.codigo_producto LIKE '%-C'
            UNION ALL 
            SELECT s.codigo_bodega, s.codigo_producto, s.stock, s.costo_unitario, s.fecha_stock
            FROM stock AS s WHERE s.codigo_producto NOT LIKE '%-C'
        ),
        tabla_stock_1 AS (
            SELECT i.codigo_producto, i.codigo_bodega, SUM(i.stock) AS stock, MIN(COALESCE(i.costo_unitario, 0)) AS costo_unitario
            FROM stock_raw AS i
            WHERE i.codigo_bodega IN ('01', '10', '16', '23', '24') AND i.stock >= 0
            GROUP BY 1, 2
        ),
        tabla_stock_2 AS ( 
            SELECT codigo_producto, 
                   CASE WHEN codigo_bodega = '01' THEN codigo_producto||' - DEALER'
                        WHEN codigo_bodega = '10' THEN codigo_producto||' - WALMART'
                        WHEN codigo_bodega = '16' THEN codigo_producto||' - CODELCO'
                        WHEN codigo_bodega = '23' THEN codigo_producto||' - ANGLO'
                        WHEN codigo_bodega = '24' THEN codigo_producto||' - AMSA'
                   END AS codigo_canal, stock, costo_unitario FROM tabla_stock_1 
        ),
        tabla_stock_3 AS (
            SELECT codigo_canal AS codigo_producto, SUM(stock) AS stock, MIN(costo_unitario) AS costo_unitario
            FROM tabla_stock_2 GROUP BY 1
        ),
        tabla_stock_historico_1 AS (
            SELECT date_trunc('month', i.fecha_stock)::date AS fecha,
                   split_part(i.codigo_producto, '-C', 1) AS codigo_producto, i.codigo_bodega,
                   SUM(i.stock) AS stock, MIN(COALESCE(i.costo_unitario, 0)) AS costo_unitario
            FROM (SELECT codigo_bodega, codigo_producto, SUM(stock) AS stock, MAX(costo_unitario) AS costo_unitario, fecha_stock::date
                  FROM stock_historico_diario_new GROUP BY 1,2,5) AS i
            WHERE i.codigo_bodega IN ('01', '10', '16', '23', '24') AND i.codigo_producto LIKE '%-C'
                  AND i.fecha_stock >= '2025-01-01'
                  AND i.fecha_stock = (date_trunc('month', i.fecha_stock) + interval '1 month - 1 day')::date
            GROUP BY 1, 2, 3
            UNION ALL
            SELECT date_trunc('month', i.fecha_stock)::date AS fecha,
                   i.codigo_producto, i.codigo_bodega,
                   SUM(i.stock) AS stock, MIN(COALESCE(i.costo_unitario, 0)) AS costo_unitario
            FROM (SELECT codigo_bodega, codigo_producto, SUM(stock) AS stock, MAX(costo_unitario) AS costo_unitario, fecha_stock::date
                  FROM stock_historico_diario_new GROUP BY 1,2,5) AS i
            WHERE i.codigo_bodega IN ('01', '10', '16', '23', '24') AND i.codigo_producto NOT LIKE '%-C'
                  AND i.fecha_stock >= '2025-01-01'
                  AND i.fecha_stock = (date_trunc('month', i.fecha_stock) + interval '1 month - 1 day')::date
            GROUP BY 1, 2, 3
        ),
        tabla_stock_historico_3 AS (
            SELECT fecha, 
                   CASE WHEN codigo_bodega = '01' THEN codigo_producto||' - DEALER'
                        WHEN codigo_bodega = '10' THEN codigo_producto||' - WALMART'
                        WHEN codigo_bodega = '16' THEN codigo_producto||' - CODELCO'
                        WHEN codigo_bodega = '23' THEN codigo_producto||' - ANGLO'
                        WHEN codigo_bodega = '24' THEN codigo_producto||' - AMSA'
                   END AS codigo_producto, SUM(stock) AS stock, MIN(costo_unitario) AS costo_unitario
            FROM tabla_stock_historico_1 GROUP BY 1, 2
        ),
        stock_consolidado AS (
            SELECT DATE_TRUNC('month', NOW())::DATE AS fecha, TRIM(UPPER(i.codigo_producto)) AS codigo_producto, 
                   i.stock AS cantidad, COALESCE(i.costo_unitario,0) AS costo_unitario FROM tabla_stock_3 AS i
            UNION ALL
            SELECT DATE_TRUNC('month', fecha)::DATE AS fecha, TRIM(UPPER(i.codigo_producto)) AS codigo_producto, 
                   i.stock AS cantidad, COALESCE(i.costo_unitario,0) AS costo_unitario FROM tabla_stock_historico_3 AS i
        )
        SELECT * FROM stock_consolidado WHERE costo_unitario > 0;
        """
        df_stock_sql = pd.read_sql(QUERY_STOCK_NUEVA.replace('%', '%%'), engine)
        df_stock_sql['fecha'] = pd.to_datetime(df_stock_sql['fecha'])
        df_stock_sql = df_stock_sql.rename(columns={'cantidad': 'stock'})

        # --- FILTRO DE CONSISTENCIA (Universe Filter) ---
        print("✂️ Filtrando Stock: solo productos con presencia en Ventas...")
        universo_productos = df_vta['codigo_producto'].unique()
        df_stock_sql = df_stock_sql[df_stock_sql['codigo_producto'].isin(universo_productos)].copy()
        # ------------------------------------------------

        # 3. Unir Stock con Ventas para el Evolutivo (Slide 3: Panel de Salud)
        # Necesita: fecha, codigo_producto, stock, venta (unidades), costo_unitario
        print("🔗 Cruzando Stock con Ventas para histórico...")
        # Ventas mensuales agrupadas
        df_vta_mensual = df_vta.groupby(['fecha', 'codigo_producto'])[['cantidad', 'venta']].sum().reset_index()
        df_vta_mensual = df_vta_mensual.rename(columns={'cantidad': 'venta_unidades', 'venta': 'venta_monto'})

        df_evo_final = df_stock_sql.merge(df_vta_mensual, on=['fecha', 'codigo_producto'], how='outer').fillna(0)
        # Normalizamos nombres para logic.py
        df_evo_final = df_evo_final.rename(columns={'venta_unidades': 'venta'})
        df_evo_final.to_parquet(EVOLUTIVO_PARQUET)

        # 4. Preparar Stock Actual (Slide 2: Panel de Stock)
        # Necesita: codigo_producto, stock_actual, demanda_promedio, std_dev, costo_unitario, etc.
        print("📊 Calculando estadísticas y métricas para Stock Actual...")
        # Filtramos solo el stock del mes de hoy
        today_start = pd.Timestamp(datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0))
        df_stock_now = df_stock_sql[df_stock_sql['fecha'] == today_start].copy()
        
        # Estadísticas de demanda (avg_6m, std_dev) calculadas desde df_vta
        today_dt = pd.Timestamp.now()
        stats_list = []
        for sku, group in df_vta.groupby('codigo_producto'):
            avg_6m = group[group['fecha'] >= (today_dt - pd.DateOffset(months=6))]['cantidad'].sum() / 6.0
            avg_4m = group[group['fecha'] >= (today_dt - pd.DateOffset(months=4))]['cantidad'].sum() / 4.0
            std_dev = group[group['fecha'] >= (today_dt - pd.DateOffset(months=12))]['cantidad'].std()
            stats_list.append({
                'codigo_producto': sku,
                'demanda_promedio': avg_6m,
                'demanda_4m': avg_4m,
                'std_dev': std_dev if not pd.isna(std_dev) else 0
            })
        df_stats = pd.DataFrame(stats_list)

        df_stock_final = df_stock_now.merge(df_stats, on='codigo_producto', how='left').fillna(0)
        # Renombrar para que logic.py y view_stock coincidan
        df_stock_final = df_stock_final.rename(columns={'stock': 'stock_actual'})
        df_stock_final['transito'] = 0
        df_stock_final['lead_time'] = 30
        
        df_stock_final.to_parquet(STOCK_PARQUET)

        # 5. Maestro de Productos (Filtros: familia, proveedor, tiering, tecnología)
        print("📥 Procesando Maestro de Productos...")
        QUERY_MAESTRO = """
        SELECT DISTINCT
            codigo,
            descripcion,
            familia,
            COALESCE(descrp_corta, 'Sin informacion') AS descripcion_corta,
            COALESCE(proveedor,'Sin informacion') AS proveedor,
            COALESCE(tiering, 'Sin informacion') AS tiering,
            COALESCE(tecnologia,'Sin informacion') AS tecnologia
        FROM public.auxiliar_maestro_producto
        """
        df_maestro = pd.read_sql(QUERY_MAESTRO.replace('%', '%%'), engine)
        df_maestro['codigo'] = df_maestro['codigo'].str.strip().str.upper()
        df_maestro.to_parquet(MAESTRO_PARQUET)
        print(f"   ✅ Maestro: {len(df_maestro)} productos cargados.")
        
        print("\n✨ REVISIÓN DE LÓGICA COMPLETADA. Datos sincronizados.")
    finally:
        engine.dispose()

if __name__ == "__main__":
    actualizar_todo()
