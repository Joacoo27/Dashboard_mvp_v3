# Logica de KPIs, calculos e indicadores

Este archivo consolida la logica funcional para las dos unicas vistas priorizadas:

- `Vista resumen financiero`
- `Vista EERR principal`

## Criterio de lectura de esta documentacion

Se distingue entre dos niveles de validacion:

- `Confirmado en Tableau`: formula o estructura levantada directamente del workbook
- `Inferido desde referencia`: formula deducida por nombre del KPI, disposicion visual o consistencia del reporte

## Base comun de datos

### Real

`Confirmado en Tableau`

El valor real proviene del campo `saldo`, con conversion segun unidad seleccionada:

- Si unidad = `Millones de pesos`, usar `saldo / 1000000`
- Si unidad = `Miles de pesos`, usar `saldo / 1000`
- Si unidad = `Pesos`, usar `saldo`

### Presupuesto

`Confirmado en Tableau`

El valor presupuesto proviene del campo `ppto`, con conversion segun unidad seleccionada:

- Si unidad = `Millones de pesos`, usar `ppto / 1000000`
- Si unidad = `Miles de pesos`, usar `ppto / 1000`
- Si unidad = `Pesos`, usar `ppto`

### Logica de periodo visible

`Confirmado en Tableau`

El workbook usa un comportamiento en que, si el dia actual es menor a 15, toma el mes anterior como mes actual visible. En caso contrario usa el mes actual.

Esto afecta particularmente tarjetas y vistas resumidas.

## Logica de columnas del EERR principal

### PPTO

`Confirmado en Tableau`

Corresponde al presupuesto acumulado de la fila contable bajo el corte seleccionado.

### % PPTO SOBRE VENTAS

`Inferido desde referencia`

Formula esperada:

`PPTO fila / PPTO ingresos`

Debe expresarse como porcentaje.

### REAL

`Confirmado en Tableau`

Corresponde al real acumulado de la fila contable bajo el corte seleccionado.

### % REAL SOBRE VENTAS

`Confirmado en Tableau en la estructura general del modelo`

Formula esperada:

`REAL fila / REAL ingresos`

Debe expresarse como porcentaje.

### VAR REAL/PPTO

`Confirmado por consistencia numerica de la referencia`

Formula:

`REAL - PPTO`

### VAR % REAL/PPTO

`Confirmado por consistencia numerica de la referencia`

Formula:

`(REAL - PPTO) / PPTO`

### REAL ANO ANT

`Inferido desde referencia`

Corresponde al real del mismo periodo acumulado del ano anterior.

### VAR REAL/ANO ANT

`Confirmado por consistencia numerica de la referencia`

Formula:

`REAL - REAL ANO ANT`

### VAR REAL/ANO ANT %

`Confirmado por consistencia numerica de la referencia`

Formula:

`(REAL - REAL ANO ANT) / REAL ANO ANT`

## Reglas de signo para EERR

`Inferido desde referencia y consistente con el modelo`

- Ingresos se presentan positivos
- Costos y gastos se presentan negativos
- Las filas de margen o resultado muestran el neto resultante
- Una variacion puede verse positiva aunque la fila sea de gasto si el real es menos negativo que el presupuesto

## Logica de agrupacion del EERR

`Confirmado en Tableau por nombres de filas y subtotales detectados`

La vista se organiza como un estado de resultados con subtotales sucesivos:

1. Ingresos y costos para llegar a `Margen Bruto`
2. Internos para llegar a `Margen Bruto Interno`
3. Gastos de venta y administracion para llegar a `Margen Operacional`
4. Resultado no operacional para llegar a `Margen Antes Provision Comercial`
5. Provision comercial para llegar a `Margen Neto RAI`
6. Impuesto para llegar a `Margen Neto`

## Logica de KPIs del resumen financiero

### 1. Crecimiento de ingresos

Valor principal:

`Inferido desde referencia`

Formula esperada:

`(Ingreso real mes actual / Ingreso real mismo mes ano anterior) - 1`

Indicador secundario:

`Inferido desde referencia`

