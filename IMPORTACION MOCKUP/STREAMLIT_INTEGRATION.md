# Guía de integración — Interwins Design System → Streamlit

Esta guía concentra las recomendaciones prácticas para llevar el look & feel del mockup (`ui_kits/dashboard/index.html`) a tu app de Streamlit existente (base: `Dashboard-responsivo/app.py`). Está escrita con foco en ir **incremental**: puedes aplicar las secciones en orden, desplegar, y medir impacto visual antes de avanzar a la siguiente.

---

## 0. Filosofía

El mockup React + HTML no reemplaza Streamlit. Se traduce en **tres capas**:

| Capa | Qué porta | Cómo |
|---|---|---|
| **Tokens** (colores, tipografía, radios, sombras) | Variables CSS del design system | `st.markdown("<style>…</style>", unsafe_allow_html=True)` o archivo `.streamlit/style.css` |
| **Widgets nativos** (KPIs simples, tablas, charts) | Componentes de Streamlit + Plotly | `st.metric`, `st.dataframe` con `column_config`, `plotly_chart` |
| **Interacciones vivas** (flip cards, hovers elaborados, toggle dark, módulo selector) | HTML+CSS+JS embebido | `streamlit.components.v1.html(...)` en iframe aislado |

La regla: **todo lo que se pueda hacer con Plotly + CSS global, se hace nativo.** Sólo las piezas con estado local visual (flips, hovers 3D, toggles animados) usan `components.v1.html`.

---

## 1. Arquitectura modular (core vs módulos)

Tu repo ya separa `app.py` + `Modulo_financiero/` + `Modulo_comercial/` + `Modulo_ventas_salud/`. La regla de oro:

> **Toda la visual vive en el core. Los módulos sólo entregan datos y widgets, nunca definen colores ni tipografías.**

Cuando agregues o quites un módulo, no debe tocarse un solo byte de CSS. La paleta no se rompe. El sidebar no se desordena.

### 1.1 Estructura de carpetas recomendada

```
Dashboard-responsivo/
├── app.py                          ← orquestador (sólo layout + registry de módulos)
├── core/                           ← NUEVA — design system + shared primitives
│   ├── __init__.py
│   ├── theme.py                    ← carga CSS, setea data-theme, expone tokens Python
│   ├── components.py               ← flip_card, kpi_metric, export_menu, header_band…
│   ├── charts.py                   ← template Plotly + helpers (gauge, dual_axis_bar, etc.)
│   ├── registry.py                 ← registro de módulos activos
│   └── assets/
│       ├── colors_and_type.css     ← copiar desde este design system
│       ├── logo_mark.svg
│       └── logo_wordmark.svg
├── Modulo_financiero/
│   ├── __init__.py                 ← expone `register(app)` — ver abajo
│   ├── data.py                     ← queries
│   ├── logic.py                    ← cálculos de KPIs
│   ├── view_resumen.py             ← render de tab
│   ├── view_eerr.py
│   └── …
├── Modulo_comercial/               ← mismo patrón
├── Modulo_ventas_salud/            ← mismo patrón
└── requirements.txt
```

### 1.2 Contrato que cada módulo debe cumplir

Cada módulo expone **un solo objeto** con una forma fija. Nada más lo ve `app.py`:

```python
# Modulo_financiero/__init__.py
from dataclasses import dataclass, field
from typing import Callable, List

@dataclass
class TabSpec:
    label: str                           # "Resumen Ejecutivo"
    render: Callable[[dict], None]       # recibe ctx, escribe con st.*
    icon: str = "📊"

@dataclass
class ModuleSpec:
    key: str                             # "financiera"
    label: str                           # "Financiera"
    icon: str                            # "💰"
    order: int = 100                     # orden en el sidebar (menor = arriba)
    tabs: List[TabSpec] = field(default_factory=list)
    filters: Callable[[dict], dict] = None   # opcional: filtros específicos del módulo

def get_module() -> ModuleSpec:
    from .view_resumen import render_resumen
    from .view_eerr    import render_eerr
    from .view_balance import render_balance
    from .view_glosas  import render_glosas
    return ModuleSpec(
        key="financiera",
        label="Financiera",
        icon="💰",
        order=10,
        tabs=[
            TabSpec("Resumen Ejecutivo", render_resumen, "📊"),
            TabSpec("Estado de Resultados", render_eerr, "📑"),
            TabSpec("Balance", render_balance, "⚖️"),
            TabSpec("Glosas", render_glosas, "📝"),
        ],
    )
```

Cada `view_*.py` **no toca CSS, no elige colores, no define tipografías**. Usa sólo primitives de `core/components.py` y `core/charts.py`:

```python
# Modulo_financiero/view_eerr.py
from core.components import header_band, export_menu, pill
from core.charts import apply_theme
import streamlit as st

def render_eerr(ctx: dict):
    header_band("Estado de Resultados",
                "EE.RR consolidado — Real vs Presupuesto.")
    col_chips, col_export = st.columns([4, 1])
    with col_chips:
        pill("Corte: Mar-2026", variant="primary")
        pill("Moneda: CLP millones", variant="soft")
        pill("Vista: Acumulado YTD", variant="ghost")
    with col_export:
        export_menu(
            scope_label="EE.RR",
            formats=["xlsx", "pdf"],
            on_export=lambda fmt: ctx["services"].export_eerr(fmt),
        )
    # ... tabla, charts, etc. — siempre vía helpers de core
```

### 1.3 Registry dinámico en `app.py`

`app.py` descubre módulos en tiempo de arranque. **Agregar o quitar un módulo = una línea.**

```python
# app.py
import streamlit as st
from core.theme import inject_theme, theme_toggle
from core.registry import discover_modules, render_sidebar, render_tabs

st.set_page_config(page_title="Interwins", layout="wide", page_icon="💠")
inject_theme()            # carga colors_and_type.css + fuentes + data-theme

# 1. Descubrir módulos — lee cada Modulo_*/__init__.py
modules = discover_modules([
    "Modulo_financiero",
    "Modulo_comercial",
    "Modulo_ventas_salud",
    # agregar aquí nuevos módulos; quitar = borrar línea
])

# 2. Sidebar con selector de módulo + filtros globales
active_key, filters = render_sidebar(modules)

# 3. Tabs del módulo activo
active_module = modules[active_key]
render_tabs(active_module, ctx={"filters": filters, "services": my_services})

# 4. Toggle dark/light (flota top-right)
theme_toggle()
```

### 1.4 `core/registry.py` — implementación mínima

```python
import importlib
import streamlit as st
from typing import List, Dict

def discover_modules(package_names: List[str]) -> Dict[str, "ModuleSpec"]:
    mods = {}
    for name in package_names:
        try:
            pkg = importlib.import_module(name)
            spec = pkg.get_module()
            mods[spec.key] = spec
        except (ImportError, AttributeError) as e:
            st.warning(f"Módulo '{name}' no cargó: {e}")
    # Ordenar por .order
    return dict(sorted(mods.items(), key=lambda kv: kv[1].order))

def render_sidebar(modules):
    from streamlit_option_menu import option_menu
    with st.sidebar:
        st.image("core/assets/logo_wordmark.svg", width=140)
        st.markdown("---")
        keys = list(modules.keys())
        labels = [f"{modules[k].icon} {modules[k].label}" for k in keys]
        selected_label = option_menu(
            menu_title="Sección",
            options=labels,
            default_index=0,
            styles={...},     # tus estilos del CSS core
        )
        active_key = keys[labels.index(selected_label)]

        # Filtros globales (fam, proveedor, tiering…)
        st.markdown("### Filtros Globales")
        filters = {
            "familia":   st.multiselect("Familia", [...]),
            "proveedor": st.selectbox("Proveedor", [...]),
            "tiering":   st.selectbox("Tiering", [...]),
        }
        # Filtros específicos del módulo (si los define)
        if modules[active_key].filters:
            filters.update(modules[active_key].filters(filters))
    return active_key, filters

def render_tabs(module, ctx):
    tab_labels = [f"{t.icon} {t.label}" for t in module.tabs]
    tabs = st.tabs(tab_labels)
    for tab, spec in zip(tabs, module.tabs):
        with tab:
            spec.render(ctx)
```

### 1.5 Qué cambia si agregas un módulo nuevo

1. Crear carpeta `Modulo_nuevo/` con `__init__.py` que exporte `get_module()`.
2. Agregar `"Modulo_nuevo"` a la lista en `app.py`.
3. **Nada más.** El sidebar, las tabs, el theme, los tokens — todo se auto-ajusta.

### 1.6 Qué cambia si quitas un módulo

1. Borrar la línea `"Modulo_quitado"` de `app.py`.
2. (Opcional) Borrar la carpeta.
3. **Nada más.** El sidebar re-renderiza con los que quedan.

### 1.7 Principios de hygiene

