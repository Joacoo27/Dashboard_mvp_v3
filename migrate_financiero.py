import os
import shutil
import re

src_dir = "/home/opdevelop/forecast_benjax/forecast_Interwins/Dashboard modulo financiero/starter_modulo_financiero"
dst_dir = "/home/opdevelop/forecast_benjax/forecast_Interwins/Dashboard_mvp_v2/Modulo_financiero"

# 1. Update logic.py
with open(f"{src_dir}/domain/financials/logic.py", "r") as f:
    logic_content = f.read()

with open(f"{src_dir}/domain/common/formatters.py", "r") as f:
    formatters_content = f.read()

demo_funcs = """
def build_demo_contable() -> pd.DataFrame: return pd.DataFrame()
def build_demo_glosas() -> pd.DataFrame: return pd.DataFrame()
"""

new_logic_content = logic_content + "\n" + formatters_content + "\n" + demo_funcs

with open(f"{dst_dir}/logic.py", "w") as f:
    f.write(new_logic_content)

# 2. Update views
views_to_copy = ["view_resumen.py", "view_eerr.py", "view_eeff_integral.py", "view_glosas.py"]

for view in views_to_copy:
    with open(f"{src_dir}/views/{view}", "r") as f:
        content = f.read()
    
    # Patch imports
    content = re.sub(r'from domain\.common\.formatters import (.*)', r'from .logic import \1', content)
    content = re.sub(r'from domain\.financials\.logic import (.*)', r'from .logic import \1', content)
    content = re.sub(r'from ui\.components import (.*)', r'from .ui_helpers import \1', content)
    
    dst_view = view
    if view == "view_eeff_integral.py":
        dst_view = "view_balance.py"
        
    with open(f"{dst_dir}/{dst_view}", "w") as f:
        f.write(content)

# 3. Create ui_helpers.py
ui_helpers_content = '''
import streamlit as st
import html

def render_header(title: str, description: str = "") -> None:
    st.markdown(f'<div class="header-band">{html.escape(title)}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f"<p style='color: #64748b; margin-top: -15px; margin-bottom: 25px;'>{html.escape(description)}</p>", unsafe_allow_html=True)

def render_metric_card(title: str, value: str, meta: str = "", delta: float = None, delta_label: str = "vs referencia", tooltip: str = None) -> None:
    help_icon = ""
    if tooltip:
        help_icon = f\'\'\'<span class="metric-help" tabindex="0" data-tooltip="{html.escape(tooltip, quote=True)}">i</span>\'\'\'

    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        color = "#2bb673" if delta >= 0 else "#ef4444"
        delta_html = f\'\'\'<div class="metric-delta" style="color:{color};"><span style="font-size:12px;">{arrow} {abs(delta):.1f}% {html.escape(delta_label)}</span></div>\'\'\'

    card_html = f\'\'\'
    <div class="metric-card">
        {help_icon}
        <div class="metric-title">{html.escape(title)}</div>
        <div class="metric-value">{html.escape(str(value))}</div>
        {delta_html}
        <div class="metric-meta">{html.escape(meta)}</div>
    </div>
    \'\'\'
    st.markdown(card_html, unsafe_allow_html=True)
'''
with open(f"{dst_dir}/ui_helpers.py", "w") as f:
    f.write(ui_helpers_content)

print("Migracion de vistas y logica completada.")
