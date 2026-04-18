import unicodedata
from typing import Optional, Union, Any

import pandas as pd


DIMENSION_FILTERS: dict[str, str] = {}

MONTH_NAMES = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}

SHORT_MONTH_NAMES = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}

GASTOS_VENTA_CODES = {
    "4-3-01-016",
    "4-3-01-017",
    "4-3-01-035",
    "4-3-01-040",
    "4-3-01-043",
    "4-3-01-046",
    "4-3-01-052",
    "4-3-01-054",
}
GASTOS_FINANCIEROS_CODES = {"4-3-01-061"}
OTROS_RESULTADOS_NO_OP_CODES = {"4-3-01-014"}
PROVISION_MARGEN_CODES = {"5-3-01-003"}

EERR_LAYOUT = [
    ("detail", "INGRESOS"),
    ("detail", "COSTOS OPERACIONALES"),
    ("detail", "COSTO DE REMUNERACIONES"),
    ("subtotal", "MARGEN BRUTO"),
    ("blank", ""),
    ("detail", "INGRESO INTERNO"),
    ("detail", "COSTO INTERNO"),
    ("subtotal", "MARGEN BRUTO INTERNO"),
    ("blank", ""),
    ("detail", "GASTOS DE VENTAS"),
    ("detail", "GASTOS OPERACIONALES"),
    ("detail", "GASTOS DE REMUNERACIONES"),
    ("subtotal", "GASTOS ADM Y VENTAS"),
    ("blank", ""),
    ("subtotal", "MARGEN OPERACIONAL"),
    ("blank", ""),
    ("detail", "DEPRECIACIONES"),
    ("detail", "GASTOS FINANCIEROS"),
    ("detail", "INGRESOS NO OPERACIONAL"),
    ("detail", "OTROS RESULTADOS NO OPERACIONALES"),
    ("detail", "GASTOS NO OPERACIONALES"),
    ("subtotal", "NO OPERACIONAL"),
    ("blank", ""),
    ("subtotal", "MARGEN ANTES PROVISIÓN COMERCIAL"),
    ("detail", "PROVISIÓN MARGEN COMERCIAL"),
    ("blank", ""),
    ("subtotal", "MARGEN NETO RAI"),
    ("detail", "IMPUESTO A LAS GANANCIAS"),
    ("blank", ""),
    ("subtotal", "MARGEN NETO"),
]

DETAIL_LINE_LABELS = [label for row_type, label in EERR_LAYOUT if row_type == "detail"]
POSITIVE_DETAIL_LABELS = {
    "INGRESOS",
    "INGRESO INTERNO",
    "INGRESOS NO OPERACIONAL",
}


def _normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.upper().strip()


def _combine_text_fields(row: pd.Series, fields: list[str]) -> str:
    tokens = []
    for field in fields:
        value = _normalize_text(row.get(field))
        if value and value not in tokens:
            tokens.append(value)
    return " | ".join(tokens)


