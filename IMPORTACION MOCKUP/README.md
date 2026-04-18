# Interwins Design System

> ⚠️ **User supplied the brand name "Biwiser"** in the project brief, but the attached repo is unambiguously branded **Interwins** (title in `app.py`, `Interwins Status inventario` sidebar title, logo filenames, documentation). I've built this design system as **Interwins**. If "Biwiser" is the real brand name and "Interwins" is a placeholder in the code, rename the root folder and swap the logos — the tokens stay identical.

## What is Interwins?

Interwins is an **executive analytics dashboard** currently implemented as a Streamlit application. It's an internal BI product aimed at commercial + operations leadership, organized around three modules:

- **Módulo Ventas & Salud** — inventory + sales performance (SKU health, service level, coverage months, stock-out alerts).
- **Módulo Financiero** — executive P&L, balance sheet, KPIs (EBITDA, ROA, ROE, margins), glosas.
- **Módulo Comercial** — commercial summary (less developed; roadmap WIP).

The visual direction is **"executive glassmorphism"** — sober navy/cream palette, flip-card KPIs, frosted surfaces, Plotly charts on white with radial gradient backdrops. The brand voice is Spanish (Chile / LatAm), formal-executive.

## Sources

- **Repo:** `Joacoo27/Dashboard-responsivo` (GitHub, private)
  - `app.py` — global CSS, shared tokens, sidebar, layout
  - `DASHBOARD_DISENO_BUENAS_PRACTICAS.md` — canonical design-intent doc
  - `Modulo_financiero/Documentaciones/MODERNIZACION_UI_FINANCIERA_2026.md` — flip-card + info-capsule rationale
  - `Modulo_ventas_salud/Documentaciones/MEJORA_UI_INTERACTIVA_2026.md` — hero chart + sidebar identity
  - `assets/logo_interwins.png`, `assets/logo_interwins.jpg` — **not importable as binary**; see "Assets" caveat below.

---

## Index

| File / folder | What it is |
|---|---|
| `README.md` | This file — brand context, fundamentals, manifest |
| `colors_and_type.css` | Single source of truth for CSS tokens (colors, type, spacing, shadows) |
| `SKILL.md` | Agent Skill entry — use this design system as a skill |
| `assets/` | Logos (placeholder wordmark + mark) |
| `preview/` | Small cards that populate the Design System tab |
| `ui_kits/dashboard/` | Click-thru recreation of the executive dashboard |

---

## CONTENT FUNDAMENTALS

**Language.** All copy is **Spanish (Chile/LatAm)**. Do not translate to English. Use executive, sober register. Examples straight from the product:

- `Panel de Venta y Stock` — section title
- `Resumen Ejecutivo` — view title
- `Actualizar desde BD` — CTA
- `Sincronizando Stock y Ventas...` — progress message
- `Haz clic para ver explicación` — flip-card hint
- `Corte actual: Mar-2026` — period label
- `vs referencia`, `vs período anterior` — delta labels

**Tone & vibe.** Ejecutivo, sobrio, claro. Never casual. "Visión estratégica", "Alertas operacionales", "Consola de mando ejecutiva" are real phrases used. No second-person ("tú/usted") overuse — most copy is declarative-impersonal ("Muestra la trayectoria…", "Define la rentabilidad operativa…"). Numbers and KPIs speak first, prose explains second.

**Casing.** Title Case in Spanish for section titles (`Panel de Venta y Stock`, `Índice de Salud Master`). UPPERCASE + 1px letter-spacing is reserved for **small eyebrow labels** inside cards (`METRIC-TITLE`, `CORTE ACTUAL`). Body sentences are normal case.

**Emoji.** Used *sparingly and only in sidebar section headers* as wayfinding glyphs: `🎯 Filtros Globales`, `⚙️ Configuración Logística`, `🔄 Datos en Caché`, `📘 Guía de Diseño`. Never inside KPIs, body copy, or marketing surfaces. Treat them as icons, not decoration. The single exception is the rare `📊` inside info-capsule popovers.

**Tooltips & help.** Explain *how to read* the indicator, don't restate its name. Real example: "Este parámetro define el umbral de meses de cobertura considerado normal. Si lo subes, la app tolera más stock antes de clasificarlo como exceso…". Always second-person singular ("subes", "bajas") — the only place the informal voice surfaces.

**Deltas.** `▲ 4.2% vs mes anterior` / `▼ 2.1% vs presupuesto`. Arrow + % + reference label. Green for positive, red for negative. Never parentheses.

**Numbers.** Thousand separators = `.` (Chilean/European). Currency = CLP by default (`$1.234.567`). Percentages 1 decimal (`12,4%`). Tabular-nums everywhere monetary.

