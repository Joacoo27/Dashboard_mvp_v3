# Migración de Query — Cualquier Módulo

El usuario quiere migrar una o varias queries SQL de un módulo del dashboard.

**Input del usuario:** $ARGUMENTS

---

## Tu misión

Migrar las queries SQL de un módulo, propagando todos los cambios necesarios
sin romper ninguna vista. El skill funciona para cualquier módulo del proyecto.

---

## REQUISITOS MÍNIMOS DE DATOS POR MÓDULO

Esta sección define las fuentes de datos obligatorias para que cada módulo funcione
correctamente. Úsala para **validar** que las queries proporcionadas cubren lo necesario
antes de iniciar la migración. Si falta alguna fuente, advierte al usuario.

---

### Módulo: `ventas_salud` → `Modulo_ventas_salud/`

El módulo necesita **4 fuentes**. Las tres primeras son obligatorias; la cuarta es
necesaria para enriquecer la visualización de inventario.

#### Fuente 1 — `ventas` (obligatoria)
**Propósito:** Base de toda la analítica de venta. Alimenta el evolutivo de ventas,
los KPIs de cumplimiento y las vistas de inventario-ventas.

**Origen:** Por defecto se asume que viene de la **tabla transaccional del ERP/WMS**
(movimientos de venta con granularidad de documento o línea). Sin embargo, el cliente
puede proveer una fuente alternativa (vista consolidada, DWH, resumen mensual, etc.).

**En ambos casos se requiere una query SQL.** La distinción entre fuente transaccional
y fuente alternativa solo afecta el nivel de detalle disponible, no la estructura
mínima de columnas que el módulo necesita.

Pregunta siempre al usuario cuál es el origen antes de asumir (ver F0.0 en FASE 0).

**Columnas mínimas requeridas** (independiente del origen):

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | date/datetime | Fecha del movimiento o periodo |
| `codigo_producto` | str | Código SKU del producto |
| `venta` | float | Unidades o monto vendido |

Columnas adicionales recomendadas para análisis completo:
`familia`, `descripcion`, `categoria`, `canal`, `sucursal`, `cliente`

> **Nota sobre granularidad:** Si el cliente usa fuente alternativa (ej: resumen
> mensual pre-agregado), advertir que métricas como estacionalidad intra-mes o
> análisis por documento no estarán disponibles. No bloquear la migración por esto.

#### Fuente 2 — `stock` (obligatoria)
**Propósito:** Alimenta los indicadores de inventario: cobertura, sobre-stock,
rotación y el índice de salud del inventario.

Viene de tablas de **stock actual e histórico diario** del WMS.

**Columnas mínimas requeridas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | date | Fecha del snapshot de stock |
| `codigo_producto` | str | Código SKU |
| `stock` | float | Unidades en stock |
| `costo_unitario` | float | Costo unitario del producto |

Columnas adicionales recomendadas:
`transito` (unidades en tránsito), `lead_time` (días de reposición),
`stock_minimo`, `stock_maximo`, `punto_reorden`

> **Nota sobre tránsitos:** Si el cliente maneja unidades en tránsito
> (pedidos confirmados aún no recibidos), deben incluirse en esta fuente
> como columna `transito`. Sin ella, la cobertura real queda subestimada
> y el índice de salud puede marcar falsas alertas de quiebre de stock.

#### Fuente 3 — `evolutivo` (obligatoria)
**Propósito:** Serie de tiempo mensual de stock + venta por SKU. Permite calcular
promedios móviles, tendencias y el índice de salud histórico.

En el proyecto actual se **genera automáticamente** cruzando `ventas` + `stock`
dentro de `actualizar_todo()`. No necesita una query propia a menos que el cliente
la provea pre-calculada.

**Columnas mínimas requeridas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | date | Mes del periodo |
| `codigo_producto` | str | Código SKU |
| `stock` | float | Stock promedio del mes |
| `venta` | float | Venta del mes |

Si el cliente provee esta fuente directamente, agrégala como query independiente.
Si no, mantén la lógica de derivación automática en `actualizar_todo()`.

#### Fuente 4 — `maestro` (necesaria para enriquecimiento)
**Propósito:** Dimensiones del producto para filtros y agrupaciones en vistas.
Sin el maestro, los filtros por familia/proveedor/tiering no funcionan.

Viene de la **tabla maestra de productos** del ERP.

**Columnas mínimas requeridas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `codigo` | str | Código SKU (llave de join con las otras fuentes) |
| `descripcion` | str | Nombre del producto |
| `familia` | str | Familia o línea de producto |

Columnas adicionales recomendadas:
`descripcion_corta`, `proveedor`, `tiering`, `tecnologia`, `unidad_medida`

---

### Módulo: `financiero` → `Modulo_financiero/`

El módulo puede funcionar con **1 fuente** consolidada, aunque puede extenderse
a 2 si el cliente maneja presupuesto en una tabla separada.

#### Fuente 1 — `contable` (obligatoria)
**Propósito:** Base de todo el análisis financiero: Estado de Resultados, Balance
y Resumen Ejecutivo. Debe incluir tanto movimientos reales como presupuesto.

Viene del **sistema contable** del cliente (PostgreSQL típicamente).
En el proyecto actual combina movimientos contables + presupuesto + maestro de cuentas
en una sola query consolidada (`QUERY_CONSOLIDADO`).

**Columnas mínimas requeridas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | int | Año contable |
| `mes` | int | Mes contable (1–12) |
| `cuenta_contable` | str | Código de cuenta |
| `saldo` | float | Saldo real del periodo |
| `PPTO` | float | Presupuesto del periodo (puede ser 0) |
| `Estado_Financiero` | str | `"ESTADO DE RESULTADOS"` o `"BALANCE"` |
| `Nivel_1_IFRS` | str | Agrupación nivel 1 IFRS (ej: `"INGRESOS"`) |
| `Nivel_2_IFRS` | str | Agrupación nivel 2 IFRS |
| `Nivel_3_IFRS` | str | Agrupación nivel 3 IFRS (línea del EERR/Balance) |
| `pcdesc_1` | str | Descripción nivel 1 del plan de cuentas |
| `pcdesc_2` | str | Descripción nivel 2 del plan de cuentas |

