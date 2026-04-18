# Vista EERR principal

Este documento define unicamente la vista `EERR principal` del nuevo panel.

La estructura debe seguir la referencia visual del archivo:

- `Referencia EERRR.png`

No se deben agregar modulos, tabs ni componentes distintos al EERR principal mostrado en la referencia.

## Objetivo de la vista

Replicar la lectura principal del estado de resultados, con comparacion entre presupuesto, real y ano anterior.

## Estructura exacta esperada

### 1. Encabezado

- Titulo superior:
  - Formato esperado: `EERR - ABRIL/2026`
- Subencabezado central:
  - `ACUMULADO`

### 2. Tabla principal

La vista debe ser una sola tabla matriz, con esta estructura de columnas:

1. Concepto o fila contable
2. `PPTO`
3. `% PPTO SOBRE VENTAS`
4. `REAL`
5. `% REAL SOBRE VENTAS`
6. `VAR REAL/PPTO`
7. `VAR % REAL/PPTO`
8. `REAL ANO ANT`
9. `VAR REAL/ANO ANT`
10. `VAR REAL/ANO ANT %`

## Orden exacto de filas

La estructura funcional del EERR debe respetar este orden:

1. `INGRESOS`
2. `COSTOS OPERACIONALES`
3. `COSTO DE REMUNERACIONES`
4. `MARGEN BRUTO`
5. `INGRESO INTERNO`
6. `COSTO INTERNO`
7. `MARGEN BRUTO INTERNO`
8. `GASTOS DE VENTAS`
9. `GASTOS OPERACIONALES`
10. `GASTOS DE REMUNERACIONES`
11. `GASTOS ADM Y VENTAS`
12. `MARGEN OPERACIONAL`
13. `DEPRECIACIONES`
14. `GASTOS FINANCIEROS`
15. `INGRESOS NO OPERACIONAL`
16. `OTROS RESULTADOS NO OPERACIONALES`
17. `GASTOS NO OPERACIONALES`
18. `NO OPERACIONAL`
19. `MARGEN ANTES PROVISION COMERCIAL`
20. `PROVISION MARGEN COMERCIAL`
21. `MARGEN NETO RAI`
22. `IMPUESTO A LAS GANANCIAS`
23. `MARGEN NETO`

## Jerarquia visual esperada

Las filas de subtotal o resultado deben destacarse visualmente, tal como en la referencia.

Filas de especial relevancia:

- `MARGEN BRUTO`
- `MARGEN BRUTO INTERNO`
- `MARGEN OPERACIONAL`
- `NO OPERACIONAL`
- `MARGEN ANTES PROVISION COMERCIAL`
- `MARGEN NETO RAI`
- `MARGEN NETO`

## Reglas de presentacion

- Los ingresos deben verse como base de referencia para porcentajes sobre ventas
- Los costos y gastos deben mantenerse con signo negativo cuando corresponda
- Las variaciones deben poder verse positivas o negativas segun resultado real contra referencia
- El formato de la tabla debe priorizar lectura ejecutiva y comparacion directa entre columnas
- No agregar graficos dentro de esta vista
- No agregar tarjetas KPI dentro de esta vista
- No agregar detalle transaccional ni drilldown adicional en esta primera documentacion

## Alcance funcional

Esta vista solo debe cubrir:

- Presupuesto acumulado
- Real acumulado
- Porcentaje sobre ventas
- Variacion contra presupuesto
- Variacion contra ano anterior

No incluir en esta vista:

- Evolutivos mensuales
- Analisis de liquidez
- Ratios de balance
- RRHH
- Proyectos
- SAM
- Trimestral
- Vistas descargables

## Dependencia con la logica

La definicion de formulas, columnas, variaciones y criterios de calculo de esta vista queda documentada en:

- `LOGICA_KPIS_CALCULOS_INDICADORES.md`