- ❌ **Ningún `view_*.py` debe contener strings de color hex (`#0A1261`, etc.).** Si lo necesitas, es un nuevo token en `core/theme.py`.
- ❌ **Ningún `view_*.py` debe llamar `st.markdown("<style>…</style>")`.** Si una vista necesita un tweak visual, el tweak va al CSS del core con un `data-view="eerr"` selector.
- ✅ **Todos los charts pasan por `core.charts.apply_theme()`** (o usan el template `pio.templates.default = "interwins"` que se setea al arranque).
- ✅ **Todos los textos tipográficos usan las clases del core** (`.iw-h1`, `.iw-metric-label`, etc.) o los `data-testid` de Streamlit que ya están targetados en el CSS.
- ✅ **Cualquier helper reusable entre módulos** (ej. `render_period_selector`) vive en `core/components.py`.

---

## 2. Scaffold `core/theme.py` y `core/components.py`

Estos dos archivos son la **única superficie** que los módulos tocan para lo visual.

### 2.1 `core/theme.py` — inyección del design system

```python
"""Theme loader — se llama UNA vez al inicio de app.py."""
from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).parent / "assets"

@st.cache_resource
def _load_css() -> str:
    return (ASSETS / "colors_and_type.css").read_text(encoding="utf-8")

def inject_theme():
    """Carga CSS global + fuentes + overrides para widgets Streamlit."""
    st.markdown(
        f'<style>{_load_css()}</style>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    # Setea data-theme inicial desde session_state (o 'light' default)
    theme = st.session_state.get("iw_theme", "light")
    st.markdown(
        f'<script>document.documentElement.setAttribute("data-theme","{theme}");</script>',
        unsafe_allow_html=True,
    )

def theme_toggle():
    """Toggle flotante top-right. Llamar una sola vez, al final de app.py."""
    col = st.columns([10, 1])[1]
    with col:
        is_dark = st.toggle("🌙", value=st.session_state.get("iw_theme") == "dark",
                            key="_theme_toggle", label_visibility="collapsed")
    new_theme = "dark" if is_dark else "light"
    if st.session_state.get("iw_theme") != new_theme:
        st.session_state.iw_theme = new_theme
        st.rerun()

# Tokens Python — úsalos en charts Plotly / lógica de color
TOKENS = {
    "navy":    "#0A1261",
    "accent":  "#3b82f6",
    "ink":     "#14233b",
    "slate":   "#64748b",
    "grid":    "#e2e8f0",
    "success": "#2bb673",
    "danger":  "#ef4444",
    "warning": "#f59e0b",
}
```

### 2.2 `core/components.py` — primitives reutilizables

```python
"""Componentes visuales compartidos por todos los módulos."""
import streamlit as st
import streamlit.components.v1 as components
from .theme import TOKENS

def header_band(title: str, description: str = ""):
    """Banner navy con título + descripción. Reemplaza <HeaderBand/> del mockup."""
    st.markdown(f"""
    <div class="iw-header-band">
      <h2 class="iw-header-title">{title}</h2>
      {f'<p class="iw-header-desc">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)

def pill(text: str, variant: str = "primary"):
    """Píldora informativa. variant: primary | soft | ghost."""
    st.markdown(f'<span class="iw-pill iw-pill--{variant}">{text}</span>',
                unsafe_allow_html=True)

def kpi_metric(label: str, value: str, delta: float = None,
               meta: str = "", explanation: str = "", flip: bool = False):
    """KPI. Si flip=True usa el iframe con flip card; si no, st.metric estilizado."""
    if flip:
        _flip_card(label, value, delta, meta, explanation)
    else:
        st.metric(label, value, f"{delta:+.1f}%" if delta is not None else None)

def _flip_card(title, value, delta, meta, explanation):
    """Flip card con explicación al dorso (iframe aislado)."""
    # ... ver sección 5.2 para el HTML completo
    components.html(FLIP_CARD_HTML.format(...), height=150, scrolling=False)

def export_menu(scope_label: str, formats: list[str], on_export):
    """Dropdown Descargar [scope]. Dispara on_export(format_key)."""
    with st.popover(f"⬇ Descargar {scope_label}", use_container_width=False):
        st.caption(f"EXPORTAR {scope_label.upper()}")
        if "xlsx" in formats and st.button("📗 Excel (.xlsx)", key=f"dl_{scope_label}_xlsx",
                                           help="Tabla editable con fórmulas", use_container_width=True):
            on_export("xlsx")
        if "pdf" in formats and st.button("📕 PDF", key=f"dl_{scope_label}_pdf",
                                          help="Informe listo para imprimir", use_container_width=True):
            on_export("pdf")

def section_tabs(labels: list[str], key: str = "tab"):
    """Wrapper sobre st.tabs con persistencia en session_state."""
    return st.tabs(labels)
```

### 2.3 `core/charts.py` — template Plotly