Columnas adicionales recomendadas para análisis completo:
`debe`, `haber`, `pcdesc_3`, `pcdesc_4`, `pccodi_*`, `Nivel_Ratio`,
`Cantidad_Registros_Contables`, `Glosas_Consolidadas`

> **Nota sobre presupuesto:** Si el cliente tiene el presupuesto en una tabla
> separada, lo más limpio es consolidarlo dentro de la misma query usando un
> LEFT JOIN o UNION. El módulo está diseñado para recibir real + presupuesto
> en la misma fila (mismo `anio`, `mes`, `cuenta_contable`).

---

### Módulo: `comercial` → `Modulo_comercial/`

El módulo funciona con **1 fuente** que contiene la actividad comercial consolidada.

#### Fuente 1 — `comercial` (obligatoria)
**Propósito:** Base de KPIs comerciales: cumplimiento de presupuesto, margen,
variación año a año, análisis por vendedor y por categoría.

Viene de una **tabla de hechos comercial** del ERP/BI del cliente
(en el proyecto actual: `biwiser_fact_comercial`).

**Columnas mínimas requeridas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha_periodo` | date | Fecha o periodo del registro |
| `monto_real` | float | Monto de venta real |
| `monto_ppto` | float | Presupuesto del periodo |
| `margen_pct` | float | Porcentaje de margen |

Columnas adicionales recomendadas para análisis completo:
`cumplimiento_ppto`, `variacion_aa`, `categoria_producto`, `vendedor_nombre`,
`canal`, `region`, `linea_negocio`

> **Nota:** Si el cliente no tiene `margen_pct` como columna calculada en BD,
> puede derivarse en la query con `(monto_real - costo_real) / monto_real * 100`.
> Lo mismo aplica para `cumplimiento_ppto` = `monto_real / monto_ppto * 100`.

---

## ASSETS Y BRANDING DEL CLIENTE

Esta sección define todos los elementos visuales que deben personalizarse para un
nuevo cliente. Aplica **siempre**, independientemente de si se está migrando una
o varias queries. Ejecuta estos pasos **después** de completar la migración de datos.

---

### Asset 1 — Logo del sidebar (izquierda superior)

**Dónde se usa:** Panel lateral izquierdo, esquina superior. Lo renderiza
`render_sidebar_brand()` en `core/components.py`, invocado desde `app.py`.

**Rutas que busca `_resolve_logo_asset()` en `app.py`, en orden de prioridad:**
1. `IMPORTACION MOCKUP/assets/logo_mark.svg` ← ruta legacy del proyecto base
2. `assets/logo_interwins.png`
3. `assets/logo_interwins.jpg`

**Formato soportado para embedding inline:** solo `.svg`. Los PNG/JPG se ignoran
silenciosamente y activan el fallback (ver más abajo).

**Qué hacer:**

Si el cliente provee un logo:
1. Convierte a SVG si es posible, o solicítalo en SVG al cliente
2. Colócalo en `assets/logo_mark.svg` (crea la carpeta `assets/` si no existe)
3. Actualiza `_resolve_logo_asset()` en `app.py` para que busque primero
   `assets/logo_mark.svg`:
   ```python
   def _resolve_logo_asset() -> Path | None:
       root = Path(__file__).resolve().parent
       for candidate in (
           root / "assets" / "logo_mark.svg",
           root / "assets" / "logo_cliente.png",
           root / "assets" / "logo_cliente.jpg",
       ):
           if candidate.exists():
               return candidate
       return None
   ```

Si el cliente **no** provee logo → activa el placeholder (ver Asset 2).

---

### Asset 2 — Placeholder de logo (fallback)

Cuando no hay logo, `render_sidebar_brand()` muestra un cuadro con texto
definido en `core/components.py` línea:
```python
logo_markup = '<div class="iw-sidebar-logo-fallback">iw</div>'
```

El texto `"iw"` son las iniciales de Interwins y **debe cambiarse** para cada cliente.

**Qué hacer cuando no hay logo:**

Modifica `render_sidebar_brand()` en `core/components.py` para aceptar un
parámetro de iniciales:
```python
def render_sidebar_brand(
    logo_path: str | Path | None,
    title: str = "Interwins",
    subtitle: str = "PANEL EJECUTIVO",
    fallback_initials: str = "iw",          # ← agregar este parámetro
) -> None:
    logo_markup = f'<div class="iw-sidebar-logo-fallback">{fallback_initials}</div>'
    ...
```

Luego actualiza la llamada en `app.py`:
```python
render_sidebar_brand(
    _resolve_logo_asset(),
    title="<Nombre Cliente>",
    subtitle="PANEL EJECUTIVO",
    fallback_initials="<XX>",   # 2-3 letras en minúsculas, ej: "ac", "tg", "int"
)
```

Pregunta al usuario el nombre del cliente y sus iniciales antes de hacer este cambio.
Si el usuario no lo sabe aún, usa `"??"` como placeholder y añade un comentario
`# TODO: reemplazar con iniciales del cliente`.

---

### Asset 3 — Nombre y subtítulo del panel

**Dónde se usan:**
- `page_title` en `st.set_page_config()` → título de la pestaña del browser
- `page_icon` en `st.set_page_config()` → ícono de la pestaña del browser
- `title` y `subtitle` en `render_sidebar_brand()` → texto bajo el logo en el sidebar

**Valores actuales en `app.py`:**
```python
st.set_page_config(
    page_title="Panel de Interwins",
    page_icon="📊",
    ...
)
...
render_sidebar_brand(_resolve_logo_asset())  # title="Interwins", subtitle="PANEL EJECUTIVO"
```

**Qué hacer:**

Actualiza `app.py` con los datos del cliente. Si no se conocen, deja placeholders:
```python
st.set_page_config(
    page_title="Panel de <Cliente>",        # TODO: nombre del cliente
    page_icon="📊",                          # TODO: emoji o ruta a favicon del cliente
    layout="wide",
    initial_sidebar_state="expanded",
)
...
render_sidebar_brand(
    _resolve_logo_asset(),
    title="<Cliente>",                       # TODO: nombre del cliente
    subtitle="PANEL EJECUTIVO",              # TODO: subtítulo si el cliente lo pide
    fallback_initials="??",                  # TODO: iniciales del cliente
)
```

