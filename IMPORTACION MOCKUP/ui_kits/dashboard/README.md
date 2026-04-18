# Dashboard UI Kit — Interwins

Click-thru recreation of the Interwins executive dashboard (Streamlit-based in production). Components are factored as JSX modules against the real tokens in `../../colors_and_type.css`.

## Files
- `index.html` — full clickable mock. Top-nav routes between *Inventario y Ventas* and *Índice de Salud Master*; sidebar filters are live (narrow the KPI set).
- `Sidebar.jsx` — navy sidebar, logo slot, filter groups.
- `TopNav.jsx` — horizontal primary/secondary nav buttons.
- `HeaderBand.jsx` — navy band w/ 6px accent rail.
- `KpiCard.jsx` — 184px metric card w/ help tooltip + delta.
- `FlipCard.jsx` — 3D flip card variant.
- `ChartPanel.jsx` — white plotly-style container w/ section title + info capsule.
- `data.js` — sample KPIs.

## Caveats
- Real Plotly/Chart.js isn't wired — charts are semi-fake SVG area + bar visuals sized to the real proportions.
- Real data connection (Parquet / PostgreSQL ETL) omitted.
- Logo is the placeholder SVG from `assets/` until the real file is uploaded.