Comparacion breve contra presupuesto del mes actual.

Alternativa funcional esperada:

`(Ingreso real mes actual - Ingreso presupuesto mes actual) / Ingreso presupuesto mes actual`

### 2. EBITDA

Valor principal:

`Inferido desde estructura financiera`

Debe representar el EBITDA del mes actual en monto.

Implementacion sugerida:

- Usar la medida `EBITDA` si existe ya consolidada en la fuente
- Si no existe, derivarla desde el resultado operacional antes de depreciacion y amortizacion

Indicador secundario:

`Inferido desde referencia`

Comparacion porcentual contra presupuesto del mes actual.

### 3. Margen bruto

Valor principal:

`Confirmado en Tableau`

Formula:

`Margen Bruto / Total Ingresos`

Indicador secundario:

`Inferido desde referencia`

Variacion en puntos porcentuales contra el mismo periodo del ano anterior.

### 4. Margen operacional

Valor principal:

`Inferido desde estructura del EERR`

Formula esperada:

`Margen Operacional / Total Ingresos`

Indicador secundario:

`Inferido desde referencia`

Variacion en puntos porcentuales contra el mismo periodo del ano anterior.

### 5. Caja / liquidez

Valor principal:

`Parcialmente confirmado en Tableau`

Existe una medida confirmada de liquidez:

`Liquidez = Activo Corriente / Pasivo Corriente`

Texto secundario:

`Inferido desde referencia`

`Caja al cierre` debe mostrar el saldo de caja o disponible al cierre del periodo.

### 6. ROA

Valor principal:

`Inferido desde referencia y alias detectados en Tableau`

Formula funcional esperada:

`Resultado TTM / Activos`

Donde:

- `Resultado TTM` = resultado acumulado de ultimos 12 meses
- `Activos` = activos totales del balance

### 7. ROE

Valor principal:

`Inferido desde referencia y alias detectados en Tableau`

Formula funcional esperada:

`Resultado TTM / Patrimonio`

Donde:

- `Resultado TTM` = resultado acumulado de ultimos 12 meses
- `Patrimonio` = patrimonio total del balance

### 8. Resultado del ejercicio

Valor principal:

`Inferido desde referencia y nombres detectados en Tableau`

Debe mostrar el resultado del ejercicio del mes actual en monto.

Referencia funcional:

- En el modelo existe la etiqueta `Ganancia del Ejercicio`

Indicador secundario:

`Inferido desde referencia`

Comparacion porcentual contra presupuesto del mes actual.

## Indicadores financieros confirmados en Tableau

Aunque no todos se usaran visualmente en estas dos vistas, en el workbook si aparecen confirmadas estas formulas base:

### Liquidez

`Confirmado en Tableau`

Formula:

`Activo Corriente / Pasivo Corriente`

### Indice acido

`Confirmado en Tableau`

Formula:

`(Activo Corriente - Inventario) / Pasivo Corriente`

### Capital de trabajo neto

`Confirmado en Tableau`

Formula:

`Activo Corriente - Pasivo Corriente`

### Leverage

`Confirmado en Tableau`

Formula:

`Pasivos / Patrimonio`

### Pasivo / Total activos

`Confirmado en Tableau`

Formula:

`Pasivos / Activos`

## Campos minimos necesarios para implementar esta logica

Para reconstruir estas dos vistas, la fuente deberia permitir como minimo:

- Periodo
- Ano
- Mes
- Saldo real
- Presupuesto
- Clasificacion IFRS o estructura equivalente
- Nivel 1 contable
- Nivel 2 contable
- Nivel 3 contable
- Cuenta contable
- Etiqueta de ingresos
- Etiqueta de gastos
- Activo corriente
- Pasivo corriente
- Inventario
- Activos totales
- Patrimonio
- Resultado del ejercicio

## Punto importante de implementacion

Para la migracion a Streamlit, conviene separar:

- Medidas base contables
- Medidas derivadas del EERR
- KPIs del resumen ejecutivo

De esta forma se evita recalcular multiples veces la misma logica y se conserva trazabilidad entre la vista resumen y la vista EERR principal.
