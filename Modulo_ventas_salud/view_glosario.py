import streamlit as st

def render(df=None):
    st.markdown('<div class="header-band">Panel Glosario y Metodología Logística</div>', unsafe_allow_html=True)
    
    st.info("""
    Este panel explica los criterios matemáticos y de negocio utilizados en el Dashboard para la gestión de inventarios (Interwins).
    """)

    # --- SECCIÓN 1: ABASTECIMIENTO ---
    with st.expander("📈 NIVEL DE SERVICIO (FILL RATE %)", expanded=True):
        st.write("""
        **Definición:** Qué porcentaje de la demanda esperada podemos cubrir con el stock físico disponible hoy.
        
        **Cálculo:** `MIN(Stock Actual + Tránsito, Demanda Promedio) / Demanda Promedio`
        
        *   Si el resultado es ≥ 1 (100%), significa que tenemos suficiente para cubrir el mes sin quiebres.
        *   Si es < 1, indica el porcentaje de "llenado" de esa demanda.
        """)

    # --- SECCIÓN 2: STOCK DE SEGURIDAD ---
    with st.expander("🛡️ STOCK DE SEGURIDAD (EXISTENCIA CRÍTICA)", expanded=True):
        st.write("""
        **Definición:** El nivel de inventario mínimo para protegernos de variaciones en la demanda y retrasos de proveedores.
        
        **Cálculo:** `Z x Desviación Estándar (12m) x √ (Lead Time / 30)`
        
        *   **Z (1.65)**: Representa un objetivo de confianza del 95%.
        *   **Lead Time**: Tiempo promedio de reposición (fijado en 30 días para este análisis).
        """)

    # --- SECCIÓN 3: SOBRE-STOCK ---
    with st.expander("📦 SOBRE-STOCK Y STOCK IDEAL", expanded=True):
        st.write("""
        **Definición:** Inventario que excede los límites de eficiencia y mantiene capital inmovilizado.
        
        **Metodología:**
        1. **Stock Ideal**: `Demanda Promedio (4 meses) x Política (Slider)`.
        2. **Umbral de Alarma**: Se considera "Sobre-stock" cuando el inventario supera el *Stock Ideal + 1 mes* de demanda promedio.
        
        *   **Unidades en Exceso**: Es la resta directa entre `Stock Actual - Stock Ideal`.
        """)

    # --- SECCIÓN 4: OBSOLESCENCIA ---
    with st.expander("💀 OBSOLESCENCIA (SKUs MUERTOS)", expanded=True):
        st.write("""
        **Definición:** SKUs que no han registrado ventas en un periodo prolongado de 12 meses.
        
        **Criterio de tiempo:**
        Siguiendo la metodología oficial (`metodo_medias`), si el mes actual aún no termina (faltan > 2 días para el cierre), la comparación se hace contra el último día del mes calendario anterior.
        """)

    # --- SECCIÓN 5: ÍNDICE DE SALUD ---
    with st.expander("🌡️ ÍNDICE MASTER DE SALUD", expanded=True):
        st.write("""
        **Definición:** Un puntaje de 0 a 100 que resume la eficiencia de la bodega. Se divide en 4 pilares con peso de **25% cada uno**:
        
        1.  **Nivel de Servicio**: Premios por cobertura de demanda.
        2.  **Disponibilidad**: Penaliza si hay muchos SKUs en quiebre.
        3.  **Eficiencia**: Penaliza si el valor del Sobre-stock es alto vs el Inventario total.
        4.  **Consumo**: Penaliza la cantidad de SKUs obsoletos acumulados.
        """)