```python
"""Template Plotly compartido. Se aplica al import."""
import plotly.graph_objects as go
import plotly.io as pio
from .theme import TOKENS

pio.templates["interwins"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=TOKENS["ink"], size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[TOKENS["accent"], TOKENS["danger"], TOKENS["success"],
                  TOKENS["warning"], "#60a5fa", TOKENS["navy"]],
        xaxis=dict(gridcolor=TOKENS["grid"], zerolinecolor=TOKENS["grid"]),
        yaxis=dict(gridcolor=TOKENS["grid"], zerolinecolor=TOKENS["grid"]),
        margin=dict(l=40, r=40, t=30, b=40),
    )
)
pio.templates.default = "interwins"

def dual_axis_bar(labels, bars, line, bar_name="", line_name=""):
    """Chart Stock vs Cobertura. Firma estable, reutilizable."""
    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=labels, y=bars, name=bar_name, marker_color=TOKENS["accent"])
    fig.add_scatter(x=labels, y=line, name=line_name, mode="lines+markers",
                    line=dict(color=TOKENS["danger"], width=2.5), secondary_y=True)
    fig.update_layout(height=320, hovermode="x unified")
    return fig

def gauge(value: float, vmin=0, vmax=100):
    """Gauge de salud 0-100 con thresholds de color."""
    return go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        gauge=dict(
            axis=dict(range=[vmin, vmax]),
            bar=dict(color=TOKENS["navy"]),
            steps=[
                dict(range=[0, 40],   color=TOKENS["danger"]),
                dict(range=[40, 70],  color=TOKENS["warning"]),
                dict(range=[70, 100], color=TOKENS["success"]),
            ],
        ),
    ))
```

### 2.4 Clases CSS que necesita el core

Extiende `colors_and_type.css` con estas clases (o crea `core/assets/components.css` y cárgalo junto):

```css
/* Header band */
.iw-header-band {
  background: linear-gradient(135deg, var(--iw-navy) 0%, #1e3a8a 100%);
  color: #fff; border-radius: var(--iw-radius-md);
  padding: 18px 24px; margin-bottom: 16px;
  box-shadow: var(--iw-shadow-card);
}
.iw-header-title { font-size: 1.4rem; font-weight: 800; margin: 0; }
.iw-header-desc  { font-size: .9rem; opacity: .85; margin: 4px 0 0; }

/* Pills */
.iw-pill {
  display: inline-block; padding: 6px 12px; border-radius: 999px;
  font-size: 11.5px; font-weight: 700; letter-spacing: .3px;
  margin-right: 8px;
}
.iw-pill--primary { background: var(--iw-navy); color: #fff; }
.iw-pill--soft    { background: #eef2ff; color: var(--iw-navy); border: 1px solid rgba(10,18,97,.12); }
.iw-pill--ghost   { background: var(--iw-surface); color: var(--iw-ink); border: 1px solid var(--iw-border-hair); }
```

---

## 3. Cargar los tokens CSS

### Opción A — inline en `app.py`
```python
from pathlib import Path
import streamlit as st

CSS = Path("colors_and_type.css").read_text(encoding="utf-8")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
```

### Opción B — archivo `.streamlit/style.css`
```python
st.markdown(
    '<link rel="stylesheet" href="colors_and_type.css">',
    unsafe_allow_html=True,
)
```

> ⚠️ Streamlit aísla algunos widgets en shadow DOM (`st.dataframe`). Esas piezas **no** heredan CSS global — ahí tienes que configurar estilos vía `column_config` o un `AgGrid`.

### Tokens clave a usar en tu CSS custom

```css
/* todos ya definidos en colors_and_type.css */
--iw-navy        /* #0A1261 — primario */
--iw-accent      /* #3b82f6 — acción */
--iw-bg          /* crema en claro, navy-charcoal en oscuro */
--iw-surface     /* fondo de card */
--iw-ink         /* texto cuerpo */
--iw-success / --iw-danger / --iw-warning  /* deltas */
```

---

## 4. Layout: sidebar, tabs, grid

| Mockup | Equivalente Streamlit |
|---|---|
| Sidebar navy (`<Sidebar/>`) | `st.sidebar` + CSS que setea `section[data-testid="stSidebar"] { background: var(--iw-navy); }` |
| Módulo selector (Financiera/Operacional) | `st.sidebar.radio` con opciones y CSS para estilizar radio buttons como pills, **o** `streamlit_option_menu.option_menu` (librería externa, 1 línea) |
| Tabs arriba (Resumen / EE.RR…) | `st.tabs(["Resumen Ejecutivo", "Estado de Resultados"])` |
| Grid de 4 KPIs | `cols = st.columns(4)` → `cols[i].metric(...)` o `cols[i].markdown(HTML)` |
| Filtros (Familia, Proveedor, Tiering) | `st.multiselect`, `st.selectbox`, `st.slider` — se estilizan con CSS sobre `div[data-testid="stMultiSelect"]` |

