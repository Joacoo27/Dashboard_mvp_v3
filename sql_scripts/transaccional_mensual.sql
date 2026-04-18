WITH venta AS (
    SELECT
        v.codigo_periodo,
        v.fecha,
        v.fecha2,
        v.codigo_local,
        v.cliente,
        split_part(v.codigo_producto, '-C', 1) AS codigo_producto,
        v.tipodocumento,
        v.folio,
        v.ventauni,
        v.montodescuento,
        v.ventapeso,
        v.iva,
        v.costo_total,
        v.margen_despachos,
        v.margen_sobre_costos,
        v.margen_sobre_ventas,
        v.cantidad_despachada,
        v.precio_vta_sin_dscto,
        v.precio_vta_con_dscto,
        v.despachado_por,
        v.vendedor,
        v.codigo_vendedor,
        v.clasificacion,
        v.zona,
        v.clasificacion_1,
        v.clasificacion_2,
        v.giro,
        v.region,
        v.nom_cliente,
        v.tipo,
        v.tiering,
        v.descrp_corta,
        v.descripcion,
        v.familia,
        v.mes,
        v.q,
        v.proveedor,
        v.año,
        v.costo,
        v.cod_consolidado,
        v.max_fecha,
        v.centro_costo,
        v.desc_centro_costo,
        v.vendedor_original,
        v.dealer,
        v.costo_unitario,
        v.total_neto,
        v.precio,
        v.total,
        v.totaldescmov,
        v.subtipodocto,
        v.vendedor_2,
        v.origen_data_vta
    FROM venta AS v
    WHERE codigo_producto LIKE '%-C'

    UNION ALL

    SELECT
        v.codigo_periodo,
        v.fecha,
        v.fecha2,
        v.codigo_local,
        v.cliente,
        v.codigo_producto,
        v.tipodocumento,
        v.folio,
        v.ventauni,
        v.montodescuento,
        v.ventapeso,
        v.iva,
        v.costo_total,
        v.margen_despachos,
        v.margen_sobre_costos,
        v.margen_sobre_ventas,
        v.cantidad_despachada,
        v.precio_vta_sin_dscto,
        v.precio_vta_con_dscto,
        v.despachado_por,
        v.vendedor,
        v.codigo_vendedor,
        v.clasificacion,
        v.zona,
        v.clasificacion_1,
        v.clasificacion_2,
        v.giro,
        v.region,
        v.nom_cliente,
        v.tipo,
        v.tiering,
        v.descrp_corta,
        v.descripcion,
        v.familia,
        v.mes,
        v.q,
        v.proveedor,
        v.año,
        v.costo,
        v.cod_consolidado,
        v.max_fecha,
        v.centro_costo,
        v.desc_centro_costo,
        v.vendedor_original,
        v.dealer,
        v.costo_unitario,
        v.total_neto,
        v.precio,
        v.total,
        v.totaldescmov,
        v.subtipodocto,
        v.vendedor_2,
        v.origen_data_vta
    FROM venta AS v
    WHERE codigo_producto NOT LIKE '%-C'
),

tabla_0 AS (
    SELECT
        v.codigo_periodo,
        v.fecha,
        v.fecha2,
        v.codigo_local,
        v.cliente,
        v.codigo_producto,
        v.tipodocumento,
        v.folio,
        v.ventauni,
        v.montodescuento,
        v.ventapeso,
        v.iva,
        v.costo_total,
        v.margen_despachos,
        v.margen_sobre_costos,
        v.margen_sobre_ventas,
        v.cantidad_despachada,
        v.precio_vta_sin_dscto,
        v.precio_vta_con_dscto,
        v.despachado_por,
        v.vendedor,
        v.codigo_vendedor,
        v.clasificacion,
        v.zona,
        v.clasificacion_1,
        v.clasificacion_2,
        v.giro,
        v.region,
        v.nom_cliente,
        v.tipo,
        v.tiering,
        v.descrp_corta,
        v.descripcion,
        v.familia,
        v.mes,
        v.q,
        v.proveedor,
        v.año,
        v.costo,
        v.cod_consolidado,
        v.max_fecha,
        v.desc_centro_costo,
        v.vendedor_original,
        v.dealer,
        v.costo_unitario,
        v.total_neto,
        v.precio,
        v.total,
        v.totaldescmov,
        v.subtipodocto,
        v.vendedor_2,
        v.origen_data_vta,
        CASE
            WHEN v.clasificacion_2 = 'RunRate'
                AND v.clasificacion_1 = 'Clientes Directos'
                AND v.centro_costo IN ('2-01-004','2-01-005')
                AND v.fecha::DATE < '2023-01-01' THEN '2-01-005'
            WHEN v.clasificacion_2 = 'RunRate'
                AND v.clasificacion_1 = 'Dealer'
                AND v.centro_costo IN ('2-01-001','2-01-002','2-01-003','2-01-004','2-01-005')
                AND v.fecha::DATE < '2023-01-01' THEN '2-01-010'
            ELSE v.centro_costo
        END AS centro_costo
    FROM venta AS v
),

