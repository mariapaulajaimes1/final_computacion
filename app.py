import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Cooltivo - Sensores Urbanos",
    page_icon="🌿",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f4f9f4;
        padding: 2rem;
        font-family: 'Segoe UI', sans-serif;
        color: #2c3e50;
    }

    h1, h2, h3 {
        color: #1b5e20;
    }

    .stButton>button {
        background-color: #43a047;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1em;
        font-weight: bold;
    }

    .stDownloadButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 10px;
    }

    .stSelectbox, .stRadio, .stSlider {
        background-color: #ffffff;
        border-radius: 5px;
    }

    .stDataFrame {
        background-color: #ffffff;
        border: 1px solid #c8e6c9;
    }
    </style>
""", unsafe_allow_html=True)

# Logo + Título
col1, col2 = st.columns([1, 8])
with col1:
    # Cambia el nombre del archivo por tu logo si lo tienes
    # st.image("logo_cooltivo.png", width=70)
    st.image("https://cdn-icons-png.flaticon.com/512/684/684908.png", width=70)
with col2:
    st.title('🌿 Cooltivo - Análisis de Sensores Urbanos')
    st.markdown("Monitoreo ambiental en tiempo real: temperatura y humedad con sensores ESP32.")

# Datos de ubicación para el mapa
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783],
    'location': ['Universidad EAFIT']
})

# Mostrar mapa
st.subheader("📍 Ubicación del Sensor - Universidad EAFIT")
st.map(eafit_location, zoom=15)

# Carga de archivo
uploaded_file = st.file_uploader('📁 Selecciona tu archivo CSV', type=['csv'])

if uploaded_file is not None:
    try:
        df1 = pd.read_csv(uploaded_file)
        column_mapping = {
            'temperatura {device="ESP32", name="Sensor 1"}': 'temperatura',
            'humedad {device="ESP32", name="Sensor 1"}': 'humedad'
        }
        df1 = df1.rename(columns=column_mapping)
        df1['Time'] = pd.to_datetime(df1['Time'])
        df1 = df1.set_index('Time')
        st.success("✅ Datos cargados correctamente")

        # Tabs principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌡️ Visualiza tus Datos Ambientales",
            "📐 Análisis Estadístico Rápido",
            "🎛️ Filtra y Descarga",
            "📌 Detalles del Sensor"
        ])

        with tab1:
            st.subheader('📈 Visualización Interactiva')

            variable = st.selectbox(
                "Selecciona la variable a visualizar",
                ["temperatura", "humedad", "Ambas variables"]
            )

            chart_type = st.selectbox(
                "Selecciona tipo de gráfico",
                ["Línea", "Área", "Barra"]
            )

            if variable == "Ambas variables":
                st.write("### Temperatura")
                if chart_type == "Línea":
                    st.line_chart(df1["temperatura"])
                elif chart_type == "Área":
                    st.area_chart(df1["temperatura"])
                else:
                    st.bar_chart(df1["temperatura"])

                st.write("### Humedad")
                if chart_type == "Línea":
                    st.line_chart(df1["humedad"])
                elif chart_type == "Área":
                    st.area_chart(df1["humedad"])
                else:
                    st.bar_chart(df1["humedad"])
            else:
                if chart_type == "Línea":
                    st.line_chart(df1[variable])
                elif chart_type == "Área":
                    st.area_chart(df1[variable])
                else:
                    st.bar_chart(df1[variable])

            if st.checkbox('📄 Ver datos sin procesar'):
                st.write(df1)

        with tab2:
            st.subheader('📊 Estadísticas Generales')

            stat_variable = st.radio(
                "Selecciona una variable",
                ["temperatura", "humedad"]
            )

            stats_df = df1[stat_variable].describe()

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(stats_df)

            with col2:
                if stat_variable == "temperatura":
                    st.metric("Temperatura Promedio", f"{stats_df['mean']:.2f}°C")
                    st.metric("Temperatura Máxima", f"{stats_df['max']:.2f}°C")
                    st.metric("Temperatura Mínima", f"{stats_df['min']:.2f}°C")
                else:
                    st.metric("Humedad Promedio", f"{stats_df['mean']:.2f}%")
                    st.metric("Humedad Máxima", f"{stats_df['max']:.2f}%")
                    st.metric("Humedad Mínima", f"{stats_df['min']:.2f}%")

        with tab3:
            st.subheader('🔎 Filtrado de Datos')

            filter_variable = st.selectbox(
                "Selecciona variable para filtrar",
                ["temperatura", "humedad"]
            )

            col1, col2 = st.columns(2)
            with col1:
                min_val = st.slider(
                    f'Valor mínimo de {filter_variable}',
                    float(df1[filter_variable].min()),
                    float(df1[filter_variable].max()),
                    float(df1[filter_variable].mean()),
                    key="min_val"
                )
                filtrado_df_min = df1[df1[filter_variable] > min_val]
                st.write(f"Registros con {filter_variable} mayor a {min_val}:")
                st.dataframe(filtrado_df_min)

            with col2:
                max_val = st.slider(
                    f'Valor máximo de {filter_variable}',
                    float(df1[filter_variable].min()),
                    float(df1[filter_variable].max()),
                    float(df1[filter_variable].mean()),
                    key="max_val"
                )
                filtrado_df_max = df1[df1[filter_variable] < max_val]
                st.write(f"Registros con {filter_variable} menor a {max_val}:")
                st.dataframe(filtrado_df_max)

            if st.button('⬇️ Descargar datos filtrados'):
                csv = filtrado_df_min.to_csv().encode('utf-8')
                st.download_button(
                    label="📄 Descargar CSV",
                    data=csv,
                    file_name='datos_filtrados.csv',
                    mime='text/csv',
                )

        with tab4:
            st.subheader("🏫 Información del Sitio de Medición")

            col1, col2 = st.columns(2)
            with col1:
                st.write("### 📍 Ubicación del Sensor")
                st.write("**Universidad EAFIT**")
                st.write("- Latitud: 6.2006")
                st.write("- Longitud: -75.5783")
                st.write("- Altitud: ~1,495 m.s.n.m")

            with col2:
                st.write("### 🔧 Detalles Técnicos")
                st.write("- Sensor: ESP32")
                st.write("- Variables medidas:")
                st.write("  * Temperatura (°C)")
                st.write("  * Humedad (%)")
                st.write("- Frecuencia: Según configuración")

        st.balloons()

    except Exception as e:
        st.error(f'❌ Error al procesar el archivo: {str(e)}')
else:
    st.warning('📂 Por favor, carga un archivo CSV para comenzar el análisis.')

# Footer
st.markdown("""
---
🛰️ Desarrollado para el análisis ambiental con sensores ESP32.  
🌍 Ubicación: Universidad EAFIT, Medellín, Colombia  
📅 Proyecto Cooltivo © 2025
""")
