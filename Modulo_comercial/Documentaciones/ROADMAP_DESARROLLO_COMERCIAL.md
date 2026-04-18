# Hoja de Ruta: Desarrollo Módulo Comercial Interwins

Este documento detalla los requerimientos y la visión estratégica para el Módulo Comercial, tomando como referencia el estándar **EMARESA Panel Ferretek v2**.

## 1. Objetivos de Visualización
El objetivo es proporcionar a la gerencia comercial una vista clara del desempeño de ventas, cumplimiento de presupuesto y comportamiento del cliente (retail).

## 2. Indicadores Clave (KPIs) - Tarjetas Ejecutivas
Se implementarán tarjetas interactivas (Flip-Cards) para las siguientes métricas:
- **Ingreso:** Monto total de facturación neta en el periodo.
- **YTD (Year To Date):** Acumulado de ventas desde el 1 de enero hasta la fecha actual.
- **Crecimiento Venta:** Variación porcentual comparada con periodos anteriores (YoY o MoM).
- **Retail Ticket Medio:** Valor promedio de las transacciones (Monto Total / N° de Tickets).
- **Cumplimiento Meta:** Porcentaje de ejecución vs. el Presupuesto (Ppto).
- **Márgenes:** Rentabilidad bruta por línea de negocio, marca o vendedor.
- **Frecuencia de Compra:** Análisis de recurrencia de los clientes.

## 3. Análisis Evolutivo (Gráficos)
Siguiendo la estética moderna del módulo de salud, se implementarán:
- **Evolutivo de Ventas vs Meta:** Gráfico de área/barras con línea de presupuesto para seguimiento de tendencias.
- **Evolutivo de Márgenes:** Monitoreo mensual de la rentabilidad para detectar desviaciones.
- **Mix de Ventas:** Desglose por Marcas, Categorías y Vendedores con visualizaciones de alto impacto (TreeMap o Barras Proporcionales).

## 4. Pendientes Técnicos
- [ ] Definir credenciales de conexión (Base de Datos Comercial).
- [ ] Validar mapeo de campos de la tabla `biwiser_fact_comercial` para cálculos específicos (Ticket Medio y Frecuencia).
- [ ] Sincronización inicial de datos a Parquet.

---
**Referencia:** EMARESA / Ferretek v2
**Documentado por:** Antigravity AI
