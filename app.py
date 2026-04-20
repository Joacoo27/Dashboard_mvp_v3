from pathlib import Path

import streamlit as st

import core.charts  # registers Plotly templates at import time
from core.components import (
    render_mode_indicator,
    render_module_nav,
    render_sidebar_brand,
    render_sidebar_divider,
    render_sidebar_mode_toggle,
    render_sidebar_section,
    render_top_nav,
)
from core.registry import discover_modules, resolve_active_module, resolve_active_tab
from core.theme import inject_theme


st.set_page_config(
    page_title="Panel de Interwins",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar antes de cualquier widget para que inject_theme y el toggle
# lean el mismo valor desde el primer render.
if "iw_dark_mode" not in st.session_state:
    st.session_state["iw_dark_mode"] = False

inject_theme()
core.charts.apply_default_template()

MODULE_PACKAGES = [
    "Modulo_ventas_salud",
    "Modulo_financiero",
    "Modulo_comercial",
]


def _query_param(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value


def _resolve_logo_asset() -> Path | None:
    root = Path(__file__).resolve().parent
    preferred = root / "IMPORTACION MOCKUP" / "assets" / "logo_mark.svg"
    if preferred.exists():
        return preferred

    for candidate in (
        root / "assets" / "logo_interwins.png",
        root / "assets" / "logo_interwins.jpg",
    ):
        if candidate.exists():
            return candidate
    return None


def _set_navigation(module_key: str, tab_key: str) -> None:
    st.query_params.clear()
    st.query_params["module"] = module_key
    st.query_params["tab"] = tab_key
    st.rerun()


def main() -> None:
    modules = discover_modules(MODULE_PACKAGES)
    active_module = resolve_active_module(modules, _query_param("module"))
    active_tab = resolve_active_tab(active_module, _query_param("tab"))

    render_sidebar_brand(_resolve_logo_asset())
    
    # Toggle de Modo en Sidebar
    sidebar_mode = render_sidebar_mode_toggle()
    render_sidebar_divider()

    if sidebar_mode == "navigation":
        render_sidebar_section("🧭 Navegación")
        selected_module_key = render_module_nav(modules, active_module.key)
    else:
        render_sidebar_section("💬 Asistente Virtual")
        _render_global_chat(active_module)
        # Mantener el módulo activo igual
        selected_module_key = active_module.key

    if selected_module_key != active_module.key:
        selected_module = modules[selected_module_key]
        next_tab = selected_module.default_tab or (selected_module.tabs[0].key if selected_module.tabs else "")
        _set_navigation(selected_module.key, next_tab)

    context = active_module.load_context() if active_module.load_context else {}
    if active_module.render_sidebar:
        maybe_context = active_module.render_sidebar(context)
        if maybe_context is not None:
            context = maybe_context

    top_nav_col, mode_col = st.columns([5.35, 1.65], vertical_alignment="center")
    with top_nav_col:
        selected_tab_key = render_top_nav(active_module, active_tab)
    with mode_col:
        render_mode_indicator()

    if selected_tab_key and active_tab and selected_tab_key != active_tab.key:
        _set_navigation(active_module.key, selected_tab_key)

    if active_tab is None:
        st.info("Este módulo aún no tiene vistas configuradas.")
        return

    active_tab.render(context)


def _render_global_chat(active_module):
    """Renderiza el chat en el sidebar con ruteo inteligente a información de módulos."""
    from Modulo_financiero.view_chat import _generate_narrative_response
    
    if "global_messages" not in st.session_state:
        st.session_state.global_messages = []

    # Contenedor de mensajes en el Sidebar
    chat_container = st.sidebar.container(height=500)
    with chat_container:
        for m in st.session_state.global_messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
    # Input - FORZADO AL SIDEBAR
    prompt = st.sidebar.chat_input("Consulta libre...")
    if prompt:
        st.session_state.global_messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Respuesta inteligente
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    p_lower = prompt.lower()
                    response = ""
                    
                    # Ruteo Lógico:
                    
                    # 1. Búsqueda en Módulo Financiero
                    fin_keywords = ["ebitda", "margen", "roa", "roe", "liquidez", "financiero", "balance", "eerr", "resultado"]
                    if any(k in p_lower for k in fin_keywords):
                        import Modulo_financiero.data as fin_data
                        fin_context = fin_data.load_all_data()
                        found_ratio = None
                        ratios = ["EBITDA", "Margen Bruto", "Margen Operacional", "Resultado del Ejercicio", "Liquidez", "ROA", "ROE"]
                        for r in ratios:
                            if r.lower() in p_lower:
                                found_ratio = r
                                break
                        
                        if found_ratio:
                            response = _generate_narrative_response(found_ratio, fin_context)
                        else:
                            response = "He analizado el **Módulo Financiero**. Mi resumen actual indica que los márgenes están en rangos operativos normales. ¿Quieres profundizar en EBITDA o Liquidez?"
                    
                    # 2. Búsqueda en Módulo Ventas Salud (si no se encontró respuesta financiera o hay match)
                    elif any(k in p_lower for k in ["salud", "paciente", "venta salud", "clínica", "hospital"]):
                        import Modulo_ventas_salud.logic as health_logic
                        # Simulación de respuesta basada en lógica de salud
                        response = "Consultando el **Módulo de Ventas Salud**. He detectado que la asertividad en pacientes de convenio está en niveles estables. ¿Deseas ver el nivel de servicio por zona?"

                    # 3. Búsqueda en Módulo Comercial
                    elif any(k in p_lower for k in ["comercial", "ventas", "producto", "cliente", "vendedor"]):
                        import Modulo_comercial.logic as com_logic
                        response = "Analizando el **Módulo Comercial**. El top de productos vendidos este mes muestra una tendencia positiva en la categoría A. ¿Necesitas el detalle por vendedor?"

                    # Fallback
                    else:
                        response = f"Actualmente estoy analizando el contexto de **{active_module.label}**. Puedo responder sobre KPIs financieros, salud o comerciales si mencionas alguno de esos temas."
                    
                    st.markdown(response)
                    st.session_state.global_messages.append({"role": "assistant", "content": response})



if __name__ == "__main__":
    main()
