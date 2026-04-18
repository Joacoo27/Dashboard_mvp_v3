import pandas as pd
import numpy as np

def filter_comercial_data(df, filters):
    """Aplica filtros dinámicos a la data comercial."""
    if df.empty:
        return df
    
    df_f = df.copy()
    
    # Filtro por rango de fechas (si se pasa en filters)
    if 'start_date' in filters and 'end_date' in filters:
        df_f = df_f[(df_f['fecha_periodo'] >= pd.Timestamp(filters['start_date'])) & 
                    (df_f['fecha_periodo'] <= pd.Timestamp(filters['end_date']))]
    
    # Filtros categóricos
    filter_map = {
        'cliente_biwiser': 'cliente_biwiser',
        'empresa_rut': 'empresa_rut',
        'vendedor_nombre': 'vendedor_nombre',
        'cliente_nombre': 'cliente_nombre',
        'canal_venta': 'canal_venta',
        'tienda_nombre': 'tienda_nombre',
        'categoria_producto': 'categoria_producto',
        'marca': 'marca',
        'proyecto_nombre': 'proyecto_nombre',
        'tipo_movimiento': 'tipo_movimiento'
    }
    
    for key, col in filter_map.items():
        if key in filters and filters[key]:
            if isinstance(filters[key], list):
                df_f = df_f[df_f[col].isin(filters[key])]
            else:
                df_f = df_f[df_f[col] == filters[key]]
                
    return df_f

def get_comercial_kpis(df):
    """Calcula los KPIs principales para el resumen comercial."""
    if df.empty:
        return {
            "monto_real": 0, "monto_margen": 0, "margen_pct": 0,
            "cumplimiento_ppto": 0, "variacion_aa": 0, "cantidad": 0
        }
    
    total_real = df['monto_real'].sum()
    total_costo = df['monto_costo'].sum()
    total_margen = df['monto_margen'].sum()
    total_ppto = df['monto_ppto'].sum()
    total_aa = df['monto_real_aa'].sum()
    total_cantidad = df['cantidad'].sum()
    
    margen_pct = (total_margen / total_real * 100) if total_real != 0 else 0
    cumplimiento = (total_real / total_ppto * 100) if total_ppto != 0 else 0
    variacion_aa = ((total_real / total_aa - 1) * 100) if total_aa != 0 else 0
    
    return {
        "monto_real": total_real,
        "monto_costo": total_costo,
        "monto_margen": total_margen,
        "margen_pct": margen_pct,
        "cumplimiento_ppto": cumplimiento,
        "variacion_aa": variacion_aa,
        "cantidad": total_cantidad
    }

def build_commercial_trends(df):
    """Agrupa por periodo para visualización evolutiva."""
    if df.empty:
        return pd.DataFrame()
    
    df_evo = df.groupby('fecha_periodo').agg({
        'monto_real': 'sum',
        'monto_ppto': 'sum',
        'monto_margen': 'sum',
        'monto_real_aa': 'sum'
    }).reset_index()
    
    df_evo = df_evo.sort_values('fecha_periodo')
    df_evo['mes_label'] = df_evo['fecha_periodo'].dt.strftime('%b %Y')
    
    # Calcular Margen % histórico
    df_evo['margen_pct'] = (df_evo['monto_margen'] / df_evo['monto_real'] * 100).fillna(0)
    
    return df_evo