**Recomendación para el módulo selector:**
```python
from streamlit_option_menu import option_menu

with st.sidebar:
    modulo = option_menu(
        menu_title=None,
        options=["Financiera", "Operacional"],
        icons=["cash-coin", "box-seam"],
        default_index=0,
        styles={
            "container": {"background": "transparent", "padding": "0"},
            "nav-link": {"color": "rgba(255,255,255,.78)", "font-weight": "700"},
            "nav-link-selected": {"background": "linear-gradient(180deg, rgba(59,130,246,.35), rgba(30,58,138,.45))"},
        },
    )
```

---

## 5. KPIs — estáticos vs. flip

### 5.1 KPIs estáticos (versión simple, 100% nativa)
Usa `st.metric` y configura via CSS global. Funciona bien cuando no necesitas el efecto flip.

```python
c1, c2, c3, c4 = st.columns(4)
c1.metric("VENTA VALORIZADA", "$1.234.567", "+4.2%")
c2.metric("STOCK VALORIZADO", "$3.820.900", "-1.8%")
```

CSS para alinear con el look del mockup:
```css
[data-testid="stMetric"] {
    background: var(--iw-surface);
    border: 1px solid var(--iw-border-hair);
    border-radius: var(--iw-radius-sm);
    padding: 14px 16px;
    box-shadow: var(--iw-shadow-card);
    transition: transform .2s ease, box-shadow .2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 40px rgba(10,18,97,.14);
    border-color: rgba(59,130,246,.3);
}
[data-testid="stMetricLabel"] {
    font-size: 10.5px !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--iw-slate-500);
}
[data-testid="stMetricValue"] {
    font-size: clamp(1.5rem, 1.9vw, 2.1rem) !important;
    font-weight: 800;
    color: var(--iw-ink);
}
```

### 5.2 Flip cards (con explicación al dorso)
**Streamlit nativo no puede hacer esto.** Solución: `components.v1.html` con un mini-componente.

```python
import streamlit.components.v1 as components

FLIP_CARD_HTML = """
<style>
  .flip { perspective: 1200px; height: 132px; cursor: pointer; font-family: 'Inter', sans-serif; }
  .flip-inner { position: relative; width:100%; height:100%; transition: transform .6s cubic-bezier(.4,.2,.2,1); transform-style: preserve-3d; }
  .flip.flipped .flip-inner { transform: rotateY(180deg); }
  .flip-face { position:absolute; inset:0; backface-visibility:hidden; border-radius:14px; padding:12px 14px; border:1px solid rgba(0,0,0,.05); box-shadow:0 8px 24px rgba(31,38,135,.05); display:flex; flex-direction:column; justify-content:center; text-align:center; gap:3px; box-sizing:border-box; }
  .flip-front { background: rgba(255,255,255,.95); }
  .flip-back { background: #0A1261; color:#fff; transform: rotateY(180deg); }
  .flip-title { color:#64748b; font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:1px; }
  .flip-value { color:#14233b; font-size:1.9rem; font-weight:800; letter-spacing:-.01em; line-height:1.05; }
  .flip-delta { font-size:11.5px; font-weight:700; }
  .flip-meta { color:#94a3b8; font-size:11px; font-weight:600; }
  .flip-hint { color:#94a3b8; font-size:9.5px; font-weight:600; margin-top:3px; }
  .flip-back-title { color:#60a5fa; font-size:11.5px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
  .flip-back-desc { color:rgba(255,255,255,.92); font-size:11.5px; line-height:1.4; font-weight:500; padding:0 4px; }
</style>
<div class="flip" onclick="this.classList.toggle('flipped')">
  <div class="flip-inner">
    <div class="flip-face flip-front">
      <div class="flip-title">{title}</div>
      <div class="flip-value">{value}</div>
      <div class="flip-delta" style="color:{delta_color}">{delta_arrow} {delta}</div>
      <div class="flip-meta">{meta}</div>
      <div class="flip-hint">↻ Haz clic para ver explicación</div>
    </div>
    <div class="flip-face flip-back">
      <div class="flip-back-title">{title}</div>
      <div class="flip-back-desc">{explanation}</div>
    </div>
  </div>
</div>
"""

def flip_card(title, value, delta, meta, explanation, height=150):
    is_pos = float(delta.replace('%','').replace('+','').replace('−','-')) >= 0
    html = FLIP_CARD_HTML.format(
        title=title, value=value,
        delta=delta, delta_color="#2bb673" if is_pos else "#ef4444",
        delta_arrow="▲" if is_pos else "▼",
        meta=meta, explanation=explanation,
    )
    components.html(html, height=height, scrolling=False)

# Uso:
c1, c2, c3, c4 = st.columns(4)
with c1:
    flip_card("VENTA VALORIZADA", "$1.234.567", "+4.2%",
              "Corte: Mar-2026",
              "Facturación total del período filtrado, valorizada a precio de venta.")
```

