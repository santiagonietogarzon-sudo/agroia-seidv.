import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE INTERFAZ PROFESIONAL ---
st.set_page_config(page_title="SEIDV | AgroIA Intelligence", page_icon="🌿", layout="wide")

# Estilo: Blanco y Verde Oscuro (Limpieza y Profesionalismo)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stApp { color: #004d26; }
    /* Botones */
    .stButton>button { 
        background-color: #004d26; 
        color: white; 
        border-radius: 8px;
        width: 100%;
        border: none;
        height: 3em;
    }
    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] { color: #004d26; font-weight: bold; }
    .stMetric {
        background-color: #f8faf9;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🌿 SEIDV: Sistema Ecofisiológico Integrado")
st.markdown("#### Plataforma de Diagnóstico Agrícola Avanzado | Metodología J. Barrios")
st.write("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración de Lote")
    cultivo = st.text_input("Tipo de Cultivo", placeholder="Ej: Mamey, Papaya, Maíz...")
    lote_nombre = st.text_input("Nombre del Lote / Finca", placeholder="Ej: Madrigal Farm")
    st.markdown("---")
    st.write("Este sistema evalúa la ruta:  \n**Hidratación → Estomas → Fotosíntesis**")

# --- CARGADOR DE DATOS (REPARADO) ---
st.subheader("📁 Carga de Biometría de Campo")
st.info("Asegúrese de que su Excel contenga las columnas: PESO FRESCO, PESO SECO, PESO TURGENTE y SPAD.")
archivo = st.file_uploader("Subir archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    try:
        # Forzamos la lectura del motor openpyxl
        df = pd.read_excel(archivo, engine='openpyxl')
        
        # Limpieza de nombres de columnas (quita espacios extras)
        df.columns = [c.strip().upper() for c in df.columns]
        
        # CÁLCULOS SEIDV
        if all(col in df.columns for col in ['PESO FRESCO', 'PESO SECO', 'PESO TURGENTE']):
            df['CRA'] = ((df['PESO FRESCO'] - df['PESO SECO']) / (df['PESO TURGENTE'] - df['PESO SECO'])) * 100
            
            # Cálculo de IDFL (Indice de Dominancia)
            hojas_criticas = df[df['CRA'] < 70].shape[0]
            idfl = hojas_criticas / len(df)
            
            # Clasificación de Tratamiento
            if 'TRATAMIENTO' in df.columns:
                df['MANEJO'] = df['TRATAMIENTO'].apply(lambda x: 'Microbióticos (TN)' if 'TN' in str(x).upper() else 'Control')
            else:
                df['MANEJO'] = 'General'

            # DASHBOARD DE INDICADORES
            st.subheader(f"📊 Análisis Fisiológico: {cultivo if cultivo else 'Cultivo General'}")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("IDFL (Dominancia)", f"{idfl:.2f}", delta="- Crítico" if idfl > 0.5 else "Óptimo", delta_color="inverse")
            with m2:
                st.metric("Vigor (SPAD) Promedio", f"{df['SPAD'].mean():.1f}")
            with m3:
                st.metric("Hidratación (CRA) Media", f"{df['CRA'].mean():.1f}%")

            st.write("---")

            # VISUALIZACIÓN INTERACTIVA
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Distribución de Vigor por Manejo**")
                fig_spad = px.box(df, x='MANEJO', y='SPAD', color='MANEJO',
                                color_discrete_map={'Microbióticos (TN)': '#004d26', 'Control': '#a8c9b9', 'General': '#004d26'},
                                template='simple_white')
                st.plotly_chart(fig_spad, use_container_width=True)

            with col_b:
                st.markdown("**Relación Hidratación vs Vigor**")
                fig_scatter = px.scatter(df, x='CRA', y='SPAD', color='MANEJO',
                                       trendline="ols", template='simple_white',
                                       color_discrete_sequence=['#004d26', '#a8c9b9'])
                st.plotly_chart(fig_scatter, use_container_width=True)

            # DIAGNÓSTICO MAESTRO
            st.subheader("📋 Conclusiones del Diagnóstico Clínico")
            expander = st.expander("Ver Análisis Detallado")
            with expander:
                if idfl > 0.5:
                    st.error(f"**ALERTA:** Se detecta un desorden de ORIGEN HÍDRICO DOMINANTE.")
                    st.write(f"El {idfl*100:.1f}% del lote está bajo restricción estomática. Se recomienda corregir la hidratación antes de aplicar nitrógeno.")
                else:
                    st.success("**ESTADO:** Equilibrio metabólico detectado. La ruta fisiológica fluye correctamente.")
                
                st.info("**Predicción Biótica (7-14 días):** Evaluar presencia de chupadores debido a cambios en la presión de turgencia.")

        else:
            st.warning("El archivo no tiene las columnas necesarias para el cálculo de CRA.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
