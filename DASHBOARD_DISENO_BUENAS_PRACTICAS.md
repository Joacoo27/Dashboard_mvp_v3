# Buenas Prácticas de Diseño del Dashboard

## Objetivo
Este documento resume las decisiones visuales y de composición que deben mantenerse en el dashboard de Interwins para conservar una experiencia consistente, limpia y ejecutiva.

## Principios de diseño
- Mantener una apariencia ejecutiva, sobria y clara.
- Evitar depender del estilo nativo del navegador o de Streamlit cuando el componente sea visible para el usuario.
- Priorizar legibilidad por sobre ornamentación.
- Usar consistencia visual entre vistas, tarjetas, títulos, filtros y gráficos.
- Cuidar alineación, espaciado y jerarquía visual antes de agregar nuevos elementos.

## Paleta y fondos
- El color principal de títulos y bandas debe ser `#0A1261`.
- El color de acento puede usarse para bordes, focos o detalles, pero no debe competir con el azul principal.
- El panel principal debe mantenerse en fondo claro, blanco o crema suave.
- Los gráficos deben usar fondo claro explícito, no heredar temas oscuros.
- Evitar contrastes de “modo mixto”, por ejemplo panel claro con header o charts oscuros.
- El sidebar debe usar el mismo azul oscuro principal del sistema.
- Los encabezados del sidebar deben ir en blanco.
- Los campos, botones y textos interactivos dentro del sidebar deben mantenerse oscuros y legibles sobre superficies claras.

## Títulos y encabezados
- Los títulos de sección deben usar fondo azul marino sólido y texto blanco.
- Las bandas principales deben compartir el mismo lenguaje visual que los títulos de sección.
- Cuando haya dos o más bloques en paralelo, los títulos deben arrancar en la misma altura.
- No usar espaciadores manuales por bloque si la alineación puede resolverse con estructura o CSS común.
- Los títulos deben mantener padding, radio y sombra consistentes.
- Los subtítulos de gráficos deben ir sin fondo, en color oscuro, como en `Panel de Venta y Stock`.
- No todos los títulos deben tener la misma jerarquía:
  - título de vista: banda principal azul
  - subtítulo de bloque: texto oscuro sin fondo
  - subtítulo secundario: banda clara más pequeña si se necesita diferenciar una subsección, como `KPI Evolutivo`

## Tarjetas KPI
- Todas las tarjetas de una misma grilla deben tener el mismo alto y ancho visual.
- El contenido interno de las tarjetas debe reservar altura para:
  - título
  - valor principal
  - delta
  - texto descriptivo
- Si una tarjeta no usa delta, igual debe conservar una estructura que no rompa la altura del conjunto.
- Debe existir separación clara entre filas de tarjetas.
- Las tarjetas deben mantener fondo claro, borde suave y sombra ligera.
- Los valores monetarios deben respetar separadores de miles de forma consistente.
- Cada tarjeta puede incorporar un ícono auxiliar pequeño de ayuda en la esquina superior derecha.
- El tooltip de ayuda debe explicar cómo leer el indicador, no repetir literalmente el nombre del KPI.
- El ícono de ayuda debe quedar integrado en la tarjeta, sin desplazar títulos ni desalinear el contenido.

## Alineación y composición
- Si dos gráficos están lado a lado, sus títulos deben alinearse entre sí.
- Si dos gráficos están lado a lado, el borde superior del área gráfica también debe alinearse.
- Cuando un lado tenga controles extra y el otro no, la compensación debe hacerse con una fila estructural común, no con hacks aislados.
- Las columnas deben sentirse balanceadas incluso si no tienen el mismo contenido.
- Evitar saltos verticales bruscos entre una sección y la siguiente.
- Los controles que gobiernan un gráfico deben quedar visualmente más cerca del gráfico que de las tarjetas o bloques superiores.
- Debe existir un separador sutil entre la zona de KPIs y la zona de gráficos cuando ayude a clarificar el cambio de contexto.

## Controles y filtros
- Radios, botones, selects y multiselects deben tener estilo definido por CSS.
- Los estados `hover`, `focus`, `active` y `checked` deben estar diseñados explícitamente.
- No dejar bordes, sombras o tipografías al comportamiento por defecto del navegador.
- Los filtros del sidebar deben compartir una misma familia visual.
- El foco visible debe existir, pero alineado al lenguaje estético general.
- La navegación principal entre vistas debe resolverse como botonera horizontal arriba del contenido principal, no dentro del sidebar.
- Los botones de navegación deben:
  - arrancar alineados a la izquierda del contenido principal
  - compartir la misma altura
  - ocupar solo el espacio necesario, sin extenderse a todo el ancho
  - mostrar estado inactivo en blanco con texto oscuro
  - mostrar estado activo en azul oscuro con texto blanco
- La botonera de `Valorizado / Unidades` debe mantenerse horizontal.
- Si un control tiene ayuda contextual, el ícono debe quedar inmediatamente al lado del componente al que explica.
- La ayuda contextual de controles debe explicar impacto o interpretación del parámetro, no solo definir su nombre.