tabla_1 AS (
    SELECT
        DATE_TRUNC('month', i.fecha)::DATE AS fecha,
        CASE
            WHEN p.codigo_antiguo IS NULL THEN i.codigo_producto
            ELSE p.codigo_nuevo
        END AS codigo,
        CASE
            WHEN i.clasificacion_2 = 'RunRate' AND i.clasificacion_1 = 'Dealer' THEN 'DEALER'
            WHEN i.clasificacion_2 = 'RunRate' AND i.clasificacion_1 = 'Proyectos' THEN 'PROYECTOS'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND (i.vendedor_2 IS NULL OR i.vendedor_2 = 'Otros Directa') THEN 'No se sabe el Cliente'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'ARAUCO' THEN 'ARAUCO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 IN ('Mantenimiento.Com', 'AMSA - Mantenimiento.Com') THEN 'AMSA'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 IN ('ANGLO - Resolutions', 'ANGLO - Critical.Com') THEN 'ANGLO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'CODELCO -  Resolutions' THEN 'CODELCO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'Walmart' THEN 'WALMART'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'GERDAU AZA' THEN 'GERDAU AZA'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'Carabineros' THEN 'CARABINEROS'
            ELSE UPPER(i.clasificacion_2)
        END AS canal_venta,
        SUM(i.ventauni) AS cantidad,
        SUM(i.ventapeso) AS venta,
        SUM(i.costo_total) AS costo,
        AVG(i.costo_unitario) AS costo_promedio
    FROM tabla_0 AS i
    LEFT JOIN io_codigos_homologos AS p
        ON i.codigo_producto = p.codigo_antiguo
    WHERE i.clasificacion_2 = 'RunRate'
        AND i.clasificacion_1 IN ('Dealer', 'Clientes Directos')
        AND i.centro_costo IN ('2-01-005','2-01-010')
    GROUP BY
        DATE_TRUNC('month', i.fecha)::DATE,
        CASE
            WHEN p.codigo_antiguo IS NULL THEN i.codigo_producto
            ELSE p.codigo_nuevo
        END,
        CASE
            WHEN i.clasificacion_2 = 'RunRate' AND i.clasificacion_1 = 'Dealer' THEN 'DEALER'
            WHEN i.clasificacion_2 = 'RunRate' AND i.clasificacion_1 = 'Proyectos' THEN 'PROYECTOS'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND (i.vendedor_2 IS NULL OR i.vendedor_2 = 'Otros Directa') THEN 'No se sabe el Cliente'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'ARAUCO' THEN 'ARAUCO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 IN ('Mantenimiento.Com', 'AMSA - Mantenimiento.Com') THEN 'AMSA'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 IN ('ANGLO - Resolutions', 'ANGLO - Critical.Com') THEN 'ANGLO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'CODELCO -  Resolutions' THEN 'CODELCO'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'Walmart' THEN 'WALMART'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'GERDAU AZA' THEN 'GERDAU AZA'
            WHEN i.clasificacion_2 = 'RunRate'
                AND i.clasificacion_1 = 'Clientes Directos'
                AND i.vendedor_2 = 'Carabineros' THEN 'CARABINEROS'
            ELSE UPPER(i.clasificacion_2)
        END
),

tabla_2 AS (
    SELECT
        fecha::DATE AS fecha,
        codigo || ' - ' || canal_venta AS codigo_producto,
        cantidad AS cantidad,
        venta AS venta,
        0 AS costo,
        0 AS margen
    FROM tabla_1
)

SELECT
    fecha,
    codigo_producto,
    cantidad,
    venta,
    costo,
    margen
FROM tabla_2
WHERE split_part(codigo_producto, ' - ', 2) IN ('DEALER', 'CODELCO', 'WALMART', 'ANGLO', 'AMSA')
    AND fecha >= '2020-01-01';