---

### Asset 4 — Colores de marca

La paleta de colores **no se modifica**. El estándar visual de este proyecto
(`--iw-navy`, `--iw-accent`, `--iw-brand`, etc.) se mantiene en todos los clientes
salvo que el usuario lo indique explícita y declarativamente en el mismo mensaje
donde invoca el skill (ej: "usa #D72323 como color principal").

**No preguntes al usuario por colores. No toques `colors_and_type.css` ni `theme.py`
a menos que vengan valores hex explícitos en el input.**

---

### Checklist de assets al iniciar un proyecto nuevo

Ejecuta este checklist y muestra el resultado al usuario al final de la migración:

```
📋 Assets del cliente — estado:

Logo:
  [ ] assets/logo_mark.svg existe             → colocar SVG del cliente
  [x] fallback_initials configurado           → render_sidebar_brand(..., fallback_initials="??")

Identidad textual (app.py):
  [ ] page_title actualizado                  → "Panel de <Cliente>"
  [ ] page_icon actualizado                   → emoji o favicon del cliente
  [ ] sidebar title actualizado               → nombre del cliente
  [ ] sidebar subtitle actualizado            → subtítulo deseado

TODOs pendientes en código: N
(Colores: estándar del proyecto — no se modifican)
```

Marca como `[x]` los que ya están resueltos y `[ ]` los que quedan pendientes.

---

## HOMOLOGACIÓN DE QUERIES

Toda query integrada al proyecto **debe** tener una versión homologada en la
carpeta `queries_homologadas/<modulo>/`. La versión homologada es el contrato
portable entre clientes: al replicar el proyecto para otro cliente, sólo
cambian las CTEs superiores (fuentes y reglas propias del cliente), mientras
que el `SELECT` final conserva exactamente los nombres y tipos del contrato
del módulo.

Ejecuta este paso **siempre** después de completar la migración de datos y
antes de la verificación de Assets. Es obligatorio tanto para queries nuevas
como para reemplazos.

---

### Estructura de `queries_homologadas/`

```
queries_homologadas/
├── README.md                  ← índice módulo → parquet → query + política de nulos
├── <modulo_1>/
│   └── <nombre_fuente>.sql
└── <modulo_2>/
    └── <nombre_fuente>.sql
```

Si la carpeta o su `README.md` no existen, créalos antes de generar la
primera query homologada del proyecto.

---

### Requisitos de cada query homologada

**1. Encabezado con metadata del módulo** (comentarios SQL al inicio del archivo):

```sql
-- =============================================================================
-- QUERY HOMOLOGADA — <Nombre del Módulo>
-- -----------------------------------------------------------------------------
-- Modulo        : <carpeta del módulo>
-- Parquet       : <ruta relativa al parquet que alimenta>
-- Consumidores  : <archivos .py que leen el parquet>
-- Origen actual : <ruta del .sql del cliente>
-- Grano final   : <descripción del grano de la tabla resultante>
-- =============================================================================
```

**2. CTEs cliente-específicas marcadas**: cualquier CTE que aplique reglas
propias del cliente (filtros, normalizaciones, overrides de SKU, homologación
de maestro) debe llevar un comentario `-- [CLIENTE-ESPECIFICO] <por qué cambia>`
para que el próximo cliente sepa exactamente dónde intervenir.

**3. SELECT final marcado como contrato [ESTANDAR]**:

```sql
-- =============================================================================
-- CONTRATO FINAL — [ESTANDAR]
-- -----------------------------------------------------------------------------
-- <resumen breve de la política de nulos aplicable al contrato>
--
-- Columnas obligatorias en nombre/tipo (valor nullable):
--   <col1>     <tipo>   -- <descripción>
--   ...
-- =============================================================================
SELECT ... FROM ...;
```

El `SELECT` final debe:

- Usar **exactamente** los nombres y tipos definidos en
  "REQUISITOS MÍNIMOS DE DATOS POR MÓDULO" para el módulo correspondiente.
- Agrupar columnas por sección semántica (Tiempo, Tienda, Vendedor, Documento,
  Cliente, Producto, Métricas, Trazabilidad, etc.) con comentarios
  `-- [ESTANDAR] <Sección>`.
- Aplicar **casts explícitos** (`::text`, `::numeric`, `::date`, `::int`,
  `::timestamp`).
- **No forzar fillers** (`'Sin X'`, `'Nulo'`, `0`): todas las columnas del
  contrato son NULLABLE. Si un campo no aplica al cliente o no existe en la
  fuente, se propaga como `NULL`. Excepciones permitidas:
  - Columnas derivadas deterministicamente
    (ej: `monto_margen = monto_real − monto_costo`).
  - `COALESCE` entre dos columnas alternativas reales
    (ej: `COALESCE(p.tipo_p, s.tipo_producto)`) — eso es fallback entre
    fuentes, no literal de relleno.

---

### Actualizar `queries_homologadas/README.md`

Al crear/modificar una query homologada, actualizar el README:
- Agregar o ajustar la fila del **índice módulo → parquet → query**.
- Actualizar la tabla de contrato del módulo si cambiaron columnas.
- Mantener la sección "Política de nulos" como declaración transversal.

---

### Checklist de homologación

Ejecuta este checklist y muéstralo al usuario al terminar:

```
📋 Homologación de query — estado:

  [ ] Archivo en queries_homologadas/<modulo>/<nombre>.sql
  [ ] Encabezado con Modulo + Parquet + Consumidores + Origen + Grano
  [ ] CTEs client-specific marcadas con [CLIENTE-ESPECIFICO]
  [ ] SELECT final marcado como CONTRATO FINAL — [ESTANDAR]
  [ ] Columnas del contrato coinciden con REQUISITOS MÍNIMOS del módulo
  [ ] Casts explícitos (::text, ::numeric, ::date, ::int, ::timestamp)
  [ ] Sin fillers ('Sin X', 'Nulo', 0) salvo derivaciones o fallbacks reales
  [ ] queries_homologadas/README.md actualizado
```