---

## VISUAL FOUNDATIONS

### Colors
- **Navy `#0A1261`** is the one true brand color. Used for: sidebar background, title bands (`header-band`), expander headers, primary buttons, table header text, flip-card reverse.
- **Accent blue `#3b82f6`** — focus rings, left-border accents, chart data series, interactive states. Never competes with navy for body dominance.
- **Deep blue `#1e3a8a`** — secondary data color, shadow tints.
- **Cream backgrounds**: app bg `#fcfbf7`, panel bg `#fffdf8`. The dashboard is *explicitly not white* — it's a warm off-white that distinguishes it from generic SaaS.
- **Slate ramp** (`#0c1e4c → #f1f5f9`) for neutrals, dividers, muted text.
- **Semantic**: success `#2bb673`, danger `#ef4444`, warning `#f59e0b`. These map 1:1 to gauge tramos (red/orange/green) and delta arrows.
- No dark mode. No color inversions. Everything is a light-surface variant.

### Type
- **Inter** is the *only* font family (400–900). No serif, no mono outside `<code>`. The repo doesn't ship TTFs — loaded from Google Fonts. 
- Executive sizes: display `clamp(1.7rem, 2.2vw, 2.2rem)`, KPI value `clamp(2.1rem, 2.7vw, 3.2rem)`, section titles 22–24px, body 14–15px, eyebrow 13–14px UPPERCASE.
- Weights trend **heavy**: body 600, titles 800, metric values 800, buttons 900. Regular 400 rarely appears.

### Backgrounds
- The signature move: two **soft radial gradients** bleeding from top-left (accent-blue 7% alpha) and top-right (deep-blue 5% alpha) into the cream panel. Defined in `--iw-app-bg`.
- **No full-bleed imagery.** No illustrations. No textures. No repeating patterns. Pure flat surfaces + those subtle radials.
- No hand-drawn illustrations.

### Animation
- Easing: mostly `ease` 0.18s for hovers, `cubic-bezier(0.4, 0.2, 0.2, 1)` 0.6s for the flip-card rotation, `cubic-bezier(0.175, 0.885, 0.32, 1.275)` with scale+rotate for the info-capsule button hover.
- One branded keyframe: `pulse-blue` — the info-capsule `i` button emits a 2s pulsing glow to invite interaction.
- Hover on cards lifts `translateY(-1px to -3px)` and intensifies shadow. No bounces elsewhere, no fades of whole sections.

### States
- **Hover**: `translateY(-1px)` + border color shifts to accent (`rgba(59,130,246,0.55)`) + deeper shadow. Buttons additionally brighten background slightly.
- **Focus-visible**: 3px ring `rgba(59,130,246,0.16)` (var `--iw-focus-ring`) stacked on the resting shadow. Explicit, always designed — never native browser outlines.
- **Active/pressed**: primary buttons don't shrink; the deeper shadow + translateY is already the press affordance.
- **Checked** (radio/nav): background → `rgba(59,130,246,0.09)`, border → accent, inner dot scales in. Active nav button = navy fill + white text.
- **Disabled**: rare; fall back to `opacity: 0.5` (no designed state in repo).

### Borders & shadows
- **Borders**: hair-thin `1px solid rgba(30, 58, 138, 0.12)` on neutral surfaces; `1.5px` on radio pucks; 6px left accent band on `header-band` and 5px on `minor-band-title` (the signature executive touch).
- **Shadow system** (all pre-named in tokens):
  - `--iw-shadow-soft` — resting cards
  - `--iw-shadow-card` — KPI cards (colder rgba tint)
  - `--iw-shadow-lift` — plotly chart containers
  - `--iw-shadow-strong` — hover lift
  - `--iw-shadow-band` — title bands (navy-tinted, heavier)
  - `--iw-shadow-navy` — primary buttons (navy, high alpha)
- No inner shadows, no neumorphism. Shadows are always downward, never colored bloom except the navy CTA.

### Radii
- `14px` small (buttons, cards inner), `16px` KPI cards, `18px` panels/expanders/table wraps, `22–24px` chart containers and shells, `999px` pills (tags, scrollbar thumb). Consistent across responsive breakpoints; on mobile some step down one tier.

### Cards
- White (`rgba(255,255,255,0.95)` + `backdrop-filter: blur(10px)`), hair border, soft shadow, 16px radius, fixed 184px height for KPI grids (so rows align across deltas). Content reserves slots: title / value / delta / meta. Even without a delta, the slot stays.
- Flip-cards: 3D rotate-Y 180°, reverse side = navy fill + white/blue-gradient type, explains the business logic of the KPI.

