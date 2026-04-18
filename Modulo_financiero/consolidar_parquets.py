import pandas as pd
import sys
import os

# Ajuste temporal del PATH para permitir ejecución directa como script en terminal o como módulo
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from Modulo_financiero.data import get_sqlalchemy_engine, CONTABLE_PARQUET, GLOSAS_PARQUET, PROJECT_DIR
except ImportError:
    from .data import get_sqlalchemy_engine, CONTABLE_PARQUET, GLOSAS_PARQUET, PROJECT_DIR

def actualizar_todo():
    """Consolida los datos financieros desde la base de datos."""
    print("🚀 Iniciando Consolidación Financiera...")
    engine = get_sqlalchemy_engine()
    if not engine:
        print("❌ Error: No se pudo conectar a la Base de Datos Financiera.")
        return

    try:
        # 1. Contable
        print("📥 Procesando Datos Contables...")
        QUERY_CONTABLE = """
-- CONSTRUCCION M CONTABLE
WITH parametros AS (
    SELECT
        date_trunc('month', current_date)::date AS mes_actual,
        (date_trunc('month', current_date) - INTERVAL '23 months')::date AS fecha_inicio
),
presupuesto_base AS (
    SELECT
        fp.anio::int AS anio,
        meses.mes,
        fp.cuenta_contable,
        fp.centro_costo,
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
    -- Se agrupa antes del join final para evitar duplicar PPTO si la fuente trae mas de una fila por llave.
    SELECT
        anio,
        mes,
        cuenta_contable,
        centro_costo,
        SUM(ppto) AS ppto
    FROM presupuesto_base
    GROUP BY anio, mes, cuenta_contable, centro_costo
),
maestro_cc AS (
    SELECT
        anio,
        centro_costo
    FROM (
        SELECT
            EXTRACT(YEAR FROM fmc.fecha_conta::date)::int AS anio,
            fmc.centro_costo
        FROM fin_movimientos_contables fmc
        CROSS JOIN parametros p
        WHERE fmc.fecha_conta::date BETWEEN p.fecha_inicio AND p.mes_actual

        UNION

        SELECT DISTINCT
            anio::int AS anio,
            cod_nivel4 AS centro_costo
        FROM fin_maestro_centro_costo
        CROSS JOIN parametros p
        WHERE make_date(anio::int, 1, 1)
            BETWEEN date_trunc('year', p.fecha_inicio)::date AND date_trunc('year', p.mes_actual)::date
    ) cc
    GROUP BY anio, centro_costo
),
tabla_fecha AS (
    SELECT
        base.anio,
        base.mes,
        base.pccodi_4,
        cc.centro_costo,
        mcc.nivel4 AS centro_costo_desc,
        mcc.nivel3 AS nivel_3_cc,
        mcc.nivel2 AS nivel_2_cc,
        mcc.nombre_proyecto AS nombre_proyecto,
        mcc.rut_cliente,
        mcc.nombre_cliente
    FROM (
        SELECT
            EXTRACT(YEAR FROM calendario.f)::int AS anio,
            EXTRACT(MONTH FROM calendario.f)::int AS mes,
            cuentas.pccodi_4
        FROM parametros p
        CROSS JOIN generate_series(
            p.fecha_inicio::timestamp,
            p.mes_actual::timestamp,
            INTERVAL '1 month'
        ) AS calendario(f)
        CROSS JOIN (
            SELECT DISTINCT
                pccodi_4
            FROM fin_maestro_cuentas
        ) cuentas
    ) base
    LEFT JOIN maestro_cc cc
        ON base.anio = cc.anio
    LEFT JOIN fin_maestro_centro_costo mcc
        ON cc.anio = mcc.anio::int
        AND cc.centro_costo = mcc.cod_nivel4
),
base_contable AS (
    SELECT
        EXTRACT(YEAR FROM fmc.fecha_conta::date)::int AS anio,
        EXTRACT(MONTH FROM fmc.fecha_conta::date)::int AS mes,
        fmc.centro_costo,
        fmc.centro_costo_desc,
        fmc.cuenta_contable,
        SUM(fmc.movdebe) AS movdebe,
        SUM(fmc.movhaber) AS movhaber,
        SUM(fmc.saldo) AS saldo
    FROM fin_movimientos_contables fmc
    CROSS JOIN parametros p
    WHERE fmc.fecha_conta::date BETWEEN p.fecha_inicio AND p.mes_actual
    GROUP BY
        EXTRACT(YEAR FROM fmc.fecha_conta::date)::int,
        EXTRACT(MONTH FROM fmc.fecha_conta::date)::int,
        fmc.centro_costo,
        fmc.centro_costo_desc,
        fmc.cuenta_contable
),
maestro_contabilidad AS (
    SELECT
        tf.anio,
        tf.mes,
        tf.centro_costo,
        tf.centro_costo_desc,
        tf.nivel_3_cc,
        tf.nivel_2_cc,
        tf.nombre_proyecto,
        tf.rut_cliente,
        tf.nombre_cliente,
        ifrs.cuenta AS cuenta_ifrs,
        ifrs."NIVEL 1 IFRS" AS nivel_1_ifrs,
        ifrs."NIVEL 2 IFRS" AS nivel_2_ifrs,
        ifrs."NIVEL 3 IFRS" AS nivel_3_ifrs,
        ifrs."TIPO EEFF" AS estado_financiero,
        ifrs."NIVEL RATIO" AS nivel_ratio,
        tf.pccodi_4 AS cuenta_contable,
        mc.pccodi_4,
        mc.pcdesc_4,
        mc.pccodi_3,
        mc.pcdesc_3,
        mc.pccodi_2,
        mc.pcdesc_2,
        mc.pccodi_1,
        mc.pcdesc_1,
        bc.movdebe,
        bc.movhaber,
        bc.saldo
    FROM tabla_fecha tf
    LEFT JOIN base_contable bc
        ON tf.anio = bc.anio
        AND tf.mes = bc.mes
        AND tf.pccodi_4 = bc.cuenta_contable
        AND tf.centro_costo = bc.centro_costo
    LEFT JOIN fin_maestro_cuentas mc
        ON tf.pccodi_4 = mc.pccodi_4
    LEFT JOIN LATERAL (
        -- Toma el ultimo anio IFRS <= al periodo; si no existe, usa el mas cercano posterior.
        SELECT
            t4.cuenta,
            t4."NIVEL 1 IFRS",
            t4."NIVEL 2 IFRS",
            t4."NIVEL 3 IFRS",
            t4."TIPO EEFF",
            t4."NIVEL RATIO"
        FROM fin_maestro_contabilidad_anual_ifrs t4
        WHERE t4."N° CUENTA" = tf.pccodi_4
        ORDER BY
            CASE WHEN t4."aÑo"::int <= tf.anio THEN 0 ELSE 1 END,
            CASE
                WHEN t4."aÑo"::int <= tf.anio THEN tf.anio - t4."aÑo"::int
                ELSE t4."aÑo"::int - tf.anio
            END
        LIMIT 1
    ) ifrs ON TRUE
),
maestro_contabilidad_agrupado AS (
    SELECT
        mc.anio,
        mc.mes,
        mc.centro_costo,
        mc.centro_costo_desc,
        mc.nivel_3_cc,
        mc.nivel_2_cc,
        mc.nombre_proyecto,
        mc.rut_cliente,
        mc.nombre_cliente,
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
        mc.movdebe AS debe,
        mc.movhaber AS haber,
        mc.saldo,
        p.ppto
    FROM maestro_contabilidad mc
    LEFT JOIN presupuesto p
        ON mc.anio = p.anio
        AND mc.mes = p.mes
        AND mc.centro_costo = p.centro_costo
        AND mc.cuenta_contable = p.cuenta_contable
)
SELECT
    anio,
    mes,
    centro_costo,
    centro_costo_desc,
    nivel_3_cc AS "Nivel_3_CC",
    nivel_2_cc AS "Nivel_2_CC",
    nombre_proyecto AS "Nombre_Proyecto",
    rut_cliente,
    nombre_cliente,
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
    END AS "pcdesc_1_Modificado", -- Categoria creada para agrupar ventas/costos internos.
    pcdesc_1,
    debe,
    haber,
    saldo,
    ppto AS "PPTO"
FROM maestro_contabilidad_agrupado
        """
        df_contable = pd.read_sql(QUERY_CONTABLE.replace('%', '%%'), engine)
        df_contable.to_parquet(CONTABLE_PARQUET)
        print(f"   ✅ Contable: {len(df_contable)} filas guardadas.")

        # 2. Glosas
        print("📥 Procesando Glosas...")
        QUERY_GLOSAS = """
        WITH Agrupacion_Contabilidad AS (
            SELECT 
                EXTRACT(year FROM fecha_conta::date)::int AS anio,
                EXTRACT(month FROM fecha_conta::date)::int AS mes,
                fecha_conta::date,
                centro_costo,
                centro_costo_desc,
                cuenta_contable,
                usuario,
                numero_comprobante,
                glosa,
                movdebe,
                movhaber,
                saldo
            FROM fin_movimientos_contables
            WHERE fecha_conta::date >= date_trunc('year', current_date - interval '2 year')::date
        )
        SELECT 
            anio,
            mes,
            fecha_conta,
            centro_costo,
            centro_costo_desc,
            cuenta_contable,
            usuario,
            numero_comprobante,
            glosa,
            SUM(movdebe) AS movdebe,
            SUM(movhaber) AS movhaber,
            SUM(saldo) AS saldo 
        FROM Agrupacion_Contabilidad
        GROUP BY anio, mes, fecha_conta, centro_costo, centro_costo_desc, cuenta_contable, glosa, numero_comprobante, usuario
        """
        df_glosas = pd.read_sql(QUERY_GLOSAS.replace('%', '%%'), engine)
        df_glosas.to_parquet(GLOSAS_PARQUET)
        print(f"   ✅ Glosas: {len(df_glosas)} filas guardadas.")

    except Exception as e:
        print(f"❌ Error durante la consolidación: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    actualizar_todo()
