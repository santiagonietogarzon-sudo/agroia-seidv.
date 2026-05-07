import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE IMAGEN Y MARCA ---
st.set_page_config(page_title="SEIDV - AgroIA", page_icon="🌿", layout="wide")

# Estilo Profesional: Verde Oscuro y Blanco
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stApp { color: #004d26; }
    .stButton>button { 
        background-color: #004d26; 
        color: white; 
        border-radius: 5px;
        border: none;
    }
    .stMetric {
        background-color: #f0f4f2;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #004d26;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("🌿 SEIDV: Sistema Ecofisiológico Integrado")
st.markdown("### Inteligencia Vegetal aplicada al Diagnóstico de Campo")
st.write("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("CONFIGURACIÓN")
    st.markdown("---")
    st.write("**Metodología:** SEIDV™")
    st.write("**Autor:** Ing. J. Barrios")
    st.write("**Cultivo:** Mamey")

# --- CARGA DE DATOS ---
st.subheader("📁 Carga de Biometría")
archivo = st.file_uploader("Sube el archivo Excel para análisis", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    
    # Cálculos Fisiológicos SEIDV
    df['CRA'] = ((df['PESO FRESCO'] - df['PESO SECO']) / (df['PESO TURGENTE'] - df['PESO SECO'])) * 100
    df['MANEJO'] = df['TRATAMIENTO'].apply(lambda x: 'Microbióticos' if 'TN' in str(x).upper() else 'Control')
    
    # Métricas Principales
    idfl = (df[df['CRA'] < 70].shape[0] / len(df))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("IDFL (Indice de Dominancia)", f"{idfl:.2f}")
    with col2:
        st.metric("Vigor SPAD Promedio", f"{df['SPAD'].mean():.1f}")
    with col3:
        st.metric("CRA Promedio", f"{df['CRA'].mean():.1f}%")

    st.write("---")
    
    # Gráfica de Impacto
    st.subheader("📊 Comparativa: Impacto de Tratamiento")
    fig = px.bar(df.groupby('MANEJO')['SPAD'].mean().reset_index(), 
                 x='MANEJO', y='SPAD', 
                 color='MANEJO',
                 color_discrete_map={'Microbióticos': '#004d26', 'Control': '#cccccc'},
                 template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

    # Diagnóstico Final
    st.subheader("📋 Conclusiones del Sistema")
    if idfl > 0.5:
        st.error(f"ORIGEN HÍDRICO DOMINANTE: Se detecta un {idfl*100:.1f}% de estrés en el lote.")
    else:
        st.success("EQUILIBRIO METABÓLICO: El sistema fluye correctamente.")