Marca como `[x]` los items resueltos y `[ ]` los que quedan pendientes.

---

### FASE -1 — CLONACIÓN DE PROYECTO (OPCIONAL)

Si el usuario indica que quiere levantar un cliente nuevo y estamos trabajando sobre el directorio "Plantilla" (ej: `MVP_V3_Indura` o `Motor_V3`), el skill debe:

1. **Sugerir/Realizar la clonación**: Crear una copia completa del directorio actual en una nueva carpeta llamada `MVP_V3_<CLIENTE_NOMBRE>` (dentro del mismo directorio padre).
2. **Cambiar de contexto**: Notificar al usuario que de ahora en adelante se trabajará en la nueva carpeta.
3. **Continuar con FASE 0** en el nuevo directorio.

---

## FASE 0 — DETECCIÓN DE PROYECTO NUEVO (ejecutar siempre primero)

Antes de cualquier otra acción, evalúa si el repositorio se encuentra en estado de
**levantamiento inicial para un nuevo cliente**. Si se detecta, entra en modo de
setup y no continúes a PASO 0 hasta que el usuario entregue las queries.

---

### Señales de proyecto nuevo (verifica todas)

**Señal A — Branding sin personalizar:**
Lee `app.py`. Si contiene alguno de estos valores sin modificar:
- `page_title="Panel de Interwins"`
- `title="Interwins"` en la llamada a `render_sidebar_brand`

→ el proyecto aún tiene identidad del template base.

**Señal B — Parquets heredados presentes:**
Busca archivos `*.parquet` dentro de cualquier carpeta `*/cache/` del proyecto.
Si existen → son datos del cliente anterior, no del nuevo cliente.

**Señal C — Sin credenciales de BD configuradas:**
Verifica si existe algún archivo `.env` en la raíz o en algún módulo con
`HOST_DATABASE` definido y no vacío. Si no existe o está vacío → sin conexión.

**Señal D — Sin queries del cliente:**
Verifica si existe una carpeta `queries/` en la raíz con archivos `.sql` dentro.
Si no existe → el cliente aún no ha entregado sus fuentes de datos.

---

### Criterio de activación

Si se cumplen **Señal A + Señal B** (o cualquiera combinada con Señal D):
→ **Modo levantamiento de proyecto nuevo activado.**

Si `$ARGUMENTS` está vacío y se cumple al menos una señal:
→ **Modo levantamiento de proyecto nuevo activado.**

Si `$ARGUMENTS` contiene queries/rutas válidas y **no** se cumple Señal A:
→ el proyecto ya fue configurado; saltar esta fase e ir directo a PASO 0.

---

### Acciones en modo levantamiento

#### F0.0 — Onboarding conversacional

Antes de hacer cualquier cambio en el proyecto, inicia una conversación con el
usuario para recopilar la información base del cliente. Haz las preguntas en un
solo mensaje, de forma clara y amigable:

```
¡Hola! Veo que estás configurando este proyecto para un nuevo cliente.
Antes de comenzar necesito algunos datos:

1. ¿Cuál es el nombre del cliente?
   (Se usará como título del panel y en el branding del sidebar)

2. ¿Quieres compartir contexto adicional sobre el cliente o el proyecto?
   (Opcional — rubro, tamaño, particularidades del negocio, foco del análisis, etc.)

3. ¿Qué módulos vas a trabajar para este cliente?
   [ ] Financiero          — Estado de resultados, balance, presupuesto vs real
   [ ] Comercial           — KPIs de ventas, cumplimiento, margen por vendedor/categoría
   [ ] Salud de Inventario — Stock, cobertura, tránsitos, índice de salud por SKU

   (Puedes seleccionar uno, dos o los tres)
```

Si entre los módulos seleccionados está **Salud de Inventario**, agrega esta
pregunta de seguimiento en el mismo mensaje antes de cerrar el onboarding:

```
Sobre el módulo de Salud de Inventario:

La fuente de ventas puede venir de dos orígenes distintos:

  A) Transaccional del ERP — query sobre la tabla de movimientos/transacciones
     del sistema (opción más común, mayor granularidad)

  B) Fuente alternativa — un resumen, un DWH, una vista consolidada u otra
     tabla que no sea la transaccional directa

En ambos casos necesito que me proporciones la query SQL correspondiente.
¿Cuál de las dos opciones aplica para este cliente?
```

Guarda la respuesta como `VENTAS_FUENTE`:
- `"transaccional"` si el usuario elige opción A
- `"alternativa"` + descripción breve si elige opción B

Si se activó FASE -1:
- Procede a copiar el directorio actual a `../MVP_V3_<CLIENTE_NOMBRE>`.
- Informa al usuario: "He creado la carpeta `MVP_V3_<CLIENTE_NOMBRE>` para trabajar de forma independiente".

Usa `VENTAS_FUENTE` en F0.2 para nombrar el archivo sugerido:
- `"transaccional"` → sugiere `ventas.sql` con la nota `← query transaccional del ERP`
- `"alternativa"` → sugiere `ventas.sql` con la nota `← [descripción que dio el usuario]`

En ambos casos el archivo requerido es el mismo (`ventas.sql`). La distinción es
solo para que el usuario sepa qué debe escribir en esa query.

Espera la respuesta del usuario antes de continuar. Con la información recibida:

- **Nombre del cliente** → guárdalo como `CLIENTE_NOMBRE` para usarlo en:
  - `page_title` de `app.py`
  - `title` en `render_sidebar_brand()`
  - `fallback_initials` (deriva las iniciales automáticamente: primeras letras
    de cada palabra, máximo 3 caracteres, en minúsculas;
    ej: "Acme Corp" → `"ac"`, "Tech Group SA" → `"tg"`)

