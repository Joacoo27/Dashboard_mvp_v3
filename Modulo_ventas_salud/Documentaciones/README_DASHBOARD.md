# Dashboard Estratégico Interwins 🚀

## ⚠️ REGLA DE ORO DE DESARROLLO (LEER PRIMERO)
**ESTRICTAMENTE PROHIBIDO ALTERAR EL FORMATO VISUAL**: No se deben cambiar colores, estilos de gráficos, diseño de tarjetas, márgenes o la estética premium actual sin petición explícita del usuario. Cualquier funcionalidad nueva debe integrarse respetando el diseño visual de "Glassmorphism" y las micro-animaciones existentes.

---

## 🚀 Puesta en Marcha

## 📘 Guía de Diseño
- Revisa `DASHBOARD_DISENO_BUENAS_PRACTICAS.md` para mantener consistencia visual, jerarquía, espaciados, navegación y patrones UI del dashboard.

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el dashboard
```bash
streamlit run app.py
```

### 3. Ejecutar solo con caché local
Si ya existen archivos en `cache/`, el dashboard puede abrir sin conexión a PostgreSQL.

### 4. Habilitar actualización desde Base de Datos
1. Crear un archivo `.env` en la raíz del proyecto usando `.env.example` como plantilla.
2. Completar las credenciales reales de PostgreSQL.
3. Asegurarse de que exista el SQL de ventas que usa el ETL.

Variables esperadas:
- `HOST_DATABASE`
- `NAME_DATABASE`
- `USER_DATABASE`
- `PASW_DATABASE`
- `PORT_DATABASE`

`python-dotenv` se usa para leer esas variables desde el archivo `.env` y cargarlas en tiempo de ejecución, evitando dejar credenciales escritas directamente en el código.

---

## 🌟 Funcionalidades Principales

### 1. Panel Unificado de Venta y Stock
Integración total de métricas críticas en una sola vista continua, eliminando la navegación fragmentada.
- **Visión Estratégica**: Venta Valorizada, Stock Valorizado, Meses de Inventario y Nivel de Servicio.
- **Alertas Operacionales**: Stock en Unidades, SKUs en Quiebre, Inversión en Exceso y SKUs sin Demanda.

### 2. Indicadores de Desempeño (MoM)
Los KPIs principales incluyen indicadores de variación porcentual comparando el mes actual contra el mes anterior (▲/▼ %), permitiendo identificar tendencias rápidas de crecimiento o contracción de inventario.

### 3. Análisis de Salud de Bodega (Dual-Axis)
- **Evolución Histórica**: Gráfico de doble eje que cruza el **Stock Físico (Barras)** con los **Meses de Cobertura (Línea)**.
- **Toggle Dinámico**: Selector para visualizar tendencias de venta tanto en **Valorizado ($)** como en **Unidades**, adaptándose a perfiles financieros u operacionales.

### 4. Filtros Enriquecidos (Maestro de Productos)
Integración con la tabla maestra para filtrar por dimensiones de negocio:
- **Familia** / **Proveedor** / **Tiering** / **Tecnología**.
- Buscador inteligente de SKUs y Rango Temporal unificado.

---

## 🏗️ Arquitectura del Proyecto
- `app.py`: Orquestador principal y gestor de estado/filtros.
- `logic.py`: Motor de cálculo logística (Stock de Seguridad, NS, Quiebres).
- `data.py`: Capa de abstracción de datos y carga de Parquet.
- `view_salud.py` / `view_stock.py`: Componentes visuales modulares y reutilizables.
- `consolidar_parquets.py`: Pipeline de ETL que sincroniza PostgreSQL con caché Parquet.
- `requirements.txt`: Dependencias mínimas para ejecutar el proyecto.
- `.env.example`: Plantilla de variables de entorno para conexión a BD.

---

## ⚙️ Mantenimiento y Rendimiento
- **Pipeline de Datos**: Ejecutar `python consolidar_parquets.py` para sincronizar ventas, stock histórico y maestro de productos.
- **Caché de Alto Rendimiento**: El dashboard utiliza archivos Parquet para garantizar una respuesta instantánea (< 1s) incluso con grandes volúmenes de datos.
- **Actualización**: El botón "Actualizar desde BD" en el sidebar permite disparar el proceso de consolidación sin salir de la herramienta.
- **Ruta de Caché**: La aplicación usa la carpeta local `cache/` dentro del proyecto.

---
**Benjamin & Antigravity - Partnership Interwins 2026**