## Gráficos
- Todos los gráficos deben renderizarse con tema claro consistente.
- En Plotly, definir explícitamente `paper_bgcolor` y `plot_bgcolor`.
- Evitar depender de `theme="streamlit"` cuando altere el diseño esperado.
- Si dos gráficos se presentan juntos, deben tener alturas compatibles.
- La leyenda, los márgenes y la tipografía deben sentirse parte del mismo sistema visual.
- Los gauges deben revisarse visualmente para que no se corten dentro del contenedor.
- Si un gauge requiere más aire, ajustarlo con `domain`, márgenes y altura antes de tocar el contenedor global.
- Los tramos de color del gauge pueden conservar semántica fuerte:
  - rojo: bajo desempeño
  - naranjo: zona media
  - verde: zona saludable
- La línea o barra de avance del gauge debe ser legible, pero no agresiva visualmente.

## Espaciado
- Toda sección debe tener respiración suficiente antes y después.
- Las filas de KPIs deben tener separación vertical homogénea.
- Los títulos no deben quedar pegados al borde del contenedor ni al gráfico siguiente.
- El espaciado debe resolverse desde clases reutilizables, no desde estilos inline repetidos.
- Aun así, el espaciado no debe ser excesivo: si una sección parece “flotar”, reducir gaps y reservas de altura.
- En especial, vigilar:
  - espacio entre la segunda fila de KPIs y el separador
  - espacio entre separador, botonera y títulos de gráficos
  - altura reservada para filas auxiliares de alineación

## Responsive
- En pantallas más estrechas, las tarjetas deben reducir su altura de forma controlada, no colapsar.
- Los tamaños tipográficos deben adaptarse sin romper títulos ni métricas.
- Los componentes deben seguir viéndose intencionales en desktop y mobile.
- Los botones de navegación no deben partirse en dos líneas si puede evitarse con una distribución de columnas más inteligente.

## Sidebar
- El sidebar es una pieza de branding y utilería, no la navegación principal entre vistas.
- Puede incluir un placeholder visual para logo o imagen futura en la parte superior.
- Ese placeholder debe ser reemplazable fácilmente por una imagen real sin rehacer el layout.
- La sección `Configuración Logística` puede incluir ayuda contextual junto al nombre del parámetro.

## Glosario
- En el glosario, solo la cabecera del expander debe usar fondo azul oscuro.
- El cuerpo del expander debe mantenerse en fondo blanco con texto negro.
- Las fórmulas o bloques `code` deben conservar contraste propio sin parecer chips oscuros heredados.

## Consistencia técnica
- Centralizar variables visuales en el bloque CSS principal.
- Reutilizar clases CSS para títulos, tarjetas, gaps y contenedores.
- Evitar valores mágicos repetidos en línea si pueden convertirse en una clase o variable.
- Antes de introducir una nueva variante visual, revisar si ya existe una clase compatible.
- Cuando un patrón ya existe, reaplicarlo:
  - ayudas con ícono `i`
  - subtítulos sin fondo
  - bandas secundarias claras
  - tablas HTML estilizadas sobre fondo claro
- Si un componente nativo de Streamlit no logra el resultado visual esperado, encapsularlo o reemplazar su salida con HTML/CSS controlado.

## Qué evitar
- Fondos oscuros accidentales por herencia del tema.
- Desalineaciones entre títulos de bloques vecinos.
- Gráficos con alturas distintas sin razón funcional.
- Controles con aspecto nativo inconsistente.
- Espaciadores manuales frágiles que dependan de un alto “a ojo”.
- Mezclar estilos nuevos con componentes antiguos sin homologar.
- Tooltips demasiado lejos del elemento que explican.
- Botoneras que cambian de horizontal a vertical por falta de ancho de columna.
- Jerarquías visuales iguales para título principal y subtítulo secundario.
- Tablas o desglose de dimensiones con bajo contraste respecto al fondo.

## Checklist antes de cerrar cambios de UI
- ¿El fondo general sigue claro y consistente?
- ¿Los títulos usan el color y estilo acordado?
- ¿Las tarjetas KPI tienen exactamente la misma dimensión visual?
- ¿Los títulos de bloques vecinos están alineados?
- ¿Los gráficos lado a lado arrancan a la misma altura?
- ¿Los controles visibles tienen estilo propio y no nativo?
- ¿La separación entre filas y secciones se ve intencional?
- ¿El resultado se mantiene limpio después de recargar la app?
- ¿Los botones de navegación tienen la misma altura y una jerarquía activa/inactiva clara?
- ¿Los íconos de ayuda están cerca del elemento que explican?
- ¿La botonera de un gráfico parece pertenecer a ese gráfico?
- ¿Los gauges, tablas y expanders se leen completos dentro de sus contenedores?

## Archivos donde suelen aplicarse estas reglas
- `app.py`: layout, CSS global, títulos, estructura de columnas y espaciados.
- `view_stock.py`: torta de salud y evolutivo de stock.
- `view_salud.py`: gráfico histórico de ventas.
- `view_indice.py`: gauge y barras del índice de salud.
- `view_glosario.py`: expanders metodológicos y jerarquía de documentación.

## Nota de mantenimiento
Si se modifica una regla visual importante, conviene actualizar este documento en el mismo cambio para que la guía siga representando el estado real del dashboard.
