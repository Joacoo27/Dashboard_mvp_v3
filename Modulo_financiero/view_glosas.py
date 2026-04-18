import streamlit as st

from .logic import format_currency, build_glosas_summary, _apply_non_date_filters
from .ui_helpers import render_header, render_metric_card


def render(bundle: dict[str, object]) -> None:
    df_glosas = bundle["glosas"]
    df_contable = bundle["contable"]
    filters = bundle.get("meta", {}).get("active_filters", {})

    # Simular la union (relación) de Tableau: 
    # Filtramos el maestro contable según las selecciones globales y cruzamos con glosas
    if filters and not df_contable.empty and not df_glosas.empty:
        filtered_contable = _apply_non_date_filters(df_contable, filters)
        if filtered_contable.empty:
            df_glosas = df_glosas.iloc[0:0] # Sin coincidencias
        else:
            # Seleccionamos las llaves de cruce exactas definidas en Tableau
            join_keys = ['anio', 'mes', 'cuenta_contable', 'centro_costo']
            valid_combos = filtered_contable[join_keys].drop_duplicates()
            # Forzamos tipo string para cruce seguro de cuentas y centros
            for col in ['cuenta_contable', 'centro_costo']:
                valid_combos[col] = valid_combos[col].astype(str)
                df_glosas[col] = df_glosas[col].astype(str)
            
            df_glosas = df_glosas.merge(valid_combos, on=join_keys, how='inner')

    render_header(
        "Glosas",
        "Detalle contable para trazabilidad: glosa, comprobante, usuario y movimientos asociados.",
    )

    search_term = st.text_input("Buscar por glosa, comprobante, usuario o cuenta", value="").strip()
    if search_term:
        search_upper = search_term.upper()
        filtered = df_glosas[
            df_glosas["glosa"].fillna("").str.upper().str.contains(search_upper)
            | df_glosas["usuario"].fillna("").str.upper().str.contains(search_upper)
            | df_glosas["numero_comprobante"].fillna("").str.upper().str.contains(search_upper)
            | df_glosas["cuenta_contable"].fillna("").astype(str).str.upper().str.contains(search_upper)
        ]
    else:
        filtered = df_glosas

    summary = build_glosas_summary(filtered)

    from .ui_helpers import render_info_capsule

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Registros", f"{summary['total_registros']:,}", "Movimientos visibles", explanation="Cantidad total de líneas contables encontradas bajo el filtro actual.")
    with k2:
        render_metric_card("Debe", format_currency(summary["movimiento_debe"]), "Suma del detalle", explanation="Sumatoria de todos los débitos registrados en el período seleccionado.")
    with k3:
        render_metric_card("Haber", format_currency(summary["movimiento_haber"]), "Suma del detalle", explanation="Sumatoria de todos los créditos registrados en el período seleccionado.")

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.5, 1])
    with left_col:
        render_info_capsule(
            "Detalle de Glosas",
            "Muestra el registro contable línea a línea para auditoría y trazabilidad.",
            "Visualización de fecha, centro de costo, usuario, comprobante y montos."
        )
        if filtered.empty:
            st.info("No hay glosas para la selección actual.")
        else:
            detail = filtered.copy()
            detail["fecha_conta"] = pd.to_datetime(detail["fecha_conta"], errors="coerce").dt.strftime("%Y-%m-%d")
            detail["movdebe"] = detail["movdebe"].map(format_currency)
            detail["movhaber"] = detail["movhaber"].map(format_currency)
            detail["saldo"] = detail["saldo"].map(format_currency)
            st.dataframe(
                detail[
                    [
                        "fecha_conta",
                        "centro_costo",
                        "cuenta_contable",
                        "usuario",
                        "numero_comprobante",
                        "glosa",
                        "movdebe",
                        "movhaber",
                        "saldo",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

    with right_col:
        st.markdown('<div class="chart-section-title">Usuarios con más movimiento</div>', unsafe_allow_html=True)
        st.dataframe(summary["top_usuarios"], width="stretch", hide_index=True)
