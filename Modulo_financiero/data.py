import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Configuración de rutas
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent
CACHE_DIR = PROJECT_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CONTABLE_PARQUET = CACHE_DIR / "contable_financiero_cache.parquet"
GLOSAS_PARQUET = CACHE_DIR / "glosas_contables_cache.parquet"

def load_environment():
    load_dotenv(PROJECT_DIR / ".env")
    load_dotenv(BASE_DIR / ".env")

def get_db_config():
    load_environment()
    return {
        "host": os.getenv('HOST_DATABASE'),
        "database": os.getenv('NAME_DATABASE'),
        "user": os.getenv('USER_DATABASE'),
        "pass": os.getenv('PASW_DATABASE'),
        "port": os.getenv('PORT_DATABASE', '5432')
    }

def get_sqlalchemy_engine():
    conf = get_db_config()
    if not all([conf['host'], conf['database'], conf['user'], conf['pass']]):
        return None
    
    connection_url = URL.create(
        "postgresql",
        username=conf['user'],
        password=conf['pass'],
        host=conf['host'],
        database=conf['database'],
        port=conf['port']
    )
    return create_engine(connection_url)

def _read_parquet(path, dataset_name: str):
    if path.exists():
        try:
            return pd.read_parquet(path), None
        except Exception as exc:
            warning = f"No se pudo leer {dataset_name} desde {path.name}. Detalle: {exc}"
            return pd.DataFrame(), warning
    return pd.DataFrame(), None

def _base_contable_row(
    fecha: pd.Timestamp,
    centro_costo: str,
    centro_costo_desc: str,
    nivel_3_cc: str,
    nivel_2_cc: str,
    nombre_proyecto: str,
    cuenta_contable: str,
) -> dict:
    return {
        "fecha": fecha,
        "anio": fecha.year,
        "mes": fecha.month,
        "centro_costo": centro_costo,
        "centro_costo_desc": centro_costo_desc,
        "Nivel_3_CC": nivel_3_cc,
        "Nivel_2_CC": nivel_2_cc,
        "Nombre_Proyecto": nombre_proyecto,
        "cuenta_contable": cuenta_contable,
        "pccodi_4": cuenta_contable,
        "debe": 0.0,
        "haber": 0.0,
        "saldo": 0.0,
        "PPTO": 0.0,
    }