- **Contexto opcional** → guárdalo como `CLIENTE_CONTEXTO`. Úsalo como memoria
  de sesión para dar respuestas más relevantes durante toda la configuración.
  Si el usuario describe particularidades del negocio (ej: "maneja tránsitos
  internacionales con lead times largos"), tenlas en cuenta al generar TODOs
  y advertencias en los pasos siguientes.

- **Módulos seleccionados** → guárdalos como `MODULOS_ACTIVOS`. Usa esta lista para:
  - Crear solo los subdirectorios `queries/<modulo>/` de los módulos activos (F0.2)
  - Mostrar solo los comandos de migración relevantes (F0.3)
  - En los pasos de migración posteriores, omitir validaciones de módulos inactivos

  Mapeo de nombres de módulo a carpetas del proyecto:
  | Nombre conversacional | Carpeta |
  |---|---|
  | Financiero | `Modulo_financiero/` |
  | Comercial | `Modulo_comercial/` |
  | Salud de Inventario | `Modulo_ventas_salud/` |

#### F0.1 — Limpiar parquets heredados

Lista todos los archivos `.parquet` encontrados en carpetas `*/cache/`,
filtrando solo los módulos en `MODULOS_ACTIVOS`:

```
Parquets heredados encontrados para los módulos seleccionados:
  Modulo_financiero/cache/contable_financiero_cache.parquet   [si Financiero activo]
  Modulo_ventas_salud/cache/ventas_cache.parquet              [si Salud de Inventario activo]
  Modulo_ventas_salud/cache/stock_cache.parquet               [si Salud de Inventario activo]
  ...

Estos archivos contienen datos del proyecto anterior y deben eliminarse
antes de configurar <CLIENTE_NOMBRE>. ¿Confirmas la eliminación?
```

Espera confirmación. Una vez confirmado, elimina los archivos listados.
No elimines las carpetas `cache/` — solo los `.parquet` dentro de ellas.

Si hay parquets de módulos **no activos**, no los menciones ni los toques.

#### F0.2 — Crear estructura de queries e informar al usuario

Crea la carpeta `queries/` en la raíz del proyecto (si no existe) con un
subdirectorio vacío por cada módulo en `MODULOS_ACTIVOS`.

Luego muestra al usuario exactamente qué archivos depositar, mostrando
**solo los módulos activos** con el nombre del cliente como contexto:

```
Proyecto: <CLIENTE_NOMBRE>
Módulos activos: [lista de MODULOS_ACTIVOS]

Deposita las queries de <CLIENTE_NOMBRE> en la siguiente estructura:

queries/
  financiero/                          [si Financiero activo]
    contable.sql     ← movimientos contables + presupuesto (obligatoria)

  ventas_salud/                        [si Salud de Inventario activo]
    ventas.sql       ← transaccional mensual de ventas (obligatoria)
    stock.sql        ← stock actual e histórico diario (obligatoria)
    maestro.sql      ← maestro de productos (necesaria)
    evolutivo.sql    ← opcional, solo si el cliente la provee pre-calculada

  comercial/                           [si Comercial activo]
    comercial.sql    ← tabla de hechos comercial (obligatoria)
```

Si `CLIENTE_CONTEXTO` contiene información relevante sobre las fuentes de datos
(ej: "usa SAP", "tiene un DWH en Redshift", "no tiene presupuesto cargado"),
agrégala como nota contextual debajo de la estructura para orientar al usuario.

#### F0.3 — Instrucciones para continuar

Muestra los comandos exactos según `MODULOS_ACTIVOS`, usando `CLIENTE_NOMBRE`
para dar contexto. Actualiza también `app.py` con el nombre y las iniciales
derivadas ya conocidas (no esperes a que el usuario lo pida — hazlo ahora):

**Actualizar branding y modularidad en `app.py`** (con los datos de F0.0):
- `page_title` → `"Panel de <CLIENTE_NOMBRE>"`
- `render_sidebar_brand(title="<CLIENTE_NOMBRE>", fallback_initials="<iniciales>")`
- **Modularidad**: Reescribir la lista `MODULE_PACKAGES` para incluir solo las carpetas de los `MODULOS_ACTIVOS`.
  - Ejemplo si solo eligió Comercial: `MODULE_PACKAGES = ["Modulo_comercial"]`
- Si aún no se tiene logo → deja `_resolve_logo_asset()` sin cambios y
  anota `# TODO: agregar assets/logo_mark.svg con el logo de <CLIENTE_NOMBRE>`

Luego muestra al usuario:

```
✅ Branding actualizado para <CLIENTE_NOMBRE>

Cuando tengas las queries listas, ejecuta uno de estos comandos:

  # Por módulo (recomendado si vas agregando queries de a una):
  /migrate-module-query financiero queries/financiero/      [si Financiero activo]
  /migrate-module-query ventas_salud queries/ventas_salud/  [si Salud de Inventario activo]
  /migrate-module-query comercial queries/comercial/        [si Comercial activo]

  # O todos a la vez si ya tienes todas las queries:
  /migrate-module-query financiero queries/financiero/ && \
  /migrate-module-query ventas_salud queries/ventas_salud/ && \
  /migrate-module-query comercial queries/comercial/

Pendiente:
  [ ] Depositar queries en queries/<modulo>/
  [ ] Agregar logo del cliente en assets/logo_mark.svg  (SVG preferido)
```

#### F0.4 — Detener ejecución

No continúes a PASO 0. El skill termina aquí hasta la próxima invocación
con queries proporcionadas.

---

## PASO 0 — Parsear argumentos e identificar módulo

### 0a — Formato de `$ARGUMENTS`

```
<modulo> <archivo.sql> [archivo2.sql ...]
<modulo> nombre1:<archivo.sql> nombre2:<archivo2.sql>
<modulo> <carpeta/>
```

El **primer token** siempre es el nombre del módulo. El resto son las queries.

Ejemplos válidos:
```
financiero contable.sql
ventas_salud transaccional.sql ventas.sql
comercial resumen:contratos.sql detalle:movimientos.sql
financiero _archive/sql_scripts/
```

Si `$ARGUMENTS` está vacío o falta el módulo, pregunta al usuario.

### 0b — Resolver la carpeta del módulo

Busca en la raíz del proyecto una carpeta cuyo nombre contenga el token del módulo
(insensible a mayúsculas/minúsculas y sin importar prefijos como `Modulo_`).

Ejemplos de resolución:
| Token | Carpeta resuelta |
|---|---|
| `financiero` | `Modulo_financiero/` |
| `ventas_salud` | `Modulo_ventas_salud/` |
| `comercial` | `Modulo_comercial/` |
| `Modulo_financiero` | `Modulo_financiero/` |

Si no encuentras ninguna carpeta que coincida, lista las carpetas disponibles
y pide al usuario que corrija el nombre.

### 0c — Leer las queries de entrada

Para cada archivo SQL:
- Si termina en `.sql` → léelo con Read
- Si es una carpeta → lee todos los `.sql` que contenga
- Si usa formato `nombre:archivo.sql` → separa nombre lógico y ruta
- Si es texto SQL directo → úsalo tal cual

**Nombre lógico de cada fuente:**
- Explícito (`nombre:archivo`) → úsalo directamente
- Del nombre de archivo: `contable_financiero.sql` → `contable_financiero`
- Si no hay nombre claro → pregunta antes de continuar

Convención: solo minúsculas, sin espacios, sin tildes (`ventas`, `contable`, `centro_costo`).

### 0d — Elegir ruta

- **1 query** → **Ruta A** (reemplazo de fuente existente)
- **2+ queries** → **Ruta B** (multi-fuente)

---

## PASO 1 — Explorar la estructura actual del módulo

Antes de hacer cualquier cambio, lee los siguientes archivos del módulo resuelto
y construye un inventario de la estructura actual:

### 1a — `<modulo>/consolidar_parquets.py`

Extrae:
- Lista de constantes de query: nombre y columnas del SELECT final de cada una
  (ej: `QUERY_CONSOLIDADO → [anio, mes, saldo, ...]`)
- Signatura actual de `actualizar_todo()`: ¿devuelve `int` o `dict`?
- Lista de parquets que guarda y sus rutas

### 1b — `<modulo>/data.py`

Extrae:
- Constantes `*_PARQUET` definidas
- Función(es) `build_demo_*()` existentes y qué columnas generan
- Qué devuelve `load_all_data()`: claves del dict de retorno

### 1c — `<modulo>/logic.py`

Extrae:
- `DIMENSION_FILTERS` (puede estar vacío o no existir)
- Lista `expected_cols` dentro de `_prepare_*()` (puede tener otro nombre)
- Columnas derivadas que genera la función de preparación (nunca tocar estas)

### 1d — `<modulo>/__init__.py`

Extrae:
- Filtros `st.sidebar.multiselect(...)` existentes (qué columnas filtran)
- Lógica del botón de actualización: cómo maneja el retorno de `actualizar_todo()`
- Función `_parquet_last_updated()` o similar

### 1e — Archivos de vistas (`view_*.py`)

Lista los archivos de vista del módulo. Para cada uno, nota qué claves del
context usa (`context["contable"]`, `context["ventas"]`, etc.).

Muestra al usuario el inventario antes de continuar:
```
Módulo: <nombre> → <carpeta>
Fuentes actuales:
  - <nombre_fuente> → <QUERY_CONST> → <PARQUET_CONST> → context["<clave>"]
Vistas:
  - view_X.py → usa context["<clave>"]
  - view_Y.py → usa context["<clave>"]
```

### 1f — Validar cobertura de fuentes mínimas

Cruza las queries proporcionadas contra los **REQUISITOS MÍNIMOS** definidos
al inicio de este skill para el módulo en cuestión.

Para cada fuente mínima requerida:
- ✅ **Cubierta**: hay una query que la provee (nombre coincide o columnas coinciden)
- ⚠️ **Parcial**: hay una query pero le faltan columnas obligatorias → lista cuáles
- ❌ **Faltante**: ninguna query cubre esta fuente

Muestra el resultado al usuario:
```
Cobertura de fuentes mínimas — módulo <nombre>:
  ✅ ventas       → cubierta por <archivo.sql>
  ⚠️ stock        → cubierta parcialmente (faltan: transito, lead_time)
  ❌ maestro      → no hay query para esta fuente

Las fuentes ❌ y ⚠️ causarán errores o funcionalidad degradada en las vistas.
¿Deseas continuar de todos modos o agregar las queries faltantes?
```

Espera respuesta del usuario antes de continuar si hay fuentes ❌ o ⚠️ obligatorias.
Si el usuario confirma continuar con fuentes faltantes, agrega un `# TODO` visible
en `consolidar_parquets.py` indicando qué falta.

### 1g — Inventariar queries homologadas existentes

Verifica si existe `queries_homologadas/` en la raíz. Si existe, lista los
archivos `.sql` homologados presentes para el módulo en cuestión:

```
Queries homologadas del módulo <nombre>:
  - queries_homologadas/<modulo>/<nombre_fuente_1>.sql
  - queries_homologadas/<modulo>/<nombre_fuente_2>.sql
  (ninguna → se crearán al final de la migración)
```

Usa esta información para decidir, en el paso de homologación posterior:
- Si la fuente ya tiene archivo homologado → **actualizar** (reemplazo).
- Si no existe → **crear** desde cero.

Si `queries_homologadas/` no existe, anótalo para crearla junto con su
`README.md` durante la homologación.

---

## ═══════════════════════════════════════════════
## RUTA A — Query única (reemplazo)
## ═══════════════════════════════════════════════

### A1 — Calcular diff de columnas

Extrae las columnas del SELECT final de la nueva query.
Compara con las columnas de la fuente existente que va a reemplazar.

Si hay más de una fuente existente y no está claro cuál reemplaza, pregunta al usuario.

Muestra el diff **antes de hacer cambios**:
```
Fuente: <nombre> (<QUERY_CONST>)
Columnas AGREGADAS (N): [lista]
Columnas ELIMINADAS (N): [lista]
Sin cambios: N columnas
```

Si `eliminadas` contiene alguna columna que aparece en `expected_cols` de `logic.py`
o en las vistas, advierte al usuario y pide confirmación.

### A2 — Actualizar `consolidar_parquets.py`

Reemplaza el contenido de la constante de query correspondiente.
Mantén el mismo nombre de constante que ya existe. No toques `actualizar_todo()`.

### A3 — Actualizar `data.py`

**Función `_base_*_row()` o equivalente** (fila base del demo data):
- Columnas numéricas nuevas → `0.0`
- Columnas de conteo (`Cantidad_*`) → `1`
- Columnas de texto nuevas → `"Demo"`
- Columnas de fecha nuevas → `fecha.date()`
- Elimina claves de columnas eliminadas

**Función `build_demo_*()`**:
- Agrega entradas en `row.update({...})` para columnas jerárquicas/clasificatorias nuevas
- Elimina entradas de columnas eliminadas
- Columnas sin categoría clara → valor neutro + `# TODO: valor demo para <col>`

### A4 — Actualizar `logic.py`

**`DIMENSION_FILTERS`**: una columna nueva califica como filtro si:
- Es texto/categórica (no numérica, no fecha)
- No es jerarquía fija del módulo (las que ya existen como base de clasificación)
- Su nombre sugiere dimensión de negocio: `centro_costo`, `region`, `sucursal`,
  `tipo_contrato`, `proyecto`, `responsable`, `linea_negocio`, etc.

Convención de clave: `<prefijo_modulo>_<NombreCol>_filter`
(prefijo = las 3 primeras letras del módulo: `fin_`, `ven_`, `com_`)

Elimina las de columnas eliminadas; agrega las de columnas nuevas que califican.

**`expected_cols`** en la función de preparación:
- Elimina columnas de `eliminadas` que estén en esa lista
- Agrega columnas de `agregadas` necesarias para la clasificación

Las columnas derivadas (cualquier columna que la función de preparación **genera**,
no las que lee) son invariantes — no las toques.

### A5 — Actualizar `__init__.py`

Para cada entrada de `DIMENSION_FILTERS`:
- Patrón de filtro en sidebar:
  ```python
  opciones = sorted(df["NombreCol"].dropna().unique())
  filtro = st.sidebar.multiselect("Label", options=opciones, default=[], key="<prefijo>_NombreCol_filter")
  if filtro:
      df = df[df["NombreCol"].isin(filtro)]
  context["meta"]["active_filters"]["NombreCol"] = filtro
  ```
- Elimina bloques de columnas eliminadas
- Agrega bloques de columnas nuevas que quedaron en `DIMENSION_FILTERS`

### A6 — Revisar vistas por referencias rotas

Lee los archivos `view_*.py` del módulo. Busca hardcodes de columnas eliminadas.
- Si hay columna equivalente en `agregadas` → reemplaza
- Si no → comenta con `# MIGRACIÓN: columna '<nombre>' eliminada — revisar lógica`

### A7 — Generar query homologada

Ejecuta los pasos de la sección **HOMOLOGACIÓN DE QUERIES**:

- Crear/actualizar el archivo
  `queries_homologadas/<modulo>/<nombre_fuente>.sql`.
- Aplicar el encabezado con `Modulo`, `Parquet`, `Consumidores`, `Origen actual`, `Grano final`.
- Marcar las CTEs cliente-específicas con `-- [CLIENTE-ESPECIFICO]`.
- Reestructurar el SELECT final como `CONTRATO FINAL — [ESTANDAR]`, con
  casts explícitos, agrupación por secciones y **sin fillers**.
- Actualizar `queries_homologadas/README.md` (índice y contrato del módulo).
- Mostrar el checklist de homologación al usuario.

### A8 — Assets del cliente

Ejecuta los pasos de la sección **ASSETS Y BRANDING DEL CLIENTE** al final de este skill
y muestra el checklist de estado al usuario.

### A9 — Resumen Ruta A

```
✅ Migración completada — módulo <nombre>

Archivos modificados:
- <modulo>/consolidar_parquets.py
- <modulo>/data.py
- <modulo>/logic.py
- <modulo>/__init__.py
[+ vistas con referencias corregidas]
- queries_homologadas/<modulo>/<nombre_fuente>.sql
- queries_homologadas/README.md

Columnas agregadas: [lista o "ninguna"]
Columnas eliminadas: [lista o "ninguna"]
[TODOs pendientes si los hay]

📋 Homologación de query:
[checklist de homologación aquí]

📋 Assets del cliente:
[checklist de assets aquí]

Siguiente paso: "Actualizar Parquet" en el sidebar del módulo
o: python -m <carpeta_modulo>.consolidar_parquets
```

---

## ═══════════════════════════════════════════════
## RUTA B — Múltiples fuentes
## ═══════════════════════════════════════════════

Para cada query de entrada determina si es **reemplazo** o **fuente nueva**:
- **Reemplazo**: el nombre lógico coincide con una fuente ya existente en el inventario
- **Nueva fuente**: no hay coincidencia → extiende la arquitectura

Para reemplazos aplica Ruta A sobre esa fuente.
Para fuentes nuevas aplica los pasos B1–B5.

### B0 — Confirmar plan con el usuario

Muestra antes de hacer cambios:
```
Plan de migración — módulo <nombre>:
  <nombre_fuente_1>  →  REEMPLAZO de <QUERY_CONST_existente>
  <nombre_fuente_2>  →  NUEVA FUENTE (extiende la arquitectura)
¿Confirmas? (sí/no o correcciones)
```

### B1 — Actualizar `consolidar_parquets.py` (fuentes nuevas)

**Agregar constante de query** (después de las existentes):
```python
QUERY_<NOMBRE_UPPER> = """
<query aquí>
"""
```

**Actualizar import de `data.py`**: añadir `<NOMBRE_UPPER>_PARQUET`.

**Actualizar `actualizar_todo()`** para ejecutar todas las queries.
Si actualmente devuelve `int`, cambia a `dict[str, int]`:
```python
def actualizar_todo():
    engine = get_sqlalchemy_engine()
    if not engine:
        raise ConnectionError("No se pudo crear el engine de BD.")

    resultados = {}
    try:
        # fuente existente (mantén la lógica actual, solo envuélvela en el dict)
        df_existente = pd.read_sql(QUERY_EXISTENTE.replace('%', '%%'), engine)
        df_existente.to_parquet(EXISTENTE_PARQUET)
        resultados["<nombre_existente>"] = len(df_existente)

        # fuente nueva
        df_nueva = pd.read_sql(QUERY_<NOMBRE_UPPER>.replace('%', '%%'), engine)
        df_nueva.to_parquet(<NOMBRE_UPPER>_PARQUET)
        resultados["<nombre_nuevo>"] = len(df_nueva)

        return resultados
    finally:
        engine.dispose()
```

### B2 — Actualizar `data.py` (fuentes nuevas)

**Agregar constante de parquet**:
```python
<NOMBRE_UPPER>_PARQUET = CACHE_DIR / "<nombre>_cache.parquet"
```

**Agregar `build_demo_<nombre>()`**:
- 24 meses de datos sintéticos con todas las columnas del SELECT final
- Numéricos → valores crecientes razonables; categóricos → `"DEMO_A"`, `"DEMO_B"`
- Añade `# TODO: ajustar valores demo para <nombre>` al inicio de la función

**Actualizar `load_all_data()`**:
```python
<nombre>, n_warn = _read_parquet(<NOMBRE_UPPER>_PARQUET, "<nombre>")
# añadir n_warn a load_warnings
# si <nombre>.empty: <nombre> = build_demo_<nombre>()
# añadir "<nombre>": <nombre> al dict de retorno
```

### B3 — Actualizar `logic.py` (fuentes nuevas)

Evalúa columnas de las nuevas fuentes para `DIMENSION_FILTERS`.
Si una nueva fuente tiene columnas de dimensión filtrable, agrégalas.
Usa el prefijo del módulo para el nombre de la clave de session_state.

### B4 — Actualizar `__init__.py` (fuentes nuevas)

**Botón de actualización**: si `actualizar_todo()` pasó de `int` a `dict`,
actualiza el handler:
```python
resultados = consolidar.actualizar_todo()
resumen = ", ".join(f"{k}: {v:,}" for k, v in resultados.items())
st.toast(f"Parquets actualizados — {resumen}", icon="✅")
```

**`_parquet_last_updated()`**: usa el `max()` de los mtime de todos los parquets.

Agrega los imports necesarios para los nuevos `*_PARQUET`.

Agrega filtros de sidebar para las columnas de dimensión de las fuentes nuevas.

### B5 — Vistas (fuentes nuevas)

Las vistas existentes no se tocan salvo que el usuario lo indique.
Informa al usuario cómo consumir la nueva fuente:
```
ℹ️  Nueva fuente "<nombre>" disponible como context["<nombre>"].
    Para usarla en una vista: df = context.get("<nombre>", pd.DataFrame())
```

### B6 — Generar queries homologadas

Ejecuta los pasos de la sección **HOMOLOGACIÓN DE QUERIES** **una vez por cada
fuente procesada** (tanto reemplazos como fuentes nuevas):

- Crear/actualizar `queries_homologadas/<modulo>/<nombre_fuente>.sql` por cada
  fuente.
- Aplicar el encabezado con `Modulo`, `Parquet`, `Consumidores`,
  `Origen actual`, `Grano final` (una entrada distinta por fuente).
- Marcar las CTEs cliente-específicas con `-- [CLIENTE-ESPECIFICO]`.
- Reestructurar cada SELECT final como `CONTRATO FINAL — [ESTANDAR]`, con
  casts explícitos, agrupación por secciones y **sin fillers**.
- Actualizar `queries_homologadas/README.md`: una fila del índice por cada
  fuente nueva y/o actualización del contrato del módulo.
- Mostrar el checklist de homologación (consolidado para todas las fuentes).

### B7 — Assets del cliente

Ejecuta los pasos de la sección **ASSETS Y BRANDING DEL CLIENTE** al final de este skill
y muestra el checklist de estado al usuario.

### B8 — Resumen Ruta B

```
✅ Migración multi-fuente completada — módulo <nombre>

Fuentes procesadas:
  <fuente_1>  →  reemplazo   [N cols agregadas, M eliminadas]
  <fuente_2>  →  nueva fuente  [N columnas]

Archivos modificados:
- <modulo>/consolidar_parquets.py
- <modulo>/data.py
- <modulo>/logic.py
- <modulo>/__init__.py
[+ vistas si se modificaron]
- queries_homologadas/<modulo>/<fuente_1>.sql
- queries_homologadas/<modulo>/<fuente_2>.sql
- queries_homologadas/README.md

[TODOs pendientes si los hay]

Siguiente paso: "Actualizar Parquets" en el sidebar
o: python -m <carpeta_modulo>.consolidar_parquets

Fuentes nuevas disponibles:
  context["<nombre>"]  →  DataFrame listo para usar en vistas

📋 Homologación de queries:
[checklist de homologación aquí — una entrada por fuente]

📋 Assets del cliente:
[checklist de assets aquí]
```

---

## NOTAS TRANSVERSALES

### Encoding SQL
Verifica caracteres especiales (`°`, `Ñ`, tildes) al leer archivos `.sql`.
PostgreSQL puede almacenar columnas con mayúsculas especiales (`aÑo`, `N° CUENTA`).
Si el archivo tiene `Â°` o `Ã±` en lugar de `°` o `ñ`, corrígelo antes de copiar.

### `%` en SQL
La constante Python debe tener `%` simples. `actualizar_todo()` aplica
`.replace('%', '%%')` al llamar a `pd.read_sql()`. No dupliques el escape.

### Demo data
Si una columna nueva no tiene valor demo obvio, `""` o `0.0` es suficiente.
El objetivo es que el DataFrame tenga la columna para evitar `KeyError`.

### No migres lógica de negocio
Si una query cambia la semántica de una columna existente (ej: `saldo` pasa de
bruto a neto), notifica al usuario sin cambiar la lógica de las vistas.

### Columnas mínimas por tipo de vista
Si el módulo tiene vistas de Balance / EERR / Resumen, la fuente principal
necesita: `anio`, `mes`, `saldo`, `PPTO`, `Estado_Financiero`, columnas de
jerarquía IFRS (`Nivel_1_IFRS`, `Nivel_2_IFRS`, `Nivel_3_IFRS`) y columnas de
plan de cuentas (`pcdesc_1`, `pcdesc_2`, `cuenta_contable`).
Si el módulo tiene otro tipo de vistas, verifica qué columnas usan leyendo los
archivos `view_*.py` antes de advertir sobre columnas "obligatorias".
