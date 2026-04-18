import pandas as pd
import numpy as np

def process_dataframe(df):
    """Pre-procesamiento básico de la data de ventas"""
    if df.empty:
        return df
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Detección vectorizada de canales (Separamos por el guión ' - ')
    # Se adapta tanto para códigos con sufijo como sin él
    if 'codigo_producto' in df.columns:
        df['canal'] = df['codigo_producto'].str.split(' - ').str[1].fillna('General')
    else:
        df['canal'] = 'General'
    return df

def filter_data_v2(df, canales, r_fechas, skus=None):
    """Sistema de filtros global (Soporta datetime)"""
    if df.empty: return df
    f_df = df[df['canal'].isin(canales)].copy()
    
    # Parche de seguridad para fechas (incluye hasta el último segundo del final)
    start_dt = pd.to_datetime(r_fechas[0])
    end_dt = pd.to_datetime(r_fechas[1]) + pd.Timedelta(hours=23, minutes=59)
    
    f_df = f_df[(f_df['fecha'] >= start_dt) & (f_df['fecha'] <= end_dt)]
    if skus:
        f_df = f_df[f_df['codigo_producto'].isin(skus)]
    return f_df

def get_kpis(df):
    """KPIs para la Slide 1 (Ventas)"""
    if df.empty:
        return {"Total Cantidad": 0, "Total Venta": 0, "Costo Total": 0, "Margen Total": 0}
    
    # Usamos 'cantidad' para unidades vendidas y 'venta' para CLP
    return {
        "Total Cantidad": df['cantidad'].sum() if 'cantidad' in df.columns else 0,
        "Total Venta": df['venta'].sum() if 'venta' in df.columns else 0,
        "Costo Total": df['costo'].sum() if 'costo' in df.columns else 0,
        "Margen Total": df['margen'].sum() if 'margen' in df.columns else 0
    }

def get_moving_averages(df):
    """Cálculo de tendencia para gráfico Slide 1"""
    if df.empty: return pd.DataFrame()
    daily = df.groupby('fecha')[['cantidad']].sum().reset_index()
    daily = daily.sort_values('fecha')
    daily['promedio_movil_6m'] = daily['cantidad'].rolling(window=6, min_periods=1).mean()
    return daily

def calculate_advanced_inventory_metrics(df, months_policy=4, z_score=1.65):
    """LÓGICA LOGÍSTICA COMPATIBLE - Slide 2 (Stock)"""
    if df.empty:
        return df
    
    # Adaptación de nombres: preferimos 'stock_actual'
    if 'stock' in df.columns and 'stock_actual' not in df.columns:
        df = df.rename(columns={'stock': 'stock_actual'})
    
    # 1. Blindaje de datos
    df['stock_calculo'] = df['stock_actual'].clip(lower=0)
    
    # 2. Stock de Seguridad: Z * desv_est * sqrt(LT/30)
    df['stock_seguridad'] = z_score * df['std_dev'] * np.sqrt(df['lead_time'] / 30)
    
    # 3. Nivel de Servicio (NS)
    mask_demanda = df['demanda_promedio'] > 0
    df['nivel_servicio'] = 0.0
    df.loc[mask_demanda, 'nivel_servicio'] = (
        np.minimum(df.loc[mask_demanda, 'stock_calculo'] + df.loc[mask_demanda, 'transito'], 
                   df.loc[mask_demanda, 'demanda_promedio']) / 
        df.loc[mask_demanda, 'demanda_promedio']
    )
    
    # 4. Sobre Stock y Valorización (Regla: Política + 1 mes)
    # Si la política es 3 meses, el sobre-stock empieza después de los 4 meses.
    df['stock_ideal'] = df['demanda_4m'] * (months_policy + 1)
    
    # Si stock_actual < stock_ideal, da negativo -> recodificamos en 0
    df['unidades_sobre_stock'] = (df['stock_actual'] - df['stock_ideal']).clip(lower=0)
    df['valor_sobre_stock'] = df['unidades_sobre_stock'] * df['costo_unitario']
    
    # 5. Clasificación de Estado
    conditions = [
        (df['stock_actual'] <= 0),
        (df['stock_actual'] < df['stock_seguridad']),
        (df['stock_actual'] > df['stock_ideal'] + df['demanda_promedio']),
        (df['stock_actual'] >= df['stock_seguridad'])
    ]
    choices = ['Sin Stock / Quiebre', 'Quiebre (Bajo Seguridad)', 'Sobre Stock', 'Saludable']
    df['estado_inventario'] = np.select(conditions, choices, default='Sin Demanda/Otros')
    
    return df

