"""Shared UI primitives used by all modules."""
import html as _html
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as _v1


# ── Flip / simple card rendered in an isolated iframe ─────────────────────────
# Using components.v1.html guarantees correct height accounting in Streamlit's
# layout engine and gives full CSS isolation (no class-name collisions).

_FONT = (
    "href='https://fonts.googleapis.com/css2?family=Inter"
    ":wght@400;500;600;700;800;900&display=swap' rel='stylesheet'"
)

# CSS template — use CARD_H as height placeholder (replaced via str.replace)
_CSS_TPL = """\
*{box-sizing:border-box;margin:0;padding:0}
html,body{overflow:hidden;background:#fcfbf7;
  font-family:'Inter',system-ui,-apple-system,sans-serif}
.ti{color:#64748b;font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.1px;line-height:1.3;width:100%}
.va{color:#14233b;font-size:clamp(1.55rem,3.5vw,2.1rem);font-weight:800;
  letter-spacing:-.01em;line-height:1.05;font-variant-numeric:tabular-nums;width:100%}
.de{font-size:12.5px;font-weight:700;width:100%}
.me{color:#94a3b8;font-size:12px;font-weight:600;width:100%}
.hi{color:#94a3b8;font-size:10px;font-weight:600;margin-top:2px;width:100%}
.ik{position:absolute;top:10px;right:10px;width:18px;height:18px;border-radius:50%;
  background:rgba(10,18,97,.08);border:1px solid rgba(10,18,97,.18);
  color:#0A1261;font-size:10px;font-weight:800;
  display:flex;align-items:center;justify-content:center;pointer-events:none}
.card{position:relative;height:CARD_H;border-radius:14px;padding:14px 14px;
  display:flex;flex-direction:column;justify-content:center;align-items:center;
  text-align:center;gap:4px;border:1px solid rgba(20,35,59,.08);
  box-shadow:0 8px 32px rgba(31,38,135,.05);background:rgba(255,255,255,.97);
  transition:box-shadow .25s,border-color .25s}
.card:hover{box-shadow:0 14px 40px rgba(10,18,97,.12);
  border-color:rgba(59,130,246,.28)}
.fw{perspective:1200px;height:CARD_H;cursor:pointer}
.fi{position:relative;width:100%;height:100%;
  transition:transform .55s cubic-bezier(.4,.2,.2,1);
  transform-style:preserve-3d}
.fw.on .fi{transform:rotateY(180deg)}
.face{position:absolute;inset:0;-webkit-backface-visibility:hidden;
  backface-visibility:hidden;border-radius:16px;padding:20px 18px;
  display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;gap:5px}
.fr{background:rgba(255,255,255,.97);border:1px solid rgba(20,35,59,.08);
  box-shadow:0 8px 32px rgba(31,38,135,.05);
  transition:box-shadow .25s,border-color .25s}
.fr:hover{box-shadow:0 14px 40px rgba(10,18,97,.12);
  border-color:rgba(59,130,246,.28)}
.bk{background:#0A1261;color:#fff;transform:rotateY(180deg);
  border:1px solid rgba(0,0,0,.1);box-shadow:0 8px 32px rgba(10,18,97,.2)}
.bk .ti{color:#60a5fa}
.bk .va{font-size:13px;line-height:1.45;font-weight:500;
  color:rgba(255,255,255,.9)}
.bk .hi{color:rgba(255,255,255,.5)}
"""

_CSS_DARK = """\
*{box-sizing:border-box;margin:0;padding:0}
html,body{overflow:hidden;background:#1b1d2a;
  font-family:'Inter',system-ui,-apple-system,sans-serif}
.ti{color:#8d93a4;font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.1px;line-height:1.3;width:100%}
.va{color:#eef1f7;font-size:clamp(1.55rem,3.5vw,2.1rem);font-weight:800;
  letter-spacing:-.01em;line-height:1.05;font-variant-numeric:tabular-nums;width:100%}
.de{font-size:12.5px;font-weight:700;width:100%}
.me{color:#6c7283;font-size:12px;font-weight:600;width:100%}
.hi{color:#6c7283;font-size:10px;font-weight:600;margin-top:2px;width:100%}
.ik{position:absolute;top:10px;right:10px;width:18px;height:18px;border-radius:50%;
  background:rgba(167,194,255,.10);border:1px solid rgba(167,194,255,.22);
  color:#a7c2ff;font-size:10px;font-weight:800;
  display:flex;align-items:center;justify-content:center;pointer-events:none}
.card{position:relative;height:CARD_H;border-radius:14px;padding:14px 14px;
  display:flex;flex-direction:column;justify-content:center;align-items:center;
  text-align:center;gap:4px;border:1px solid rgba(167,194,255,.08);
  box-shadow:0 8px 32px rgba(0,0,0,.35);background:rgba(42,45,62,0.92);
  transition:box-shadow .25s,border-color .25s}
.card:hover{box-shadow:0 14px 40px rgba(0,0,0,.45);
  border-color:rgba(122,168,255,.22)}
.fw{perspective:1200px;height:CARD_H;cursor:pointer}
.fi{position:relative;width:100%;height:100%;
  transition:transform .55s cubic-bezier(.4,.2,.2,1);
  transform-style:preserve-3d}
.fw.on .fi{transform:rotateY(180deg)}
.face{position:absolute;inset:0;-webkit-backface-visibility:hidden;
  backface-visibility:hidden;border-radius:16px;padding:20px 18px;
  display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;gap:5px}
.fr{background:rgba(42,45,62,0.92);border:1px solid rgba(167,194,255,.08);
  box-shadow:0 8px 32px rgba(0,0,0,.35);
  transition:box-shadow .25s,border-color .25s}
.fr:hover{box-shadow:0 14px 40px rgba(0,0,0,.45);
  border-color:rgba(122,168,255,.22)}
.bk{background:#0d1545;color:#fff;transform:rotateY(180deg);
  border:1px solid rgba(122,168,255,.15);box-shadow:0 8px 32px rgba(0,0,0,.45)}
.bk .ti{color:#60a5fa}
.bk .va{font-size:13px;line-height:1.45;font-weight:500;
  color:rgba(255,255,255,.9)}
.bk .hi{color:rgba(255,255,255,.5)}
"""

