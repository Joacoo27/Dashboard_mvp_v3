import html
import io

import pandas as pd
import streamlit as st

from .logic import format_accounting, format_percent, build_eerr_statement
from core.components import render_header, render_pills


# ── helpers ───────────────────────────────────────────────────────────────────

def _fmt(value: float, value_type: str) -> str:
    if value_type == "percent":
        return format_percent(value, decimals=2)
    return format_accounting(value)


def _cell_cls(value: float) -> str:
    return "eerr-negative" if value < 0 else ""


def _cumpl_bar(real: float, presupuesto: float) -> str:
    """Mini progress bar HTML for Cumpl.% column."""
    if not presupuesto:
        return '<td style="text-align:right;">—</td>'

    pct = (real / presupuesto) * 100
    if pct >= 100:
        color = "#2bb673"
    elif pct >= 80:
        color = "#f59e0b"
    else:
        color = "#ef4444"

    bar_w = min(pct, 130) / 130 * 64   # max 64 px
    bar_w = max(bar_w, 2)

    return (
        '<td style="text-align:right;">'
        '<div class="eerr-cumpl-wrap">'
        f'<div class="eerr-cumpl-bar" style="width:{bar_w:.0f}px;background:{color};"></div>'
        f'<span class="eerr-cumpl-label" style="color:{color};font-weight:700;">{pct:.0f}%</span>'
        "</div>"
        "</td>"
    )


def _build_eerr_html(statement_rows: pd.DataFrame) -> str:
    headers = [
        "Cuenta", "PPTO", "% PPTO<br>/ Ventas", "Real",
        "% Real<br>/ Ventas", "Var.<br>Real/PPTO", "Var. %<br>Real/PPTO",
        "Real<br>Año Ant.", "Var.<br>Real/Año Ant.", "Var. %<br>Real/Año Ant.", "Cumpl.",
    ]
    header_row = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = []
    for _, row in statement_rows.iterrows():
        row_type = row["row_type"]
        if row_type == "blank":
            rows_html.append('<tr class="eerr-spacer"><td colspan="11"></td></tr>')
            continue

        row_class = "eerr-subtotal" if row_type == "subtotal" else ""
        fields = [
            ("presupuesto",      "currency"),
            ("pct_presupuesto",  "percent"),
            ("real",             "currency"),
            ("pct_real",         "percent"),
            ("var_real_ppto",    "currency"),
            ("var_real_ppto_pct","percent"),
            ("real_aa",          "currency"),
            ("var_real_aa",      "currency"),
            ("var_real_aa_pct",  "percent"),
        ]
        cells = [f'<td class="eerr-label">{html.escape(row["label"])}</td>']
        for field, vtype in fields:
            v = row[field]
            cells.append(f'<td class="{_cell_cls(v)}">{_fmt(v, vtype)}</td>')
        cells.append(_cumpl_bar(row["real"], row["presupuesto"]))

        rows_html.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    return (
        '<div class="eerr-table-scroll">'
        '<table class="eerr-table">'
        f"<thead><tr>{header_row}</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table>"
        "</div>"
    )


def _build_excel(rows: pd.DataFrame, title: str) -> bytes:
    """Build Excel bytes from statement rows."""
    cols = [
        "label", "presupuesto", "pct_presupuesto", "real", "pct_real",
        "var_real_ppto", "var_real_ppto_pct", "real_aa", "var_real_aa", "var_real_aa_pct",
    ]
    rename = {
        "label": "Cuenta", "presupuesto": "PPTO",
        "pct_presupuesto": "% PPTO/Ventas", "real": "Real",
        "pct_real": "% Real/Ventas", "var_real_ppto": "Var. Real/PPTO",
        "var_real_ppto_pct": "Var. % Real/PPTO", "real_aa": "Real Año Ant.",
        "var_real_aa": "Var. Real/Año Ant.", "var_real_aa_pct": "Var. % Real/Año Ant.",
    }
    export_df = (
        rows[rows["row_type"] != "blank"][cols]
        .rename(columns=rename)
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="EE.RR")
    return buf.getvalue()


# ── main render ───────────────────────────────────────────────────────────────

def render(bundle: dict) -> None:
    df_contable = bundle["contable"]
    reference_contable = bundle.get("reference_contable", df_contable)
    filters = bundle.get("meta", {}).get("active_filters", {})

    render_header(
        "Estado de Resultados",
        "EE.RR consolidado — Real vs Presupuesto, variación absoluta y porcentual.",
    )

    statement = build_eerr_statement(df_contable, reference_contable, filters)
    rows = statement["rows"]
    if rows.empty:
        st.info("No hay datos para construir el EE.RR con la selección actual.")
        return

    # ── Period label from data ────────────────────────────────────────────────
    period_label = statement.get("period_label", "")
    if not period_label and "mes" in df_contable.columns and "año" in df_contable.columns:
        try:
            from Modulo_financiero.logic import SHORT_MONTH_NAMES
            max_row = df_contable.sort_values(["año", "mes"]).iloc[-1]
            period_label = f"{SHORT_MONTH_NAMES.get(int(max_row['mes']), '')}-{int(max_row['año'])}"
        except Exception:
            period_label = ""

    # ── Context pills ─────────────────────────────────────────────────────────
    pills: list[tuple[str, str]] = []
    if period_label:
        pills.append((f"Corte: {period_label}", "primary"))
    pills += [
        ("Moneda: CLP millones", "soft"),
        ("Vista: Acumulado YTD", "ghost"),
    ]
    render_pills(pills)

    # ── Export menu ───────────────────────────────────────────────────────────
    _, export_col = st.columns([5, 1])
    with export_col:
        with st.popover("⬇ Descargar EE.RR", use_container_width=True):
            st.caption("EXPORTAR ESTADO DE RESULTADOS")
            try:
                excel_bytes = _build_excel(rows, statement["title"])
                st.download_button(
                    label="📗 Excel (.xlsx)",
                    data=excel_bytes,
                    file_name="eerr_interwins.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Tabla editable con todas las columnas",
                )
            except Exception:
                st.info("Instala openpyxl para exportar a Excel.")
            st.button("📕 PDF", disabled=True, use_container_width=True, help="Próximamente")

    # ── Table ─────────────────────────────────────────────────────────────────
    report_html = (
        '<div class="eerr-report-shell">'
        f'<div class="eerr-title">{html.escape(statement["title"])}</div>'
        f'<div class="eerr-subtitle">{html.escape(statement["subtitle"])}</div>'
        f"{_build_eerr_html(rows)}"
        "</div>"
    )
    st.markdown(report_html, unsafe_allow_html=True)
