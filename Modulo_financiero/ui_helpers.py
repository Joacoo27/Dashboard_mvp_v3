
import streamlit as st
import html

def render_header(title: str, description: str = "") -> None:
    st.markdown(f'<div class="header-band">{html.escape(title)}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f"<p style='color: #64748b; margin-top: -15px; margin-bottom: 25px;'>{html.escape(description)}</p>", unsafe_allow_html=True)

def render_metric_card(title: str, value: str, meta: str = "", delta: float = None, delta_label: str = "vs referencia", explanation: str = "") -> None:
    card_id = f"flip_{hash(title) & 0xffffffff}"
    
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        color = "#2bb673" if delta >= 0 else "#ef4444"
        delta_html = f'<div class="metric-delta" style="color:{color};">{arrow} {abs(delta):.1f}% {html.escape(delta_label)}</div>'

    card_html = f"""<label class="flip-card-wrapper" for="{card_id}">
<input type="checkbox" id="{card_id}">
<div class="flip-card-inner">
<div class="flip-card-front metric-card">
<div class="metric-title">{html.escape(title)}</div>
<div class="metric-value">{html.escape(str(value))}</div>
{delta_html}
<div class="metric-meta">{html.escape(meta)}</div>
<div class="card-hint">Haz clic para ver explicación</div>
</div>
<div class="flip-card-back metric-card">
<div class="flip-card-back-title">{html.escape(title)}</div>
<div class="flip-card-back-desc">{html.escape(explanation)}</div>
<div class="card-hint" style="color:rgba(255,255,255,0.6); margin-top:15px;">Haz clic para volver</div>
</div>
</div>
</label>"""
    st.markdown(card_html, unsafe_allow_html=True)

def render_info_capsule(title: str, description: str, methodology: str = "") -> None:
    """Renders a section header with an interactive info capsule."""
    capsule_id = f"capsule_{hash(title) & 0xffffffff}"
    
    html_code = f"""
    <div class="capsule-wrapper">
        <div class="chart-section-title">{html.escape(title)}</div>
        <div class="capsule-container">
            <input type="checkbox" id="{capsule_id}" class="capsule-checkbox">
            <label for="{capsule_id}" class="capsule-btn">
                <span class="capsule-icon">i</span>
            </label>
            <div class="capsule-content">
                <label for="{capsule_id}" class="capsule-close">×</label>
                <div class="capsule-title">📊 {html.escape(title)}</div>
                <div class="capsule-text">
                    <p><strong>Descripción:</strong> {html.escape(description)}</p>
                    {f'<p><strong>Metodología:</strong> {html.escape(methodology)}</p>' if methodology else ''}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