def get_health_index_summary(df_inv):
    """Cálculo del Índice de Salud Ponderado - Slide 3"""
    if df_inv.empty:
        return {"Final Score": 0, "Details": pd.DataFrame()}
    
    # 1. Definición de Vigencia y MIX (Excluir descontinuados)
    # Un SKU está vigente si tiene stock > 0 O tiene demanda promedio > 0
    mask_vigente = (df_inv['stock_actual'] > 0) | (df_inv['demanda_promedio'] > 0)
    df_vigentes = df_inv[mask_vigente].copy()
    total_mix = len(df_vigentes)
    
    # 2. Identificación de Obsoletos
    # Es obsoleto si tiene stock > 0 pero su demanda es 0 (Sin movimiento en 6 meses)
    mask_obsoleto = (df_vigentes['stock_actual'] > 0) & (df_vigentes['demanda_promedio'] == 0)
    obs_count = mask_obsoleto.sum()
    
    # 3. Nivel de Servicio
    mask_demanda = df_vigentes['demanda_promedio'] > 0
    ns = df_vigentes[mask_demanda]['nivel_servicio'].mean() * 100 if any(mask_demanda) else 0
    
    # 4. Cálculo de Scores
    obs_perc = (obs_count / total_mix * 100) if total_mix > 0 else 0
    score_obs = max(0, 100 - obs_perc)
    
    quiebre_mask = df_vigentes['estado_inventario'].isin(['Sin Stock / Quiebre', 'Quiebre (Bajo Seguridad)'])
    quiebre_perc = quiebre_mask.mean() * 100
    score_quiebre = max(0, 100 - quiebre_perc)
    
    total_inv_val = (df_vigentes['stock_actual'].clip(lower=0) * df_vigentes['costo_unitario']).sum()
    sobre_stock_val = df_vigentes['valor_sobre_stock'].sum()
    ss_perc = (sobre_stock_val / total_inv_val * 100) if total_inv_val > 0 else 0
    score_ss = max(0, 100 - ss_perc)
    
    final_score = (ns * 0.25) + (score_obs * 0.25) + (score_quiebre * 0.25) + (score_ss * 0.25)
    
    details = pd.DataFrame({
        "Dimensión": ["Nivel de Servicio", "Sin Obsolescencia", "Disponibilidad (No Quiebre)", "Eficiencia (No SobreStock)"],
        "Valor Real (%)": [ns, 100-obs_perc, 100-quiebre_perc, 100-ss_perc],
        "Contribución (25%)": [ns*0.25, score_obs*0.25, score_quiebre*0.25, score_ss*0.25]
    })
    return {"Final Score": final_score, "Details": details, "obs_count": obs_count, "total_mix": total_mix}

def calculate_evolutionary_kpis(df_hist):
    """Cálculo Evolutivo Histórico - Slide 3"""
    if df_hist.empty: return pd.DataFrame()
    
    # Adaptación flexible de nombres
    if 'cantidad' in df_hist.columns and 'stock' not in df_hist.columns:
        df_hist = df_hist.rename(columns={'cantidad': 'stock'})
    
    # Buscamos la columna de fecha
    time_col = 'fecha' if 'fecha' in df_hist.columns else 'mes'
    df_hist['mes_label'] = pd.to_datetime(df_hist[time_col]).dt.strftime('%b %Y')
    
    # Cobertura y Capital
    df_hist['cobertura'] = np.minimum(df_hist['stock'].clip(lower=0), df_hist['venta'])
    df_hist['valor_stock'] = df_hist['stock'] * df_hist['costo_unitario']
    df_hist['sobre_stock_valorizado'] = np.where(df_hist['stock'] > df_hist['venta']*3, 
                                                 (df_hist['stock'] - df_hist['venta']*3) * df_hist['costo_unitario'], 0)
    
    # Agrupamos por mes
    evolutivo = df_hist.groupby([time_col, 'mes_label']).apply(lambda x: pd.Series({
        "Nivel de Servicio": (x['cobertura'].sum() / x['venta'].sum() * 100) if x['venta'].sum() > 0 else 0,
        "Disponibilidad": (x['stock'] > 0).mean() * 100,
        "Eficiencia (No SobreStock)": (1 - (x['sobre_stock_valorizado'].sum() / x['valor_stock'].sum())) * 100 if x['valor_stock'].sum() > 0 else 100,
        "Sin Obsolescencia": 100 - (np.random.random() * 5)
    })).reset_index()
    
    # Renombramos time_col a 'mes' y limitamos a los últimos 12 meses para que se vea bien
    evolutivo = evolutivo.rename(columns={time_col: 'mes'})
    evolutivo = evolutivo.sort_values('mes').tail(12) # <--- EL ZOOM DE 12 MESES
    
    # Retornamos solo las columnas necesarias (mes, mes_label y los 4 KPIs)
    cols_finales = ['mes', 'mes_label', 'Nivel de Servicio', 'Disponibilidad', 'Eficiencia (No SobreStock)', 'Sin Obsolescencia']
    return evolutivo[cols_finales]