> ⚠️ Cada `components.html` vive en su propio iframe. Es invisible para Streamlit (no puedes leer clicks en el componente desde Python). Para los flip esto no importa — es sólo visual.

---

## 6. Gráficos — Plotly con la paleta Interwins

Todos los charts del mockup tienen equivalente Plotly más potente (tooltips nativos, zoom, pan).

### 6.1 Theme Plotly compartido
Crea `iw_plotly_theme.py` y aplícalo una vez al inicio:

```python
import plotly.graph_objects as go
import plotly.io as pio

IW_NAVY   = "#0A1261"
IW_ACCENT = "#3b82f6"
IW_INK    = "#14233b"
IW_SLATE  = "#64748b"
IW_GRID   = "#e2e8f0"
IW_SUCCESS = "#2bb673"
IW_DANGER  = "#ef4444"

pio.templates["interwins"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=IW_INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[IW_ACCENT, IW_DANGER, IW_SUCCESS, "#f59e0b", "#60a5fa", IW_NAVY],
        xaxis=dict(gridcolor=IW_GRID, zerolinecolor=IW_GRID, tickfont=dict(color=IW_SLATE)),
        yaxis=dict(gridcolor=IW_GRID, zerolinecolor=IW_GRID, tickfont=dict(color=IW_SLATE)),
        legend=dict(bgcolor="rgba(255,255,255,.9)", bordercolor=IW_GRID, borderwidth=1),
        margin=dict(l=40, r=40, t=30, b=40),
    )
)
pio.templates.default = "interwins"
```

### 6.2 Stock vs Cobertura (dual-axis)
El chart que pediste hoy se hace así en Plotly:

```python
from plotly.subplots import make_subplots

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_bar(x=labels, y=stock, name="Stock (Unid.)",
            marker_color=IW_ACCENT, marker_opacity=0.88,
            text=[f"{v/1000:.0f}K" for v in stock], textposition="outside")
fig.add_scatter(x=labels, y=cobertura, name="Meses de Inv.",
                mode="lines+markers+text", line=dict(color=IW_DANGER, width=2.5),
                marker=dict(size=7, color=IW_DANGER),
                text=[f"{v:.1f}" for v in cobertura], textposition="top center",
                secondary_y=True)
fig.update_yaxes(title_text="Unidades en Bodega", secondary_y=False, color=IW_NAVY)
fig.update_yaxes(title_text="Meses de Inventario", secondary_y=True, color=IW_DANGER)
fig.update_layout(height=320, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)
```

### 6.3 Gauge de Salud
```python
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=78,
    gauge=dict(
        axis=dict(range=[0, 100]),
        bar=dict(color=IW_NAVY),
        steps=[
            dict(range=[0, 40],  color="#ef4444"),
            dict(range=[40, 70], color="#f59e0b"),
            dict(range=[70, 100], color="#2bb673"),
        ],
    ),
))
st.plotly_chart(fig, use_container_width=True)
```

---

## 7. Tablas — Estado de Resultados

Para el EE.RR con columna de cumplimiento visual (progress bar), la mejor opción es `st.dataframe` con `column_config`:

```python
import pandas as pd

df = pd.DataFrame([
    {"Cuenta": "Ingresos Operacionales", "Real": 12480, "Presupuesto": 11900},
    {"Cuenta": "Costo de Venta", "Real": -7620, "Presupuesto": -7350},
    # ...
])
df["Var. Abs."]  = df["Real"] - df["Presupuesto"]
df["Var. %"]     = (df["Var. Abs."] / df["Presupuesto"].abs()) * 100
df["Cumpl."]     = df["Real"] / df["Presupuesto"] * 100

st.dataframe(
    df,
    column_config={
        "Cuenta":      st.column_config.TextColumn(width="large"),
        "Real":        st.column_config.NumberColumn(format="%,d"),
        "Presupuesto": st.column_config.NumberColumn(format="%,d"),
        "Var. Abs.":   st.column_config.NumberColumn(format="%+,d"),
        "Var. %":      st.column_config.NumberColumn(format="%+.1f%%"),
        "Cumpl.":      st.column_config.ProgressColumn(
            format="%.0f%%",
            min_value=0, max_value=120,
        ),
    },
    hide_index=True, use_container_width=True,
)
```