_FLIP_HTML = """\
<!doctype html><html><head><meta charset="utf-8">
<link {FONT}><style>{CSS}</style></head>
<body>
<div class="fw" onclick="this.classList.toggle('on')">
  <div class="fi">
    <div class="face fr">
      {IK}
      <div class="ti">{T}</div>
      <div class="va">{V}</div>
      {D}
      <div class="me">{M}</div>
      <div class="hi">&#8635; Haz clic para ver explicaci&#xF3;n</div>
    </div>
    <div class="face bk">
      <div class="ti">{T}</div>
      <div class="va">{DESC}</div>
      <div class="hi">&#8635; Haz clic para volver</div>
    </div>
  </div>
</div>
</body></html>"""

_SIMPLE_HTML = """\
<!doctype html><html><head><meta charset="utf-8">
<link {FONT}><style>{CSS}</style></head>
<body>
<div class="card">
  {IK}
  <div class="ti">{T}</div>
  <div class="va">{V}</div>
  {D}
  <div class="me">{M}</div>
</div>
</body></html>"""


def render_header(title: str, description: str = "") -> None:
    st.markdown(
        f'<div class="header-band">{_html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    if description:
        st.markdown(
            f"<p class='iw-header-desc'>{_html.escape(description)}</p>",
            unsafe_allow_html=True,
        )


def render_metric_card(
    title: str,
    value: str,
    meta: str = "",
    delta: float = None,
    delta_label: str = "vs referencia",
    explanation: str = "",
    tooltip: str = None,
    flip_desc: str = None,
    height: int = 132,
) -> None:
    """KPI card rendered in an isolated iframe.

    If explanation or flip_desc is provided the card flips on click to show
    the description on the back.
    """
    desc = flip_desc or explanation

    delta_html = ""
    if delta is not None:
        arrow = "&#9650;" if delta >= 0 else "&#9660;"
        color = "#2bb673" if delta >= 0 else "#ef4444"
        delta_html = (
            f'<div class="de" style="color:{color};">'
            f"{arrow} {abs(delta):.1f}%&nbsp;{_html.escape(delta_label)}"
            f"</div>"
        )

    ik_html = '<div class="ik">i</div>' if (desc or tooltip) else ""
    is_dark = st.session_state.get("iw_dark_mode", False)
    css = (_CSS_DARK if is_dark else _CSS_TPL).replace("CARD_H", f"{height}px")

    if desc:
        html_out = _FLIP_HTML.format(
            FONT=_FONT, CSS=css, IK=ik_html,
            T=_html.escape(title),
            V=_html.escape(str(value)),
            M=_html.escape(meta),
            D=delta_html,
            DESC=_html.escape(desc),
        )
    else:
        html_out = _SIMPLE_HTML.format(
            FONT=_FONT, CSS=css, IK=ik_html,
            T=_html.escape(title),
            V=_html.escape(str(value)),
            M=_html.escape(meta),
            D=delta_html,
        )

    _v1.html(html_out, height=height, scrolling=False)


def render_info_capsule(title: str, description: str, methodology: str = "") -> None:
    capsule_id = f"capsule_{abs(hash(title)) & 0xFFFFFF}"
    meth_html = (
        f'<p><strong>Metodolog&#xED;a:</strong> {_html.escape(methodology)}</p>'
        if methodology else ""
    )
    html_code = f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
  <div class="chart-section-title" style="margin-bottom:0;">{_html.escape(title)}</div>
  <div class="capsule-wrapper">
    <input type="checkbox" id="{capsule_id}" class="capsule-checkbox">
    <label for="{capsule_id}" class="capsule-btn" data-tooltip-text="&#128202; Ver detalle">i</label>
    <div class="capsule-content">
      <label for="{capsule_id}" class="capsule-close">&#215;</label>
      <div class="capsule-title">&#128202; {_html.escape(title)}</div>
      <div class="capsule-text">
        <p>{_html.escape(description)}</p>
        {meth_html}
      </div>
    </div>
  </div>
</div>"""
    st.markdown(html_code, unsafe_allow_html=True)


def render_pills(pills: list[tuple[str, str]]) -> None:
    """Render context pills. pills = [(label, variant), ...]
    variant: 'primary' | 'soft' | 'ghost'
    """
    items = "".join(
        f'<span class="iw-pill iw-pill--{v}">{_html.escape(l)}</span>'
        for l, v in pills
    )
    st.markdown(f'<div class="iw-pill-row">{items}</div>', unsafe_allow_html=True)


def render_sidebar_brand(logo_path: str | Path | None, title: str = "Interwins", subtitle: str = "PANEL EJECUTIVO") -> None:
    logo_markup = '<div class="iw-sidebar-logo-fallback">iw</div>'
    if logo_path:
        path = Path(logo_path)
        if path.exists() and path.suffix.lower() == ".svg":
            logo_markup = path.read_text(encoding="utf-8")

    st.sidebar.markdown(
        (
            '<div class="iw-sidebar-brand">'
            f'<div class="iw-sidebar-mark">{logo_markup}</div>'
            '<div class="iw-sidebar-brand-copy">'
            f'<div class="iw-sidebar-brand-title">{_html.escape(title)}</div>'
            f'<div class="iw-sidebar-brand-subtitle">{_html.escape(subtitle)}</div>'
            '</div>'
            '</div>'
            '<div class="iw-sidebar-divider"></div>'
        ),
        unsafe_allow_html=True,
    )


def render_sidebar_section(title: str) -> None:
    st.sidebar.markdown(
        f'<div class="iw-sidebar-section-label">{_html.escape(title)}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar_divider() -> None:
    st.sidebar.markdown('<div class="iw-sidebar-divider"></div>', unsafe_allow_html=True)


def render_module_nav(modules: dict[str, object], active_key: str) -> str:
    keys = list(modules.keys())
    selected = st.sidebar.radio(
        "Sección",
        options=keys,
        index=keys.index(active_key) if active_key in keys else 0,
        format_func=lambda key: f"{modules[key].icon}  {modules[key].sidebar_label or modules[key].label}",
        key="iw_module_nav_radio",
        label_visibility="collapsed",
    )
    return selected


def render_top_nav(module, active_tab) -> str | None:
    if not module.tabs or active_tab is None:
        return None

    col_widths = [2.05]
    for tab in module.tabs:
        label_len = len(tab.label)
        col_widths.append(max(1.55, min(2.3, 1.18 + label_len * 0.04)))

    cols = st.columns(col_widths, gap="small", vertical_alignment="center")
    selected_tab = active_tab.key

    with cols[0]:
        st.markdown(
            (
                '<div class="iw-topnav-badge">'
                f'<span class="iw-topnav-badge-icon">{_html.escape(module.icon)}</span>'
                '<span class="iw-topnav-badge-kicker">SECCIÓN</span>'
                f'<span class="iw-topnav-badge-label">{_html.escape(module.sidebar_label or module.label)}</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    for col, tab in zip(cols[1:1 + len(module.tabs)], module.tabs):
        with col:
            if st.button(
                tab.label,
                key=f"iw_topnav_{module.key}_{tab.key}",
                width="stretch",
                type="primary" if tab.key == active_tab.key else "secondary",
            ):
                selected_tab = tab.key

    return selected_tab


def render_mode_indicator() -> None:
    is_dark = st.session_state.get("iw_dark_mode", False)
    label = "MODO OSCURO" if is_dark else "MODO CLARO"
    st.markdown(
        f'<div class="iw-mode-indicator">'
        f'<span class="iw-mode-label">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    def _sync_dark_mode():
        # Actualiza la variable de estado persistente desde el widget
        st.session_state["iw_dark_mode"] = st.session_state.get("_iw_dark_toggle", False)

    # El key del widget (_iw_dark_toggle) es distinto del estado real (iw_dark_mode).
    # Streamlit puede limpiar el key del widget cuando no se renderiza (navegación),
    # pero iw_dark_mode es una variable plana que nunca se limpia automáticamente.
    st.toggle(
        "Modo oscuro",
        value=is_dark,
        key="_iw_dark_toggle",
        on_change=_sync_dark_mode,
        label_visibility="collapsed",
    )


def render_kicker(text: str) -> None:
    st.markdown(f'<p class="iw-kicker">{_html.escape(text)}</p>', unsafe_allow_html=True)
