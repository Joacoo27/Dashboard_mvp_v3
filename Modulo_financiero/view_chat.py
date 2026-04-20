import streamlit as st
import pandas as pd
from datetime import datetime
from .logic import build_resumen_dashboard, format_currency, format_percent, format_ratio

def render(context: dict):
    st.subheader("💬 Chat Financiero (Beta)")
    st.info("Este chat resuelve tus dudas sobre los indicadores financieros de Interwins usando los datos actuales.")

    # Inicializar historial de chat si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Renderizar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Selector de indicador para mantener el modo "Estructurado" (Fácil de usar)
    available_ratios = [
        "EBITDA", 
        "Margen Bruto", 
        "Margen Operacional", 
        "Resultado del Ejercicio", 
        "ROA", 
        "ROE", 
        "Liquidez"
    ]
    
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_ratio = st.selectbox("¿Sobre qué indicador quieres consultar?", available_ratios, index=None, placeholder="Selecciona un indicador...")
    with col2:
        st.write("") # Espaciador
        st.write("")
        btn_send = st.button("Enviar Consulta", use_container_width=True)

    if btn_send and selected_ratio:
        # 1. Crear prompt del usuario
        user_prompt = f"¿Cómo está el {selected_ratio} en el periodo actual?"
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # Mostrar el mensaje del usuario inmediatamente
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # 2. Generar respuesta (Lógica "Light")
        with st.chat_message("assistant"):
            with st.spinner("Consultando motor financiero..."):
                response = _generate_narrative_response(selected_ratio, context)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def _generate_narrative_response(ratio_label: str, context: dict) -> str:
    """Genera una narrativa simple basada en los datos actuales."""
    df_contable = context.get("df_contable", pd.DataFrame())
    if df_contable.empty:
        return "Lo siento, no tengo datos cargados para realizar el cálculo."

    # Usamos build_resumen_dashboard para obtener valores consistentes
    resumen = build_resumen_dashboard(df_contable, df_contable)
    cards = resumen.get("cards", [])
    periodo = resumen.get("period_label", "el periodo actual")

    # Buscar la tarjeta correspondiente
    match_card = next((c for c in cards if c["title"].lower() == ratio_label.lower()), None)
    
    if not match_card:
        # Fallback para Liquidez que a veces tiene label diferente
        if "liquidez" in ratio_label.lower():
            match_card = next((c for c in cards if "liquidez" in c["title"].lower()), None)

    if not match_card:
        return f"No encontré datos específicos para el indicador **{ratio_label}** en el resumen ejecutivo."

    val = match_card["value"]
    v_type = match_card.get("value_type", "number")
    delta = match_card.get("delta", 0)
    
    # Formatear valor principal
    if v_type == "currency":
        formatted_val = format_currency(val)
    elif v_type == "percent":
        formatted_val = format_percent(val)
    elif v_type == "ratio":
        formatted_val = format_ratio(val)
    else:
        formatted_val = str(val)

    # Construir narrativa
    narrativa = f"Para **{periodo}**, el **{match_card['title']}** presenta un valor de **{formatted_val}**.\n\n"
    
    # Agregar lógica de tendencia si hay delta
    if delta != 0:
        sentido = "superior" if delta > 0 else "inferior"
        if v_type == "percent":
            diff_text = f"{abs(delta)*100:.1f} puntos porcentuales"
        else:
            diff_text = f"{abs(delta)*100:.1f}%"
            
        narrativa += f"Este resultado es un **{diff_text} {sentido}** respecto al presupuesto/meta configurada.\n\n"
    
    # Agregar nota del meta si existe
    if match_card.get("meta"):
        narrativa += f"💡 *Nota: {match_card['meta']}*"

    return narrativa