> Para colorear filas/celdas con lógica (filas total en navy, variaciones rojas/verdes) necesitas `st-aggrid` (`streamlit-aggrid`). Recomendado si el EE.RR es la vista principal.

---

## 8. Modo claro / oscuro

Streamlit tiene un toggle de tema **nativo** (claro/oscuro del sistema). Pero no respeta nuestras variables custom. Dos estrategias:

### 8.1 Respetar tema del sistema
```python
import streamlit as st

# Detectar tema activo de Streamlit (experimental)
theme_base = st.get_option("theme.base")  # "light" | "dark"

# Inyectar data-theme en <html>
st.markdown(
    f'<script>document.documentElement.setAttribute("data-theme", "{theme_base}");</script>',
    unsafe_allow_html=True,
)
```

Tu `.streamlit/config.toml`:
```toml
[theme]
base = "light"
primaryColor = "#3b82f6"
backgroundColor = "#fcfbf7"
secondaryBackgroundColor = "#fffdf8"
textColor = "#14233b"
font = "sans serif"
```

Y para modo oscuro (segundo config) — Streamlit cambia entre estos según preferencia del usuario.

### 8.2 Toggle custom dentro de la app
Pon un `st.toggle` en tu sidebar y setea `data-theme` vía JS:

```python
dark = st.sidebar.toggle("🌙 Modo oscuro",
                         value=st.session_state.get("dark", False))
st.session_state.dark = dark

st.markdown(f"""
<script>
  document.documentElement.setAttribute('data-theme', '{'dark' if dark else 'light'}');
</script>
""", unsafe_allow_html=True)
```

> Como el CSS de `colors_and_type.css` ya define el bloque `[data-theme="dark"]`, todos los tokens se reorganizan solos.
> ⚠️ Plotly **no** escucha `data-theme` — tienes que tener dos templates (`interwins_light`, `interwins_dark`) y elegir según el toggle.

---

## 9. Hovers, transiciones y animaciones

Streamlit no impide hovers: todo lo que inyectas con `<style>` global funciona. Consejos:

- **Prefijar siempre los selectores** con `section.main` o `[data-testid]` para no pisar el chrome de Streamlit.
- **Usa `transition` con duración baja** (.15s–.25s). Streamlit re-renderiza mucho; animaciones largas se ven cortadas.
- **Evita `transform: translateY` sobre contenedores de Streamlit** que ya tienen su propio layout absoluto — puede romper overlays de tooltips. Seguro es aplicarlo a `[data-testid="stMetric"]` y a tus propios `<div>` custom.

---

## 10. Performance — cuándo caching y cuándo no

- Carga de CSS: `@st.cache_resource` — no cambia entre sesiones.
- Data que alimenta los KPIs/charts: `@st.cache_data(ttl=300)` por 5 minutos.
- **NO cachees** el HTML de flip cards con datos inline — invalida el cache cada corrida.

```python
@st.cache_resource
def load_css():
    return Path("colors_and_type.css").read_text(encoding="utf-8")

@st.cache_data(ttl=300)
def fetch_kpis(corte):
    # query BD
    ...
```

---

## 11. Plan de migración sugerido

### Fase 0 — Crear el `core/` (1 día)
1. Crear carpeta `core/` con `theme.py`, `components.py`, `charts.py`, `registry.py`, `assets/`.
2. Copiar `colors_and_type.css` a `core/assets/`.
3. Copiar logos (`logo_mark.svg`, `logo_wordmark.svg`) a `core/assets/`.
4. Agregar `streamlit-option-menu` a `requirements.txt`.
5. Probar que `inject_theme()` carga sin errores en un `app.py` vacío.

### Fase 1 — Migrar `app.py` a orquestador (1 día)
1. Implementar `core/registry.py` (`discover_modules`, `render_sidebar`, `render_tabs`).
2. Reducir `app.py` a: `inject_theme` → `discover_modules` → `render_sidebar` → `render_tabs` → `theme_toggle`.
3. En cada `Modulo_*/` crear `__init__.py` con `get_module()` que devuelve un `ModuleSpec`.
4. Verificar que los 3 módulos aparecen en el sidebar, que al cambiar no rompe nada.

### Fase 2 — Migrar vistas a primitives (2 días)
1. Reemplazar en cada `view_*.py` los `st.markdown` de color por `header_band`, `pill`, `kpi_metric`, `export_menu`.
2. Purgar cualquier `<style>` inline de los módulos — mover al core.
3. Grep `#` (hex) en `Modulo_*/` — no debería quedar ninguno.