def _safe_div(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return numerator / denominator


def _apply_non_date_filters(df: pd.DataFrame, filters: Optional[dict]) -> pd.DataFrame:
    if df.empty or not filters:
        return df

    filtered = df.copy()
    for column, filter_key in DIMENSION_FILTERS.items():
        selected_values = filters.get(filter_key, [])
        if selected_values and column in filtered.columns:
            filtered = filtered[filtered[column].astype(str).isin(selected_values)]
    return filtered


def _current_reporting_period() -> pd.Timestamp:
    today = pd.Timestamp.today().normalize()
    if today.day < 15:
        today = (today.replace(day=1) - pd.DateOffset(months=1)).normalize()
    return today.replace(day=1)


def _format_period_label(date: pd.Timestamp, short: bool = False) -> str:
    month_names = SHORT_MONTH_NAMES if short else MONTH_NAMES
    month_name = month_names.get(date.month, date.strftime("%b"))
    separator = " " if short else "/"
    return f"{month_name}{separator}{date.year}"


def _prepare_contable(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    prepared = df.copy()
    
    # Fix PostgreSQL lowercasing issues by mapping expected mixed-case strings
    expected_cols = [
        "Estado_Financiero", "pcdesc_1_Modificado", "pcdesc_2", "pcdesc_3_Modificado",
        "pcdesc_4", "pcdesc_1", "pcdesc_3", "Nivel_1_IFRS", "Nivel_2_IFRS", "Nivel_3_IFRS",
        "PPTO", "saldo",
    ]
    renames = {}
    for actual_col in prepared.columns:
        for expected in expected_cols:
            if actual_col.lower() == expected.lower() and actual_col != expected:
                renames[actual_col] = expected
    
    if renames:
        prepared = prepared.rename(columns=renames)

    if "fecha" not in prepared.columns and "anio" in prepared.columns and "mes" in prepared.columns:
        prepared["fecha"] = pd.to_datetime(prepared["anio"].astype(int).astype(str) + "-" + prepared["mes"].astype(int).astype(str) + "-01")
    elif "fecha" in prepared.columns:
        prepared["fecha"] = pd.to_datetime(prepared["fecha"], errors="coerce")
    prepared["real_abs"] = prepared["saldo"].abs()
    prepared["ppto_abs"] = prepared["PPTO"].abs()

    statement_cols = [
        "Estado_Financiero",
        "pcdesc_1_Modificado",
        "pcdesc_2",
        "pcdesc_3_Modificado",
        "pcdesc_4",
        "Nivel_1_IFRS",
        "Nivel_2_IFRS",
        "Nivel_3_IFRS",
    ]
    detail_cols = [
        "Nivel_1_IFRS",
        "Nivel_2_IFRS",
        "Nivel_3_IFRS",
        "pcdesc_1_Modificado",
        "pcdesc_2",
        "pcdesc_3_Modificado",
        "pcdesc_4",
    ]

    # Optimization: Apply slow Python text normalizing/deduplicating only to unique combinations (~500 rows instead of 600K)
    unique_texts = prepared[statement_cols].drop_duplicates().copy()
    unique_texts["statement_text"] = unique_texts.apply(
        lambda row: _combine_text_fields(row, statement_cols), axis=1
    )
    unique_texts["detail_text"] = unique_texts.apply(
        lambda row: _combine_text_fields(row, detail_cols), axis=1
    )

    prepared = prepared.merge(unique_texts, on=statement_cols, how="left")

    prepared["statement_group"] = prepared["statement_text"].map(_classify_statement_group)
    prepared["balance_bucket"] = prepared["detail_text"].map(_classify_balance_bucket)
    prepared["is_cash_equivalent"] = prepared["detail_text"].map(_is_cash_equivalent)
    prepared["eerr_detail_label"] = prepared.apply(_classify_eerr_detail_label, axis=1)
    return prepared


def _classify_statement_group(text: str) -> str:
    if any(keyword in text for keyword in ["ACTIVO", "PASIVO", "PATRIMONIO", "BALANCE"]):
        return "BALANCE"
    if "ORDEN" in text:
        return "ORDEN"
    return "EERR"


def _classify_balance_bucket(text: str) -> str:
    if "PATRIMONIO" in text:
        return "patrimonio"
    if "PASIVO CORRIENTE" in text:
        return "pasivo_corriente"
    if "PASIVO" in text:
        return "pasivo_no_corriente"
    if "ACTIVO CORRIENTE" in text:
        return "activo_corriente"
    if "ACTIVO" in text:
        return "activo_no_corriente"
    return "otros"


def _is_cash_equivalent(text: str) -> bool:
    return any(keyword in text for keyword in ["EFECTIVO", "CAJA", "BANCO", "EQUIVALENTES"])


def _classify_eerr_detail_label(row: pd.Series) -> Optional[str]:
    if row.get("statement_group") != "EERR":
        return None

    code = _normalize_text(row.get("pccodi_4") or row.get("cuenta_contable"))
    text = row.get("detail_text", "")

    if "CORRECCION MONETARIA" in text:
        return None
    if "INGRESO INTERNO" in text or ("INTERNO" in text and any(token in text for token in ["INGRESO", "VENTA"])):
        return "INGRESO INTERNO"
    if "COSTO INTERNO" in text or ("INTERNO" in text and "COSTO" in text):
        return "COSTO INTERNO"
    if code in GASTOS_VENTA_CODES or "GASTOS DE VENTAS" in text or "GASTOS DE VENTA" in text:
        return "GASTOS DE VENTAS"
    if code in GASTOS_FINANCIEROS_CODES or "GASTOS FINANCIEROS" in text or "RESULTADO FINANCIERO" in text:
        return "GASTOS FINANCIEROS"
    if code in OTROS_RESULTADOS_NO_OP_CODES or "OTROS RESULTADOS NO OPERACIONALES" in text:
        return "OTROS RESULTADOS NO OPERACIONALES"
    if code in PROVISION_MARGEN_CODES or "PROVISION MARGEN COMERCIAL" in text:
        return "PROVISIÓN MARGEN COMERCIAL"
    if "IMPUESTO A LAS GANANCIAS" in text or "IMPUESTO" in text:
        return "IMPUESTO A LAS GANANCIAS"
    if "COSTO DE REMUNERACIONES" in text or ("REMUNER" in text and "COSTO" in text):
        return "COSTO DE REMUNERACIONES"
    if "GASTOS DE REMUNERACIONES" in text or ("REMUNER" in text and "GASTO" in text):
        return "GASTOS DE REMUNERACIONES"
    if "INGRESOS NO OPERACIONALES" in text or ("INGRESO" in text and "NO OPERACIONAL" in text):
        return "INGRESOS NO OPERACIONAL"
    if "GASTOS NO OPERACIONALES" in text or ("GASTO" in text and "NO OPERACIONAL" in text):
        return "GASTOS NO OPERACIONALES"
    if "DEPRECI" in text or "AMORT" in text:
        return "DEPRECIACIONES"
    if "COSTOS OPERACIONALES" in text or "COSTO DE VENTA" in text or "COSTOS DE VENTA" in text:
        return "COSTOS OPERACIONALES"
    if "GASTOS OPERACIONALES" in text:
        return "GASTOS OPERACIONALES"
    if "INGRESOS OPERACIONALES" in text or (("INGRESO" in text or "VENTA" in text) and "NO OPERACIONAL" not in text):
        return "INGRESOS"
    return None


def _scoped_reference(reference_df: pd.DataFrame, filters: Optional[dict]) -> pd.DataFrame:
    prepared = _prepare_contable(reference_df)
    return _apply_non_date_filters(prepared, filters)


def _resolve_anchor_date(
    filtered_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    filters: Optional[dict],
) -> pd.Timestamp:
    anchor = _current_reporting_period()

    date_range = (filters or {}).get("date_range")
    if date_range:
        range_end = pd.to_datetime(date_range[1]).normalize().replace(day=1)
        if range_end < anchor:
            anchor = range_end

    scoped = _scoped_reference(reference_df, filters)
    if scoped.empty or scoped["fecha"].dropna().empty:
        return anchor

    available_periods = scoped["fecha"].dropna().dt.to_period("M").sort_values().unique()
    target_period = anchor.to_period("M")
    eligible = [period for period in available_periods if period <= target_period]
    if eligible:
        return eligible[-1].to_timestamp()
    return available_periods[-1].to_timestamp()


def _slice_specific_month(scoped_df: pd.DataFrame, target_date: pd.Timestamp) -> pd.DataFrame:
    if scoped_df.empty:
        return scoped_df
    target = pd.Timestamp(target_date).replace(day=1)
    return scoped_df[
        (scoped_df["fecha"].dt.year == target.year)
        & (scoped_df["fecha"].dt.month == target.month)
    ]


def _slice_period(
    scoped_df: pd.DataFrame,
    anchor_date: pd.Timestamp,
    mode: str,
    year_offset: int = 0,
    periods: int = 12,
) -> pd.DataFrame:
    if scoped_df.empty:
        return scoped_df

    shifted_anchor = (pd.Timestamp(anchor_date).replace(day=1) + pd.DateOffset(years=year_offset)).normalize()

    if mode == "month":
        return _slice_specific_month(scoped_df, shifted_anchor)

    if mode == "ytd":
        return scoped_df[
            (scoped_df["fecha"].dt.year == shifted_anchor.year)
            & (scoped_df["fecha"].dt.month <= shifted_anchor.month)
        ]

    if mode == "rolling":
        start_date = shifted_anchor - pd.DateOffset(months=periods - 1)
        end_date = shifted_anchor + pd.offsets.MonthEnd(0)
        return scoped_df[(scoped_df["fecha"] >= start_date) & (scoped_df["fecha"] <= end_date)]

    return scoped_df


def _empty_line_values() -> dict[str, float]:
    return {"real": 0.0, "ppto": 0.0}


def _signed_line_value(label: str, amount: float) -> float:
    if label in POSITIVE_DETAIL_LABELS:
        return amount
    return -amount


def _sum_line_values(line_values: dict[str, dict[str, float]], labels: list[str]) -> dict[str, float]:
    return {
        "real": sum(line_values.get(label, _empty_line_values())["real"] for label in labels),
        "ppto": sum(line_values.get(label, _empty_line_values())["ppto"] for label in labels),
    }


def _aggregate_eerr_lines(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    line_values = {label: _empty_line_values() for label in DETAIL_LINE_LABELS}
    if df.empty:
        return _append_derived_lines(line_values)

    details = df[df["eerr_detail_label"].notna()]
    if not details.empty:
        grouped = details.groupby("eerr_detail_label")[["real_abs", "ppto_abs"]].sum()
        for label in DETAIL_LINE_LABELS:
            line_values[label] = {
                "real": _signed_line_value(label, float(grouped["real_abs"].get(label, 0.0))),
                "ppto": _signed_line_value(label, float(grouped["ppto_abs"].get(label, 0.0))),
            }

    return _append_derived_lines(line_values)


def _append_derived_lines(line_values: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    derived = dict(line_values)
    derived["MARGEN BRUTO"] = _sum_line_values(
        derived,
        ["INGRESOS", "COSTOS OPERACIONALES", "COSTO DE REMUNERACIONES"],
    )
    derived["MARGEN BRUTO INTERNO"] = _sum_line_values(
        derived,
        ["INGRESO INTERNO", "COSTO INTERNO"],
    )
    derived["GASTOS ADM Y VENTAS"] = _sum_line_values(
        derived,
        ["GASTOS DE VENTAS", "GASTOS OPERACIONALES", "GASTOS DE REMUNERACIONES"],
    )
    derived["MARGEN OPERACIONAL"] = _sum_line_values(
        derived,
        ["MARGEN BRUTO", "MARGEN BRUTO INTERNO", "GASTOS ADM Y VENTAS"],
    )
    derived["NO OPERACIONAL"] = _sum_line_values(
        derived,
        [
            "DEPRECIACIONES",
            "GASTOS FINANCIEROS",
            "INGRESOS NO OPERACIONAL",
            "OTROS RESULTADOS NO OPERACIONALES",
            "GASTOS NO OPERACIONALES",
        ],
    )
    derived["MARGEN ANTES PROVISIÓN COMERCIAL"] = _sum_line_values(
        derived,
        ["MARGEN OPERACIONAL", "NO OPERACIONAL"],
    )
    derived["MARGEN NETO RAI"] = _sum_line_values(
        derived,
        ["MARGEN ANTES PROVISIÓN COMERCIAL", "PROVISIÓN MARGEN COMERCIAL"],
    )
    derived["MARGEN NETO"] = _sum_line_values(
        derived,
        ["MARGEN NETO RAI", "IMPUESTO A LAS GANANCIAS"],
    )
    return derived


def _aggregate_balance(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "activo_corriente": 0.0,
            "activo_no_corriente": 0.0,
            "pasivo_corriente": 0.0,
            "pasivo_no_corriente": 0.0,
            "patrimonio": 0.0,
            "efectivo": 0.0,
            "fecha_corte": None,
        }

    balance = df[df["statement_group"] == "BALANCE"]
    if balance.empty:
        return {
            "activo_corriente": 0.0,
            "activo_no_corriente": 0.0,
            "pasivo_corriente": 0.0,
            "pasivo_no_corriente": 0.0,
            "patrimonio": 0.0,
            "efectivo": 0.0,
            "fecha_corte": None,
        }

    latest_date = balance["fecha"].max()
    snapshot = balance[balance["fecha"] == latest_date]
    grouped = snapshot.groupby("balance_bucket")["real_abs"].sum()
    return {
        "activo_corriente": float(grouped.get("activo_corriente", 0.0)),
        "activo_no_corriente": float(grouped.get("activo_no_corriente", 0.0)),
        "pasivo_corriente": float(grouped.get("pasivo_corriente", 0.0)),
        "pasivo_no_corriente": float(grouped.get("pasivo_no_corriente", 0.0)),
        "patrimonio": float(grouped.get("patrimonio", 0.0)),
        "efectivo": float(snapshot.loc[snapshot["is_cash_equivalent"], "real_abs"].sum()),
        "fecha_corte": latest_date,
    }


def build_resumen_dashboard(
    filtered_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    filters: Optional[dict] = None,
) -> dict[str, object]:
    scoped = _scoped_reference(reference_df, filters)
    anchor_date = _resolve_anchor_date(filtered_df, reference_df, filters)

    current_month_df = _slice_period(scoped, anchor_date, "month")
    previous_year_month_df = _slice_period(scoped, anchor_date, "month", year_offset=-1)
    previous_month_df = _slice_specific_month(scoped, anchor_date - pd.DateOffset(months=1))
    current_ttm_df = _slice_period(scoped, anchor_date, "rolling", periods=12)
    previous_year_ttm_df = _slice_period(scoped, anchor_date, "rolling", year_offset=-1, periods=12)

    current_month = _aggregate_eerr_lines(current_month_df)
    previous_year_month = _aggregate_eerr_lines(previous_year_month_df)
    current_ttm = _aggregate_eerr_lines(current_ttm_df)
    previous_year_ttm = _aggregate_eerr_lines(previous_year_ttm_df)

    current_balance = _aggregate_balance(current_month_df)
    previous_month_balance = _aggregate_balance(previous_month_df)
    previous_year_balance = _aggregate_balance(previous_year_month_df)

    current_assets = current_balance["activo_corriente"] + current_balance["activo_no_corriente"]
    previous_assets = previous_year_balance["activo_corriente"] + previous_year_balance["activo_no_corriente"]

    current_liquidity = _safe_div(current_balance["activo_corriente"], current_balance["pasivo_corriente"])
    previous_liquidity = _safe_div(previous_month_balance["activo_corriente"], previous_month_balance["pasivo_corriente"])

    current_roa = _safe_div(current_ttm["MARGEN NETO"]["real"], current_assets)
    previous_roa = _safe_div(previous_year_ttm["MARGEN NETO"]["real"], previous_assets)

    current_roe = _safe_div(current_ttm["MARGEN NETO"]["real"], current_balance["patrimonio"])
    previous_roe = _safe_div(previous_year_ttm["MARGEN NETO"]["real"], previous_year_balance["patrimonio"])

    ingresos_month = current_month["INGRESOS"]["real"]
    ingresos_previous_year = previous_year_month["INGRESOS"]["real"]
    ingresos_growth = _safe_div(ingresos_month - ingresos_previous_year, abs(ingresos_previous_year))
    ingresos_budget_delta = _safe_div(
        ingresos_month - current_month["INGRESOS"]["ppto"],
        abs(current_month["INGRESOS"]["ppto"]),
    )

    margen_bruto_pct = _safe_div(current_month["MARGEN BRUTO"]["real"], ingresos_month)
    margen_bruto_previous = _safe_div(previous_year_month["MARGEN BRUTO"]["real"], ingresos_previous_year)

    margen_operacional_pct = _safe_div(current_month["MARGEN OPERACIONAL"]["real"], ingresos_month)
    margen_operacional_previous = _safe_div(previous_year_month["MARGEN OPERACIONAL"]["real"], ingresos_previous_year)

    ebitda_month = current_month["MARGEN OPERACIONAL"]["real"]
    ebitda_delta = _safe_div(
        ebitda_month - current_month["MARGEN OPERACIONAL"]["ppto"],
        abs(current_month["MARGEN OPERACIONAL"]["ppto"]),
    )

    resultado_month = current_month["MARGEN NETO"]["real"]
    resultado_delta = _safe_div(
        resultado_month - current_month["MARGEN NETO"]["ppto"],
        abs(current_month["MARGEN NETO"]["ppto"]),
    )

    cards = [
        {
            "title": "Crecimiento de Ingresos",
            "value": ingresos_growth,
            "value_type": "percent",
            "delta": ingresos_budget_delta,
            "delta_label": "vs ppto",
            "meta": "Mes actual vs mismo mes ano anterior",
        },
        {
            "title": "EBITDA",
            "value": ebitda_month,
            "value_type": "currency",
            "delta": ebitda_delta,
            "delta_label": "vs ppto",
            "meta": "Mes actual",
        },
        {
            "title": "Margen Bruto",
            "value": margen_bruto_pct,
            "value_type": "percent",
            "delta": margen_bruto_pct - margen_bruto_previous,
            "delta_label": "pp vs AA",
            "meta": "Mes actual sobre ventas",
        },
        {
            "title": "Margen Operacional",
            "value": margen_operacional_pct,
            "value_type": "percent",
            "delta": margen_operacional_pct - margen_operacional_previous,
            "delta_label": "pp vs AA",
            "meta": "Mes actual sobre ventas",
        },
        {
            "title": "Caja / Liquidez",
            "value": current_liquidity,
            "value_type": "ratio",
            "meta": f"Caja al cierre: {current_balance['efectivo']}",
            "extra_meta_type": "currency",
            "extra_meta_value": current_balance["efectivo"],
        },
        {
            "title": "ROA",
            "value": current_roa,
            "value_type": "percent",
            "delta": current_roa - previous_roa,
            "delta_label": "pp vs AA",
            "meta": "Resultado TTM / activos",
        },
        {
            "title": "ROE",
            "value": current_roe,
            "value_type": "percent",
            "delta": current_roe - previous_roe,
            "delta_label": "pp vs AA",
            "meta": "Resultado TTM / patrimonio",
        },
        {
            "title": "Resultado del Ejercicio",
            "value": resultado_month,
            "value_type": "currency",
            "delta": resultado_delta,
            "delta_label": "vs ppto",
            "meta": "Mes actual",
        },
    ]

    return {
        "anchor_date": anchor_date,
        "period_label": _format_period_label(anchor_date),
        "cards": cards,
    }


def build_resumen_trends(
    filtered_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    filters: Optional[dict] = None,
) -> Union[dict, pd.DataFrame, pd.Timestamp]:
    scoped = _scoped_reference(reference_df, filters)
    anchor_date = _resolve_anchor_date(filtered_df, reference_df, filters)
    periods = pd.period_range(end=anchor_date.to_period("M"), periods=12, freq="M")

    rows = []
    for period in periods:
        period_date = period.to_timestamp()
        month_df = _slice_specific_month(scoped, period_date)
        month_lines = _aggregate_eerr_lines(month_df)
        ingresos = month_lines["INGRESOS"]["real"]
        margen_bruto = month_lines["MARGEN BRUTO"]["real"]
        rows.append(
            {
                "fecha": period_date,
                "mes_label": _format_period_label(period_date, short=True),
                "ingresos_real": ingresos,
                "ingresos_ppto": month_lines["INGRESOS"]["ppto"],
                "margen_bruto_real": margen_bruto,
                "margen_bruto_ppto": month_lines["MARGEN BRUTO"]["ppto"],
                "margen_bruto_pct": _safe_div(margen_bruto, ingresos),
            }
        )

    trend_df = pd.DataFrame(rows)
    return {"anchor_date": anchor_date, "trend": trend_df}


def build_eerr_statement(
    filtered_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    filters: Optional[dict] = None,
) -> dict[str, object]:
    scoped = _scoped_reference(reference_df, filters)
    anchor_date = _resolve_anchor_date(filtered_df, reference_df, filters)

    current_ytd_df = _slice_period(scoped, anchor_date, "ytd")
    previous_ytd_df = _slice_period(scoped, anchor_date, "ytd", year_offset=-1)

    current_lines = _aggregate_eerr_lines(current_ytd_df)
    previous_lines = _aggregate_eerr_lines(previous_ytd_df)

    ventas_real = current_lines["INGRESOS"]["real"]
    ventas_ppto = current_lines["INGRESOS"]["ppto"]

    rows = []
    for row_type, label in EERR_LAYOUT:
        if row_type == "blank":
            rows.append({"row_type": row_type, "label": ""})
            continue

        current = current_lines.get(label, _empty_line_values())
        previous = previous_lines.get(label, _empty_line_values())
        real = current["real"]
        presupuesto = current["ppto"]
        real_aa = previous["real"]

        rows.append(
            {
                "row_type": row_type,
                "label": label,
                "presupuesto": presupuesto,
                "pct_presupuesto": _safe_div(presupuesto, ventas_ppto),
                "real": real,
                "pct_real": _safe_div(real, ventas_real),
                "var_real_ppto": real - presupuesto,
                "var_real_ppto_pct": _safe_div(real - presupuesto, abs(presupuesto)),
                "real_aa": real_aa,
                "var_real_aa": real - real_aa,
                "var_real_aa_pct": _safe_div(real - real_aa, abs(real_aa)),
            }
        )

    return {
        "anchor_date": anchor_date,
        "title": f"EERR - {_format_period_label(anchor_date)}",
        "subtitle": "ACUMULADO",
        "rows": pd.DataFrame(rows),
    }


def build_balance_snapshot(
    filtered_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    filters: Optional[dict] = None,
) -> dict[str, object]:
    scoped = _scoped_reference(reference_df, filters)
    anchor_date = _resolve_anchor_date(filtered_df, reference_df, filters)
    current_month_df = _slice_period(scoped, anchor_date, "month")
    current_balance = _aggregate_balance(current_month_df)
    ttm_lines = _aggregate_eerr_lines(_slice_period(scoped, anchor_date, "rolling", periods=12))

    activos = current_balance["activo_corriente"] + current_balance["activo_no_corriente"]
    pasivos = current_balance["pasivo_corriente"] + current_balance["pasivo_no_corriente"]
    patrimonio = current_balance["patrimonio"]

    components = pd.DataFrame(
        [
            {"Componente": "Activo Corriente", "Monto": current_balance["activo_corriente"]},
            {"Componente": "Activo No Corriente", "Monto": current_balance["activo_no_corriente"]},
            {"Componente": "Pasivo Corriente", "Monto": current_balance["pasivo_corriente"]},
            {"Componente": "Pasivo No Corriente", "Monto": current_balance["pasivo_no_corriente"]},
            {"Componente": "Patrimonio", "Monto": patrimonio},
        ]
    )

    ratios = pd.DataFrame(
        [
            {"Ratio": "Liquidez Corriente", "Valor": _safe_div(current_balance["activo_corriente"], current_balance["pasivo_corriente"])},
            {"Ratio": "Endeudamiento", "Valor": _safe_div(pasivos, activos)},
            {"Ratio": "Leverage", "Valor": _safe_div(pasivos, patrimonio)},
            {"Ratio": "ROA", "Valor": _safe_div(ttm_lines["MARGEN NETO"]["real"], activos)},
            {"Ratio": "ROE", "Valor": _safe_div(ttm_lines["MARGEN NETO"]["real"], patrimonio)},
        ]
    )

    return {
        "cards": {
            "activos": activos,
            "pasivos": pasivos,
            "patrimonio": patrimonio,
            "capital_trabajo": current_balance["activo_corriente"] - current_balance["pasivo_corriente"],
            "fecha_corte": current_balance["fecha_corte"] or anchor_date,
        },
        "components": components,
        "ratios": ratios,
    }


def build_glosas_summary(df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {
            "total_registros": 0,
            "movimiento_debe": 0.0,
            "movimiento_haber": 0.0,
            "top_cuentas": pd.DataFrame(columns=["Cuenta", "Registros", "Glosas"]),
        }

    total = int(df["Cantidad_Registros_Contables"].sum()) if "Cantidad_Registros_Contables" in df.columns else len(df)
    debe  = float(df["debe"].sum())  if "debe"  in df.columns else 0.0
    haber = float(df["haber"].sum()) if "haber" in df.columns else 0.0

    top_cuentas = (
        df.groupby("cuenta_contable")
        .agg(
            Registros=("Cantidad_Registros_Contables", "sum"),
            Glosas=("Cantidad_Glosas", "sum"),
        )
        .reset_index()
        .rename(columns={"cuenta_contable": "Cuenta"})
        .sort_values("Registros", ascending=False)
        .head(10)
    )

    return {
        "total_registros": total,
        "movimiento_debe": debe,
        "movimiento_haber": haber,
        "top_cuentas": top_cuentas,
    }

def format_currency(value: float, decimals: int = 1) -> str:
    scale = abs(value)
    if scale >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.{decimals}f}B"
    if scale >= 1_000_000:
        return f"${value / 1_000_000:,.{decimals}f}M"
    if scale >= 1_000:
        return f"${value / 1_000:,.{decimals}f}K"
    return f"${value:,.0f}"


def format_number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{value * 100:,.{decimals}f}%"


def format_ratio(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}x"


def format_accounting(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}"


def build_demo_contable() -> pd.DataFrame: return pd.DataFrame()
def build_demo_glosas() -> pd.DataFrame: return pd.DataFrame()