def build_demo_contable() -> pd.DataFrame:
    current_month = pd.Timestamp.today().normalize().replace(day=1)
    months = pd.date_range(end=current_month, periods=24, freq="MS")
    rows = []
    unidades = [
        {"centro_costo": "CORP-001", "centro_costo_desc": "Corporativo", "Nivel_3_CC": "Corporativo", "Nivel_2_CC": "Administracion", "Nombre_Proyecto": "Gestion Central", "factor": 1.0},
        {"centro_costo": "COM-010", "centro_costo_desc": "Ventas Consultoria", "Nivel_3_CC": "Comercial", "Nivel_2_CC": "Servicios", "Nombre_Proyecto": "Consultoria Empresarial", "factor": 1.35},
        {"centro_costo": "OPS-020", "centro_costo_desc": "Operaciones Proyectos", "Nivel_3_CC": "Operaciones", "Nivel_2_CC": "Proyectos", "Nombre_Proyecto": "Implementaciones", "factor": 1.2},
    ]

    for idx, month in enumerate(months):
        for unidad in unidades:
            factor = unidad["factor"]
            base = 940_000 + idx * 26_000
            ingresos = base * factor
            costo_venta = ingresos * 0.54
            gastos_operacionales = ingresos * 0.17
            depreciacion = ingresos * 0.025
            gasto_financiero = ingresos * 0.012
            
            presupuesto_ingresos = ingresos * 0.97
            presupuesto_costo = presupuesto_ingresos * 0.53
            presupuesto_opex = presupuesto_ingresos * 0.165
            presupuesto_dep = presupuesto_ingresos * 0.024
            presupuesto_fin = presupuesto_ingresos * 0.011

            eerr_rows = [
                ("410100", "Ingresos", "INGRESOS", "INGRESOS OPERACIONALES", "ESTADO DE RESULTADOS", ingresos, presupuesto_ingresos),
                ("510100", "Costo de Venta", "COSTO DE VENTA", "COSTO DE VENTA", "ESTADO DE RESULTADOS", costo_venta, presupuesto_costo),
                ("610100", "Gastos Operacionales", "GASTOS OPERACIONALES", "GASTOS OPERACIONALES", "ESTADO DE RESULTADOS", gastos_operacionales, presupuesto_opex),
                ("620100", "Depreciacion", "GASTOS OPERACIONALES", "DEPRECIACION", "ESTADO DE RESULTADOS", depreciacion, presupuesto_dep),
                ("710100", "Resultado Financiero", "RESULTADO FINANCIERO", "NO OPERACIONAL", "ESTADO DE RESULTADOS", gasto_financiero, presupuesto_fin),
            ]

            for cuenta, descripcion, nivel_1, nivel_3, estado, real, presupuesto in eerr_rows:
                row = _base_contable_row(month, unidad["centro_costo"], unidad["centro_costo_desc"], unidad["Nivel_3_CC"], unidad["Nivel_2_CC"], unidad["Nombre_Proyecto"], cuenta)
                row.update({
                    "Cuenta_IFRS": cuenta, "Nivel_1_IFRS": nivel_1, "Nivel_2_IFRS": descripcion, "Nivel_3_IFRS": nivel_3, "Estado_Financiero": estado,
                    "pcdesc_4": descripcion, "pccodi_3": cuenta[:4], "pcdesc_3_Modificado": descripcion.upper(), "pcdesc_3": descripcion.upper(),
                    "pccodi_2": cuenta[:2], "pcdesc_2": "RESULTADOS", "pccodi_1": "4", "pcdesc_1_Modificado": "RESULTADOS", "pcdesc_1": "RESULTADOS",
                    "debe": real if "INGRESOS" not in nivel_1 else 0.0, "haber": real if "INGRESOS" in nivel_1 else 0.0, "saldo": real, "PPTO": presupuesto,
                })
                rows.append(row)

            efectivo = 2_400_000 * factor + idx * 85_000
            cuentas_por_cobrar = 1_650_000 * factor + idx * 58_000
            inventario = 620_000 * factor + idx * 12_000
            activo_no_corriente = 3_500_000 * factor + idx * 45_000
            pasivo_corriente = 1_720_000 * factor + idx * 36_000
            pasivo_no_corriente = 1_180_000 * factor + idx * 22_000
            patrimonio = (efectivo + cuentas_por_cobrar + inventario + activo_no_corriente - pasivo_corriente - pasivo_no_corriente)

            balance_rows = [
                ("110100", "Efectivo y Equivalentes", "ACTIVOS", "ACTIVO CORRIENTE", "ACTIVO CORRIENTE", efectivo),
                ("120100", "Cuentas por Cobrar", "ACTIVOS", "ACTIVO CORRIENTE", "ACTIVO CORRIENTE", cuentas_por_cobrar),
                ("130100", "Inventarios", "ACTIVOS", "ACTIVO CORRIENTE", "ACTIVO CORRIENTE", inventario),
                ("210100", "Propiedades Planta y Equipo", "ACTIVOS", "ACTIVO NO CORRIENTE", "ACTIVO NO CORRIENTE", activo_no_corriente),
                ("310100", "Pasivo Corriente", "PASIVOS Y PATRIMONIO", "PASIVO CORRIENTE", "PASIVO CORRIENTE", pasivo_corriente),
                ("320100", "Pasivo No Corriente", "PASIVOS Y PATRIMONIO", "PASIVO NO CORRIENTE", "PASIVO NO CORRIENTE", pasivo_no_corriente),
                ("410900", "Patrimonio", "PASIVOS Y PATRIMONIO", "PATRIMONIO", "PATRIMONIO", patrimonio),
            ]

            for cuenta, descripcion, nivel_1, nivel_2, nivel_3, real in balance_rows:
                row = _base_contable_row(month, unidad["centro_costo"], unidad["centro_costo_desc"], unidad["Nivel_3_CC"], unidad["Nivel_2_CC"], unidad["Nombre_Proyecto"], cuenta)
                row.update({
                    "Cuenta_IFRS": cuenta, "Nivel_1_IFRS": nivel_1, "Nivel_2_IFRS": nivel_2, "Nivel_3_IFRS": nivel_3, "Estado_Financiero": "BALANCE",
                    "pcdesc_4": descripcion, "pccodi_3": cuenta[:4], "pcdesc_3_Modificado": descripcion.upper(), "pcdesc_3": descripcion.upper(),
                    "pccodi_2": cuenta[:2], "pcdesc_2": nivel_2, "pccodi_1": cuenta[:1], "pcdesc_1_Modificado": nivel_1, "pcdesc_1": nivel_1,
                    "debe": real, "haber": 0.0, "saldo": real, "PPTO": 0.0,
                })
                rows.append(row)

    return pd.DataFrame(rows)

def build_demo_glosas() -> pd.DataFrame:
    today = pd.Timestamp.today().normalize()
    rows = []
    sample_rows = [
        ("CORP-001", "Corporativo", "410100", "ajimenez", "CMP-1001", "Reconocimiento ingreso mensual"),
        ("COM-010", "Ventas Consultoria", "510100", "mvaldes", "CMP-1002", "Costo directo de consultoria"),
        ("OPS-020", "Operaciones Proyectos", "610100", "lrojas", "CMP-1003", "Gasto operacional proyecto"),
    ]

    for idx in range(40):
        fecha_conta = today - pd.Timedelta(days=idx * 3)
        centro_costo, centro_desc, cuenta, usuario, comprobante, glosa = sample_rows[idx % len(sample_rows)]
        monto = 140_000 + idx * 6_500
        rows.append({
            "fecha": fecha_conta, "anio": fecha_conta.year, "mes": fecha_conta.month, "fecha_conta": fecha_conta,
            "centro_costo": centro_costo, "centro_costo_desc": centro_desc, "cuenta_contable": cuenta, "usuario": usuario,
            "numero_comprobante": comprobante, "glosa": glosa, "movdebe": monto if cuenta != "410100" else 0.0,
            "movhaber": monto if cuenta == "410100" else 0.0, "saldo": monto,
        })
    return pd.DataFrame(rows)

def load_all_data():
    """Carga los datos financieros desde Parquet. Genera demo data si no existen."""
    contable, c_warn = _read_parquet(CONTABLE_PARQUET, "contable")
    glosas, g_warn = _read_parquet(GLOSAS_PARQUET, "glosas")
    
    load_warnings = [w for w in [c_warn, g_warn] if w]
    
    using_demo = False
    if contable.empty or glosas.empty:
        using_demo = True
        if contable.empty:
            contable = build_demo_contable()
        if glosas.empty:
            glosas = build_demo_glosas()
            
    return {
        "contable": contable,
        "glosas": glosas,
        "meta": {
            "using_demo_data": using_demo,
            "load_warnings": load_warnings
        }
    }
