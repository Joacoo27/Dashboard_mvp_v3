import pandas as pd
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent
CACHE_DIR = PROJECT_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CONTABLE_PARQUET = CACHE_DIR / "contable_financiero_cache.parquet"


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


@st.cache_resource
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


def _base_contable_row(fecha: pd.Timestamp, cuenta_contable: str) -> dict:
    last_day = (fecha + pd.offsets.MonthEnd(0)).date()
    return {
        "anio": fecha.year,
        "mes": fecha.month,
        "cuenta_contable": cuenta_contable,
        "pccodi_4": cuenta_contable,
        "debe": 0.0,
        "haber": 0.0,
        "saldo": 0.0,
        "PPTO": 0.0,
        "Primera_Fecha_Conta": fecha.date(),
        "Ultima_Fecha_Conta": last_day,
        "Cantidad_Registros_Contables": 10,
        "Cantidad_Comprobantes": 3,
        "Cantidad_Glosas": 4,
        "Glosas_Consolidadas": "Registro demo",
        "Cantidad_Usuarios": 2,
        "Usuarios_Contables": "usuario_a | usuario_b",
        "Nivel_Ratio": None,
    }


def build_demo_contable() -> pd.DataFrame:
    current_month = pd.Timestamp.today().normalize().replace(day=1)
    months = pd.date_range(end=current_month, periods=24, freq="MS")
    rows = []

    for idx, month in enumerate(months):
        base = 940_000 + idx * 26_000
        ingresos          = base * 3.55
        costo_venta       = ingresos * 0.54
        gastos_op         = ingresos * 0.17
        depreciacion      = ingresos * 0.025
        gasto_fin         = ingresos * 0.012
        ppto_ing          = ingresos * 0.97

        eerr_defs = [
            ("410100", "Ingresos", "INGRESOS", "INGRESOS OPERACIONALES", "ESTADO DE RESULTADOS",
             ingresos, ppto_ing),
            ("510100", "Costo de Venta", "COSTO DE VENTA", "COSTO DE VENTA", "ESTADO DE RESULTADOS",
             costo_venta, ppto_ing * 0.53),
            ("610100", "Gastos Operacionales", "GASTOS OPERACIONALES", "GASTOS OPERACIONALES", "ESTADO DE RESULTADOS",
             gastos_op, ppto_ing * 0.165),
            ("620100", "Depreciacion", "GASTOS OPERACIONALES", "DEPRECIACION", "ESTADO DE RESULTADOS",
             depreciacion, ppto_ing * 0.024),
            ("710100", "Resultado Financiero", "RESULTADO FINANCIERO", "NO OPERACIONAL", "ESTADO DE RESULTADOS",
             gasto_fin, ppto_ing * 0.011),
        ]
        for cuenta, desc, nivel_1, nivel_3, estado, real, ppto in eerr_defs:
            row = _base_contable_row(month, cuenta)
            row.update({
                "Cuenta_IFRS": cuenta,
                "Nivel_1_IFRS": nivel_1,
                "Nivel_2_IFRS": desc,
                "Nivel_3_IFRS": nivel_3,
                "Nivel_3_IFRS_Original": nivel_3,
                "Estado_Financiero": estado,
                "pcdesc_4": desc,
                "pccodi_3": cuenta[:4],
                "pcdesc_3_Modificado": desc.upper(),
                "pcdesc_3": desc.upper(),
                "pccodi_2": cuenta[:2],
                "pcdesc_2": "RESULTADOS",
                "pccodi_1": "4",
                "pcdesc_1_Modificado": "RESULTADOS",
                "pcdesc_1": "RESULTADOS",
                "debe":  real if "INGRESOS" not in nivel_1 else 0.0,
                "haber": real if "INGRESOS" in nivel_1 else 0.0,
                "saldo": real,
                "PPTO": ppto,
            })
            rows.append(row)

        efectivo           = 2_400_000 + idx * 85_000
        cuentas_cobrar     = 1_650_000 + idx * 58_000
        inventario         = 620_000   + idx * 12_000
        activo_nc          = 3_500_000 + idx * 45_000
        pasivo_c           = 1_720_000 + idx * 36_000
        pasivo_nc          = 1_180_000 + idx * 22_000
        patrimonio         = efectivo + cuentas_cobrar + inventario + activo_nc - pasivo_c - pasivo_nc

        balance_defs = [
            ("110100", "Efectivo y Equivalentes", "ACTIVOS", "ACTIVO CORRIENTE",    "ACTIVO CORRIENTE",    efectivo),
            ("120100", "Cuentas por Cobrar",       "ACTIVOS", "ACTIVO CORRIENTE",    "ACTIVO CORRIENTE",    cuentas_cobrar),
            ("130100", "Inventarios",              "ACTIVOS", "ACTIVO CORRIENTE",    "ACTIVO CORRIENTE",    inventario),
            ("210100", "Propiedades Planta Equipo","ACTIVOS", "ACTIVO NO CORRIENTE", "ACTIVO NO CORRIENTE", activo_nc),
            ("310100", "Pasivo Corriente",  "PASIVOS Y PATRIMONIO", "PASIVO CORRIENTE",    "PASIVO CORRIENTE",    pasivo_c),
            ("320100", "Pasivo No Corriente","PASIVOS Y PATRIMONIO", "PASIVO NO CORRIENTE", "PASIVO NO CORRIENTE", pasivo_nc),
            ("410900", "Patrimonio",        "PASIVOS Y PATRIMONIO", "PATRIMONIO",          "PATRIMONIO",          patrimonio),
        ]
        for cuenta, desc, nivel_1, nivel_2, nivel_3, real in balance_defs:
            row = _base_contable_row(month, cuenta)
            row.update({
                "Cuenta_IFRS": cuenta,
                "Nivel_1_IFRS": nivel_1,
                "Nivel_2_IFRS": nivel_2,
                "Nivel_3_IFRS": nivel_3,
                "Nivel_3_IFRS_Original": nivel_3,
                "Estado_Financiero": "BALANCE",
                "pcdesc_4": desc,
                "pccodi_3": cuenta[:4],
                "pcdesc_3_Modificado": desc.upper(),
                "pcdesc_3": desc.upper(),
                "pccodi_2": cuenta[:2],
                "pcdesc_2": nivel_2,
                "pccodi_1": cuenta[:1],
                "pcdesc_1_Modificado": nivel_1,
                "pcdesc_1": nivel_1,
                "debe": real,
                "haber": 0.0,
                "saldo": real,
                "PPTO": 0.0,
            })
            rows.append(row)

    return pd.DataFrame(rows)


def load_all_data() -> dict:
    """Carga los datos financieros desde Parquet. Genera demo data si no existe cache."""
    contable, c_warn = _read_parquet(CONTABLE_PARQUET, "contable")
    load_warnings = [c_warn] if c_warn else []

    using_demo = False
    if contable.empty:
        using_demo = True
        contable = build_demo_contable()

    return {
        "contable": contable,
        "meta": {
            "using_demo_data": using_demo,
            "load_warnings": load_warnings,
        },
    }
