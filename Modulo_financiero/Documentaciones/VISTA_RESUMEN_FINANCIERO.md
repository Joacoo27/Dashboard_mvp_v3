# Vista resumen financiero

Este documento define unicamente la vista `Resumen Financiero` del nuevo panel.

La construccion de esta vista debe seguir la referencia visual enviada en:

- `Referencia resumen financiero parte 1.png`
- `Referencia resumen financiero parte 2.png`

No se deben agregar bloques extra, modulos adicionales ni vistas complementarias fuera de lo que aparece en esa referencia.

## Objetivo de la vista

Mostrar una lectura ejecutiva del mes actual, con foco en:

- KPIs principales del negocio
- Comparaciones resumidas contra presupuesto o ano anterior
- Dos evolutivos principales

## Estructura exacta esperada

La vista debe quedar estructurada en este orden:

### 1. Encabezado principal

- Titulo: `Resumen Ejecutivo`
- Subtitulo: `Tarjetas del mes actual y evolutivos principales del reporte financiero.`
- Badge o pastilla de corte:
  - Formato esperado: `Corte actual: ABRIL/2026`

### 2. Grilla de tarjetas KPI

La grilla debe tener `8 tarjetas` distribuidas en `2 filas x 4 columnas`.

#### Fila 1

1. `CRECIMIENTO DE INGRESOS`
2. `EBITDA`
3. `MARGEN BRUTO`
4. `MARGEN OPERACIONAL`

#### Fila 2

1. `CAJA / LIQUIDEZ`
2. `ROA`
3. `ROE`
4. `RESULTADO DEL EJERCICIO`

## Contenido exacto de cada tarjeta

### 1. Crecimiento de ingresos

- Titulo: `CRECIMIENTO DE INGRESOS`
- Valor principal: porcentaje grande
- Indicador secundario: variacion breve contra presupuesto
- Texto de apoyo: `Mes actual vs mismo mes ano anterior`

### 2. EBITDA

- Titulo: `EBITDA`
- Valor principal: monto grande abreviado en millones
- Indicador secundario: variacion breve vs presupuesto
- Texto de apoyo: `Mes actual`

### 3. Margen bruto

- Titulo: `MARGEN BRUTO`
- Valor principal: porcentaje grande
- Indicador secundario: variacion en puntos porcentuales vs ano anterior
- Texto de apoyo: `Mes actual sobre ventas`

### 4. Margen operacional

- Titulo: `MARGEN OPERACIONAL`
- Valor principal: porcentaje grande
- Indicador secundario: variacion en puntos porcentuales vs ano anterior
- Texto de apoyo: `Mes actual sobre ventas`

### 5. Caja / liquidez

- Titulo: `CAJA / LIQUIDEZ`
- Valor principal: ratio en `x`
- Texto secundario inferior: `Caja al cierre: $...`

### 6. ROA

- Titulo: `ROA`
- Valor principal: porcentaje grande
- Indicador secundario: variacion en puntos porcentuales vs ano anterior
- Texto de apoyo: `Resultado TTM / activos`

### 7. ROE

- Titulo: `ROE`
- Valor principal: porcentaje grande
- Indicador secundario: variacion en puntos porcentuales vs ano anterior
- Texto de apoyo: `Resultado TTM / patrimonio`

### 8. Resultado del ejercicio

- Titulo: `RESULTADO DEL EJERCICIO`
- Valor principal: monto grande abreviado en millones
- Indicador secundario: variacion breve vs presupuesto
- Texto de apoyo: `Mes actual`

## Evolutivos obligatorios

Debajo de las tarjetas deben existir solamente `2 graficos`.

### 1. Evolutivo de ingresos

- Titulo: `Evolutivo de Ingresos`
- Tipo: grafico combinado
- Serie 1: barras azules para `Ingreso Real`
- Serie 2: linea roja segmentada para `Ingreso Presupuesto`
- Eje X: meses moviles
- Objetivo: comparar ejecucion real contra presupuesto en la serie temporal

### 2. Evolutivo de margen bruto

- Titulo: `Evolutivo de Margen Bruto`
- Tipo: grafico combinado
- Serie 1: barras verdes para `Margen Bruto`
- Serie 2: linea azul oscura para `% Margen Bruto`
- Eje X: meses moviles
- Objetivo: mostrar simultaneamente monto y margen porcentual

## Reglas de construccion visual

- La estructura debe respetar el orden exacto de los bloques de la referencia
- La vista debe abrir mostrando primero las tarjetas y luego los dos evolutivos
- No incluir tablas, tabs, acordeones ni modulos extra
- No incluir indicadores de liquidez, solvencia o ratios adicionales fuera de las 8 tarjetas definidas
- No agregar un tercer grafico ni secciones secundarias

## Filtro funcional minimo

La vista debe operar con un `corte actual` visible, equivalente al periodo que se esta mostrando en las tarjetas.

## Dependencia con la logica

La definicion de formulas, KPIs, comparaciones y criterios de calculo de esta vista queda documentada en:

- `LOGICA_KPIS_CALCULOS_INDICADORES.md`
