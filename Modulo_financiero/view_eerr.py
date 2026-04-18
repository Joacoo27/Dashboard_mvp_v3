import html

import streamlit as st

from .logic import format_accounting, format_percent
from .logic import build_eerr_statement
from .ui_helpers import render_header


def _format_eerr_value(value: float, value_type: str) -> str:
    if value_type == "percent":
        return format_percent(value, decimals=2)
    return format_accounting(value)


def _cell_class(value: float) -> str:
    if value < 0:
        return "eerr-negative"
    return ""


def _build_eerr_html(statement_rows) -> str:
    header_cells = [
        "",
        "PPTO",
        "% PPTO<br>SOBRE<br>VENTAS",
        "REAL",
        "% REAL<br>SOBRE<br>VENTAS",
        "VAR<br>REAL/PPTO",
        "VAR %<br>REAL/PPTO",
        "REAL AÑO<br>ANT",
        "VAR<br>REAL/AÑO ANT",
        "VAR<br>REAL/AÑO ANT %",
    ]

    html_rows = []
    for _, row in statement_rows.iterrows():
        row_type = row["row_type"]
        if row_type == "blank":
            html_rows.append('<tr class="eerr-spacer"><td colspan="10"></td></tr>')
            continue

        row_class = "eerr-subtotal" if row_type == "subtotal" else ""
        values = [
            ("presupuesto", "currency"),
            ("pct_presupuesto", "percent"),
            ("real", "currency"),
            ("pct_real", "percent"),
            ("var_real_ppto", "currency"),
            ("var_real_ppto_pct", "percent"),
            ("real_aa", "currency"),
            ("var_real_aa", "currency"),
            ("var_real_aa_pct", "percent"),
        ]

        cells = [f'<td class="eerr-label">{html.escape(row["label"])}</td>']
        for field, value_type in values:
            value = row[field]
            css_class = _cell_class(value)
            formatted = _format_eerr_value(value, value_type)
            cells.append(f'<td class="{css_class}">{formatted}</td>')

        html_rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    return (
        '<div class="eerr-table-scroll">'
        '<table class="eerr-table">'
        f"<thead><tr>{''.join(f'<th>{cell}</th>' for cell in header_cells)}</tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody>"
        "</table>"
        "</div>"
    )


def render(bundle: dict[str, object]) -> None:
    df_contable = bundle["contable"]
    reference_contable = bundle.get("reference_contable", df_contable)
    filters = bundle.get("meta", {}).get("active_filters", {})

    render_header(
        "EE.RR",
        "Vista acumulada al mes de corte, replicando la logica comparativa del panel financiero de Tableau.",
    )

    statement = build_eerr_statement(df_contable, reference_contable, filters)
    rows = statement["rows"]
    if rows.empty:
        st.info("No hay datos para construir el EE.RR con la seleccion actual.")
        return

    report_html = (
        '<div class="eerr-report-shell">'
        f'<div class="eerr-title">{html.escape(statement["title"])}</div>'
        f'<div class="eerr-subtitle">{html.escape(statement["subtitle"])}</div>'
        f'{_build_eerr_html(rows)}'
        "</div>"
    )
    st.markdown(report_html, unsafe_allow_html=True)