### Fase 3 — Charts con template (1 día)
1. `import core.charts` al inicio de `app.py` (activa template default).
2. Reemplazar creación de figuras con helpers `dual_axis_bar`, `gauge`, etc. cuando aplique.
3. Borrar colores hardcoded en Plotly de los módulos.

### Fase 4 — Componentes vivos (1–2 días)
1. Flip cards: `kpi_metric(..., flip=True)`.
2. Export menu: usar `export_menu` del core; conectar `on_export` a tus funciones reales (xlsxwriter / reportlab).
3. EE.RR con `st.dataframe` + `ProgressColumn`.

### Fase 5 — Modo oscuro (0.5 día)
1. `theme_toggle()` al final de `app.py`.
2. Verificar paleta oscura en los 3 módulos.
3. Agregar segundo template Plotly (`interwins_dark`) y switch según `session_state.iw_theme`.

### Fase 6 — Polish (continuo)
1. Hovers, transiciones, popovers.
2. Loading skeletons.
3. Responsive (< 900px).

---

## 12. Librerías Python recomendadas

| Propósito | Librería | Por qué |
|---|---|---|
| Charts | `plotly` | Dual-axis nativo, tooltips ricos |
| Tablas complejas | `streamlit-aggrid` | Celdas con color, sticky headers, ordenamiento |
| Menú lateral pill | `streamlit-option-menu` | Look cercano al mockup, 3 líneas |
| Cards vivas | `streamlit.components.v1.html` (builtin) | Cualquier HTML/CSS/JS |
| Extra components | `streamlit-extras` | Badges, loading bars, etc. |
| Caching | Builtin (`@st.cache_data`, `@st.cache_resource`) | — |

---

## 13. Checklist antes de pushear a producción

### Arquitectura
- [ ] `app.py` no contiene ningún `st.markdown("<style>...")`
- [ ] Ningún `view_*.py` contiene strings hex (`#0A1261`, etc.) — todo vía tokens
- [ ] Agregar o quitar un módulo = 1 línea en `app.py`; se probó añadiendo uno dummy
- [ ] Cada `Modulo_*/__init__.py` expone `get_module()` con `ModuleSpec`

### Visual
- [ ] CSS tokens cargados antes del primer render
- [ ] Light/Dark ambos probados (Plotly, tablas, sidebar)
- [ ] Todos los charts usan template `interwins` — ninguno con colores default de Plotly
- [ ] Nivel de servicio: verde `#2bb673` para positivos, rojo `#ef4444` para negativos — consistente
- [ ] Tipografía Inter cargada (no fallback a system-ui)
- [ ] Sidebar no se rompe en móvil (< 900px) — Streamlit la colapsa sola, pero revisa anchos de chips
- [ ] Flip cards con altura fija (iframe necesita height explícito)
- [ ] Caching: data-layer tiene TTL razonable (300s típico)
- [ ] Logos (`assets/logo_mark.svg`, `assets/logo_interwins_wordmark.svg`) reemplazados por los reales de la marca

### Funcional
- [ ] `export_menu` conectado a funciones reales (xlsxwriter / reportlab)
- [ ] `theme_toggle` persiste en session_state entre reruns

---

## 14. Referencias dentro del design system

- `README.md` — overview general y content fundamentals
- `colors_and_type.css` — tokens completos + dark mode (copia a `core/assets/`)
- `ui_kits/dashboard/` — los componentes React que puedes traducir
  - `ExportMenu.jsx` — referencia visual del dropdown de descarga (sección 2.2 lo porta a Python)
  - `ThemeToggle.jsx` — referencia del toggle dark/light (sección 2.1 lo porta)
  - `FlipCard.jsx` — referencia de las flip cards (sección 5.2 lo porta)
- `preview/` — cards de preview que muestran tokens individuales
- `SKILL.md` — instrucciones para agentes que trabajen sobre este sistema
- `assets/` — logos (`logo_mark.svg`, `logo_interwins_wordmark.svg`) — copia a `core/assets/`

---

## 15. TL;DR — orden de implementación

1. Crear `core/` con `theme.py`, `components.py`, `charts.py`, `registry.py`, `assets/`.
2. Copiar `colors_and_type.css` y logos a `core/assets/`.
3. Reducir `app.py` a 10 líneas (inject → discover → sidebar → tabs → toggle).
4. Cada `Modulo_*/` expone `get_module()` — un solo archivo `__init__.py` de 20 líneas.
5. Ninguna vista toca CSS ni colores hex. Solo primitives del core.
6. Agregar / quitar módulo = editar 1 línea en `app.py`.

---

¿Dudas o algo no traduce bien? Cuando tengas el primer port, compartilo y revisamos deltas.
