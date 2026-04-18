import pandas as pd
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from Modulo_financiero.data import get_sqlalchemy_engine, CONTABLE_PARQUET, PROJECT_DIR
except ImportError:
    from .data import get_sqlalchemy_engine, CONTABLE_PARQUET, PROJECT_DIR

QUERY_CONSOLIDADO = """
-- M CONTABLE CONSOLIDADO
-- Grano final: anio + mes + cuenta_contable
-- Alcance: ultimos 24 meses moviles incluyendo el mes actual
WITH parametros AS (
    SELECT
        date_trunc('month', current_date)::date AS mes_actual,
        (date_trunc('month', current_date) - INTERVAL '23 months')::date AS fecha_inicio,
        current_date::date AS fecha_fin
),
movimientos_filtrados AS (
    SELECT
        fmc.fecha_conta::date AS fecha_conta,
        EXTRACT(YEAR FROM fmc.fecha_conta::date)::int AS anio,
        EXTRACT(MONTH FROM fmc.fecha_conta::date)::int AS mes,
        fmc.cuenta_contable,
        fmc.usuario,
        fmc.numero_comprobante,
        NULLIF(BTRIM(fmc.glosa), '') AS glosa,
        fmc.movdebe,
        fmc.movhaber,
        fmc.saldo
    FROM fin_movimientos_contables fmc
    CROSS JOIN parametros p
    WHERE fmc.fecha_conta::date BETWEEN p.fecha_inicio AND p.fecha_fin
),
presupuesto_base AS (
    SELECT
        fp.anio::int AS anio,
        meses.mes,
        fp.cuenta_contable,
        meses.ppto
    FROM fin_presupuestos fp
    CROSS JOIN LATERAL (
        VALUES
            (1, fp.ene),
            (2, fp.feb),
            (3, fp.mar),
            (4, fp.abr),
            (5, fp.may),
            (6, fp.jun),
            (7, fp.jul),
            (8, fp.ago),
            (9, fp.sep),
            (10, fp.oct),
            (11, fp.nov),
            (12, fp.dic)
    ) AS meses(mes, ppto)
    CROSS JOIN parametros p
    WHERE make_date(fp.anio::int, meses.mes, 1) BETWEEN p.fecha_inicio AND p.mes_actual
),
presupuesto AS (
    SELECT
        anio,
        mes,
        cuenta_contable,
        SUM(ppto) AS ppto
    FROM presupuesto_base
    GROUP BY anio, mes, cuenta_contable
),
base_contable AS (
    SELECT
        mf.anio,
        mf.mes,
        mf.cuenta_contable,
        SUM(mf.movdebe) AS debe,
        SUM(mf.movhaber) AS haber,
        SUM(mf.saldo) AS saldo
    FROM movimientos_filtrados mf
    GROUP BY mf.anio, mf.mes, mf.cuenta_contable
),
glosas_metricas AS (
    SELECT
        mf.anio,
        mf.mes,
        mf.cuenta_contable,
        MIN(mf.fecha_conta) AS primera_fecha_conta,
        MAX(mf.fecha_conta) AS ultima_fecha_conta,
        COUNT(*) AS cantidad_registros_contables,
        COUNT(DISTINCT mf.numero_comprobante) AS cantidad_comprobantes
    FROM movimientos_filtrados mf
    GROUP BY mf.anio, mf.mes, mf.cuenta_contable
),
glosas_resumen AS (
    SELECT
        base.anio,
        base.mes,
        base.cuenta_contable,
        COUNT(*) AS cantidad_glosas,
        STRING_AGG(base.glosa, ' | ' ORDER BY base.glosa) AS glosas_consolidadas
    FROM (
        SELECT DISTINCT
            mf.anio,
            mf.mes,
            mf.cuenta_contable,
            mf.glosa
        FROM movimientos_filtrados mf
        WHERE mf.glosa IS NOT NULL
    ) base
    GROUP BY base.anio, base.mes, base.cuenta_contable
),
usuarios_resumen AS (
    SELECT
        base.anio,
        base.mes,
        base.cuenta_contable,
        COUNT(*) AS cantidad_usuarios,
        STRING_AGG(base.usuario, ' | ' ORDER BY base.usuario) AS usuarios_contables
    FROM (
        SELECT DISTINCT
            mf.anio,
            mf.mes,
            mf.cuenta_contable,
            mf.usuario
        FROM movimientos_filtrados mf
        WHERE NULLIF(BTRIM(mf.usuario), '') IS NOT NULL
    ) base
    GROUP BY base.anio, base.mes, base.cuenta_contable
),
universo AS (
    SELECT bc.anio, bc.mes, bc.cuenta_contable FROM base_contable bc
    UNION
    SELECT p.anio, p.mes, p.cuenta_contable FROM presupuesto p
),
maestro_contabilidad AS (
    SELECT
        u.anio,
        u.mes,
        u.cuenta_contable,
        mc.pccodi_4,
        mc.pcdesc_4,
        mc.pccodi_3,
        mc.pcdesc_3,
        mc.pccodi_2,
        mc.pcdesc_2,
        mc.pccodi_1,
        mc.pcdesc_1,
        ifrs.cuenta AS cuenta_ifrs,
        ifrs."NIVEL 1 IFRS" AS nivel_1_ifrs,
        ifrs."NIVEL 2 IFRS" AS nivel_2_ifrs,
        ifrs."NIVEL 3 IFRS" AS nivel_3_ifrs,
        ifrs."TIPO EEFF" AS estado_financiero,
        ifrs."NIVEL RATIO" AS nivel_ratio
    FROM universo u
    LEFT JOIN fin_maestro_cuentas mc
        ON u.cuenta_contable = mc.pccodi_4
    LEFT JOIN LATERAL (
        SELECT
            t4.cuenta,
            t4."NIVEL 1 IFRS",
            t4."NIVEL 2 IFRS",
            t4."NIVEL 3 IFRS",
            t4."TIPO EEFF",
            t4."NIVEL RATIO"
        FROM fin_maestro_contabilidad_anual_ifrs t4
        WHERE t4."N° CUENTA" = u.cuenta_contable
        ORDER BY
            CASE WHEN t4."aÑo"::int <= u.anio THEN 0 ELSE 1 END,
            CASE
                WHEN t4."aÑo"::int <= u.anio THEN u.anio - t4."aÑo"::int
                ELSE t4."aÑo"::int - u.anio
            END
        LIMIT 1
    ) ifrs ON TRUE
),
salida AS (
    SELECT
        mc.anio,
        mc.mes,
        mc.cuenta_ifrs,
        mc.nivel_1_ifrs,
        mc.nivel_2_ifrs,
        mc.nivel_3_ifrs,
        CASE
            WHEN mc.nivel_1_ifrs = 'RESULTADO ANTES DE IMPUESTOS' THEN 'RESULTADO ANTES DE IMPUESTOS'
            ELSE mc.nivel_3_ifrs
        END AS nivel_3_ifrs_modificado,
        mc.estado_financiero,
        mc.nivel_ratio,
        mc.cuenta_contable,
        mc.pccodi_4,
        mc.pcdesc_4,
        mc.pccodi_3,
        CASE
            WHEN mc.pcdesc_4 = 'VENTAS INTERNAS' THEN 'VENTAS INTERNAS'
            WHEN mc.pcdesc_4 = 'COSTOS INTERNOS' THEN 'COSTOS INTERNOS'
            ELSE mc.pcdesc_3
        END AS pcdesc_3_modificado,
        mc.pcdesc_3,
        mc.pccodi_2,
        mc.pcdesc_2,
        mc.pccodi_1,
        mc.pcdesc_1,
        bc.debe,
        bc.haber,
        bc.saldo,
        p.ppto,
        gm.primera_fecha_conta,
        gm.ultima_fecha_conta,
        gm.cantidad_registros_contables,
        gm.cantidad_comprobantes,
        gr.cantidad_glosas,
        gr.glosas_consolidadas,
        ur.cantidad_usuarios,
        ur.usuarios_contables
    FROM maestro_contabilidad mc
    LEFT JOIN base_contable bc
        ON mc.anio = bc.anio AND mc.mes = bc.mes AND mc.cuenta_contable = bc.cuenta_contable
    LEFT JOIN presupuesto p
        ON mc.anio = p.anio AND mc.mes = p.mes AND mc.cuenta_contable = p.cuenta_contable
    LEFT JOIN glosas_metricas gm
        ON mc.anio = gm.anio AND mc.mes = gm.mes AND mc.cuenta_contable = gm.cuenta_contable
    LEFT JOIN glosas_resumen gr
        ON mc.anio = gr.anio AND mc.mes = gr.mes AND mc.cuenta_contable = gr.cuenta_contable
    LEFT JOIN usuarios_resumen ur
        ON mc.anio = ur.anio AND mc.mes = ur.mes AND mc.cuenta_contable = ur.cuenta_contable
)
SELECT
    anio,
    mes,
    cuenta_ifrs AS "Cuenta_IFRS",
    nivel_1_ifrs AS "Nivel_1_IFRS",
    nivel_2_ifrs AS "Nivel_2_IFRS",
    nivel_3_ifrs_modificado AS "Nivel_3_IFRS",
    nivel_3_ifrs AS "Nivel_3_IFRS_Original",
    estado_financiero AS "Estado_Financiero",
    nivel_ratio AS "Nivel_Ratio",
    cuenta_contable,
    pccodi_4,
    pcdesc_4,
    pccodi_3,
    pcdesc_3_modificado AS "pcdesc_3_Modificado",
    pcdesc_3,
    pccodi_2,
    pcdesc_2,
    pccodi_1,
    CASE
        WHEN pcdesc_3_modificado = 'VENTAS INTERNAS' THEN 'INTERNO'
        WHEN pcdesc_3_modificado = 'COSTOS INTERNOS' THEN 'INTERNO'
        ELSE pcdesc_1
    END AS "pcdesc_1_Modificado",
    pcdesc_1,
    debe,
    haber,
    saldo,
    ppto AS "PPTO",
    primera_fecha_conta AS "Primera_Fecha_Conta",
    ultima_fecha_conta AS "Ultima_Fecha_Conta",
    cantidad_registros_contables AS "Cantidad_Registros_Contables",
    cantidad_comprobantes AS "Cantidad_Comprobantes",
    cantidad_glosas AS "Cantidad_Glosas",
    glosas_consolidadas AS "Glosas_Consolidadas",
    cantidad_usuarios AS "Cantidad_Usuarios",
    usuarios_contables AS "Usuarios_Contables"
FROM salida
"""


def actualizar_todo():
    """Consolida los datos financieros desde la base de datos. Lanza excepción si falla."""
    engine = get_sqlalchemy_engine()
    if not engine:
        raise ConnectionError(
            "No se pudo crear el engine de BD. Verifica las variables de entorno "
            "(HOST_DATABASE, NAME_DATABASE, USER_DATABASE, PASW_DATABASE)."
        )

    try:
        df = pd.read_sql(QUERY_CONSOLIDADO.replace('%', '%%'), engine)
        df.to_parquet(CONTABLE_PARQUET)
        return len(df)
    finally:
        engine.dispose()


if __name__ == "__main__":
    actualizar_todo()