### Transparency & blur
- `rgba(255, 255, 255, 0.96)` on most surfaces over the gradient panel.
- `backdrop-filter: blur(10–15px)` on: header, metric cards, info-capsule popovers. Never on hero or full sections — always on components that float over the gradient.

### Layout
- Max width `1550px`, centered block container.
- Fixed sidebar (navy fill, white text) is *branding + filters only* — primary navigation is a **horizontal button row** at the top of the content area (white resting, navy active).
- KPI grids come in rows of 4 (desktop). Responsive collapses to 1-col at 768px.
- Clear vertical rhythm: 1.8rem between KPI rows, 0.35rem divider, 2.8rem before chart title rows.

### Iconography
- No icon font, no SVG sprite. Emoji as wayfinding icons in the sidebar (see Content Fundamentals). Unicode `▲ ▼` for deltas. Unicode `i` inside navy circle for help capsules. `✅` inside form-submit CTAs. `×` (close) inside popovers.
- When additional icons are needed for a new surface, prefer **Lucide** (CDN) at `stroke-width: 1.75` with `color: var(--iw-navy)`; document the substitution.

### Charts (Plotly-isms)
- `template="plotly_white"`, explicit `paper_bgcolor` and `plot_bgcolor` both `rgba(255,255,255,1)`.
- Font `#14233b`. No modebar on mobile (`display: none` ≤768px).
- Data colors use the same variables: bars `--iw-accent`, secondary series `--iw-navy`, budget line `--iw-danger` dashed, margin series `--iw-success`.
- Every chart sits inside a `[data-testid="stPlotlyChart"]`-equivalent container: white, `radius: 22px`, hair border, `--iw-shadow-lift`.

### What to avoid
- Bluish-purple gradient backgrounds
- Dark mode anywhere
- Left-border-accent-only cards with rounded corners (only the bands use left accents; never the KPI cards)
- Emoji inside body or marketing copy
- Hand-drawn SVG illustrations
- Native-looking form controls (always restyle)

---

## ICONOGRAPHY

No formal icon system ships with the repo. In practice the product gets away with a minimal vocabulary:

1. **Emoji as section wayfinding glyphs** in the sidebar: `🎯` (filters), `⚙️` (config), `🔄` (data refresh), `📘` (design guide), `📊` (chart context). Never in body copy, never in marketing, never in KPIs.
2. **Unicode primitives** for inline semantics: `▲ ▼` (deltas), `i` (help), `×` (close), `✅` (form confirm).
3. **Logo marks** — the only raster assets in `assets/`.

### Logos
- `assets/logo_interwins.png` (103 KB) and `.jpg` (29 KB) live in the source repo. **I could not import these** (binary files aren't transferable through the GitHub text importer available to me, and raw.githubusercontent.com isn't reachable from this environment).
- I've written **placeholder wordmark + mark SVGs** at `assets/logo_interwins_wordmark.svg` and `assets/logo_mark.svg` using the brand navy + the "iw" monogram. **Replace these with the real files as soon as possible** — preferably by uploading them via the project import menu.

### Recommended additions (if needed for new work)
- **Lucide** (`https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/…`) — stroke-1.75, color `var(--iw-navy)`. Closest match to the minimal executive tone. Flag any use as a substitution.
- Avoid Heroicons solid / Font Awesome / Material — too decorative for this brand.

---

## Manifest

```
Interwins Design System/
├── README.md                     ← you are here
├── SKILL.md                      ← Agent Skill entry
├── colors_and_type.css           ← all tokens
├── assets/
│   ├── logo_interwins_wordmark.svg   (placeholder)
│   └── logo_mark.svg                 (placeholder)
├── preview/                      ← Design System tab cards
│   ├── colors-brand.html
│   ├── colors-neutrals.html
│   ├── colors-semantic.html
│   ├── type-scale.html
│   ├── type-weights.html
│   ├── spacing-radii.html
│   ├── shadows.html
│   ├── button-primary.html
│   ├── button-secondary.html
│   ├── kpi-card.html
│   ├── flip-card.html
│   ├── header-band.html
│   ├── minor-band.html
│   ├── nav-buttons.html
│   ├── info-capsule.html
│   ├── radio-pill.html
│   ├── table-breakdown.html
│   ├── sidebar.html
│   └── logo.html
└── ui_kits/
    └── dashboard/
        ├── README.md
        ├── index.html            ← full clickable mock
        ├── Sidebar.jsx
        ├── TopNav.jsx
        ├── HeaderBand.jsx
        ├── KpiCard.jsx
        ├── FlipCard.jsx
        ├── ChartPanel.jsx
        └── data.js
```
