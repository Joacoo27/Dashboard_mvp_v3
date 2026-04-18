// Sample data for the dashboard UI kit
window.IW_DATA = {
  kpisInventario: [
    { title: 'VENTA VALORIZADA', value: '$1.234.567', delta: 4.2, meta: 'Corte: Mar-2026', explanation: 'Facturación total del período filtrado, valorizada a precio de venta. Incluye todos los canales activos y excluye notas de crédito.' },
    { title: 'STOCK VALORIZADO', value: '$3.820.900', delta: -1.8, meta: '$ costo × unidades', explanation: 'Valor del inventario al costo actual. Multiplica las unidades en bodega por el costo promedio ponderado de cada SKU.' },
    { title: 'MESES DE INVENTARIO', value: '2,8', delta: -0.6, meta: 'Cobertura promedio', explanation: 'Stock dividido por la demanda promedio mensual. Indica cuántos meses podrías vender sin reponer. Política objetivo: 3 meses.' },
    { title: 'NIVEL DE SERVICIO', value: '94,2%', delta: 1.3, meta: 'SKUs con demanda', explanation: 'Proporción de pedidos cubiertos sin quiebre de stock. Meta mínima: 95%.' }
  ],
  kpisAlertas: [
    { title: 'STOCK EN UNIDADES', value: '48.102', delta: -3.1, meta: 'Total existencias', explanation: 'Total de unidades físicas en bodega al corte actual, sumando todas las familias activas.' },
    { title: 'SKUS EN QUIEBRE', value: '128', delta: -2.1, meta: 'de 2.430 activos', danger: true, explanation: 'SKUs con stock cero pero demanda activa en los últimos 90 días. Cada quiebre es una venta perdida.' },
    { title: 'INVERSIÓN EN EXCESO', value: '$412.700', delta: 8.4, meta: 'Sobre política', danger: true, explanation: 'Valor del inventario que supera la política definida (3 meses). Capital inmovilizado innecesariamente.' },
    { title: 'SKUS SIN DEMANDA', value: '94', delta: 1.5, meta: 'Con stock, sin venta', danger: true, explanation: 'SKUs con stock positivo pero sin venta en los últimos 90 días. Candidatos a liquidación o castigo.' }
  ],
  kpisFinanciero: [
    { title: 'CRECIMIENTO INGRESOS', value: '6,8%', delta: 2.1, meta: 'vs año anterior', explanation: 'Variación porcentual de la facturación neta comparada con el mismo período del año anterior.' },
    { title: 'EBITDA', value: '$82,4M', delta: 4.7, meta: 'Margen operacional', explanation: 'Beneficio antes de intereses, impuestos, depreciaciones y amortizaciones. Refleja la rentabilidad operativa pura del negocio.' },
    { title: 'MARGEN BRUTO', value: '38,2%', delta: 0.9, meta: 'Sobre facturación', explanation: 'Porcentaje de utilidad sobre la facturación tras descontar el costo directo de ventas.' },
    { title: 'CAJA / LIQUIDEZ', value: '1,72', delta: -0.3, meta: 'Ratio corriente', explanation: 'Ratio de disponibilidad inmediata de efectivo frente a obligaciones.' },
    { title: 'ROA', value: '9,4%', delta: 1.2, meta: 'Retorno s/ activos', explanation: 'Mide la eficiencia en el uso de los recursos totales de la empresa.' },
    { title: 'ROE', value: '18,1%', delta: 2.8, meta: 'Retorno s/ patrimonio', explanation: 'Mide el retorno para los accionistas sobre su capital invertido.' },
    { title: 'MARGEN OPERACIONAL', value: '11,9%', delta: 0.4, meta: 'EBIT / Ventas', explanation: 'Cuánto beneficio se obtiene por cada peso de venta, tras descontar G&A.' },
    { title: 'RESULTADO EJERCICIO', value: '$46,2M', delta: 5.9, meta: 'Utilidad neta', explanation: 'Utilidad neta final del período tras descontar todos los costos, gastos e impuestos.' }
  ],
  trendBars: [38, 42, 36, 48, 52, 46, 58, 62, 59, 68, 72, 74],
  trendLine: [40, 40, 40, 45, 48, 50, 55, 58, 60, 63, 66, 70],
  monthLabels: ['Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic','Ene','Feb','Mar'],
  stockEvo: {
    labels: ['May25','Jun25','Jul25','Ago25','Sep25','Oct25','Nov25','Dic25','Ene26','Feb26','Mar26','Abr26'],
    stock: [21000, 22000, 23000, 20500, 19800, 19200, 18000, 14000, 13000, 16000, 27000, 14000],
    cobertura: [3.7, 4.1, 3.2, 3.4, 3.5, 3.5, 3.6, 2.0, 2.2, 2.8, 4.5, 4.4],
  },
  familias: [
    { name: 'Antibióticos', venta: '$48.210.000', stock: '2.341', ns: '94,2%' },
    { name: 'Analgésicos',  venta: '$32.190.500', stock: '1.812', ns: '91,7%' },
    { name: 'Cardiología',  venta: '$21.800.200', stock:   '908', ns: '88,1%' },
    { name: 'Dermatología', venta: '$18.440.000', stock: '1.124', ns: '92,5%' },
    { name: 'Pediatría',    venta: '$14.210.600', stock:   '738', ns: '89,9%' }
  ]
};
