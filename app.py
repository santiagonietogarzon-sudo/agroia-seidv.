import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE INTERFAZ (BLANCO Y VERDE ESMERALDA) ---
st.set_page_config(page_title="SEIDV | AgroIA Platform", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #013220; }
    [data-testid="stMetric"] { 
        background-color: #f8faf9 !important; 
        border-left: 5px solid #004d26 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    .stButton>button { 
        background-color: #004d26 !important; 
        color: white !important; 
        font-size: 20px !important;
        height: 3em !important;
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CABECERA ---
st.title("🌿 SEIDV: Sistema de Diagnóstico Ecofisiológico")
st.write("---")

# --- 3. PANEL DE ENTRADA ---
with st.sidebar:
    st.header("📍 Configuración")
    cultivo = st.text_input("Variedad de Cultivo", "Mamey")
    lote = st.text_input("Lote / Sección", "Lote A")
    st.markdown("---")
    st.caption("Metodología: J. Barrios (2026)")

st.subheader("1. Carga de Biometría")
archivo = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    # Mostramos un mensaje de éxito al cargar
    st.success("Archivo cargado correctamente. Configure los parámetros y presione el botón de abajo.")
    
    # --- BOTÓN DE INICIO (TU PEDIDO) ---
    st.write("---")
    if st.button("🚀 INICIAR ANÁLISIS SEIDV™"):
        try:
            df = pd.read_excel(archivo, engine='openpyxl')
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Cálculos Maestros
            df['CRA'] = ((df['PESO FRESCO'] - df['PESO SECO']) / (df['PESO TURGENTE'] - df['PESO SECO'])) * 100
            df['MANEJO'] = df['TRATAMIENTO'].apply(lambda x: 'Microbióticos (TN)' if 'TN' in str(x).upper() else 'Control')
            
            hojas_criticas = df[df['CRA'] < 70].shape[0]
            idfl = hojas_criticas / len(df)
            
            # --- RESULTADOS ---
            st.header(f"🔬 Resultados del Diagnóstico: {lote}")
            
            # Métricas de Impacto
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("IDFL", f"{idfl:.2f}", "Dominancia" if idfl > 0.5 else "Estable")
            m2.metric("SPAD Promedio", f"{df['SPAD'].mean():.1f}")
            m3.metric("CRA Lote", f"{df['CRA'].mean():.1f}%")
            m4.metric("Estado", "ALERTA" if idfl > 0.5 else "ÓPTIMO")

            # --- ANÁLISIS GRÁFICO ---
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.box(df, x='MANEJO', y='SPAD', color='MANEJO', 
                             title="Vigor Foliar por Manejo",
                             color_discrete_map={'Microbióticos (TN)': '#004d26', 'Control': '#cccccc'})
                st.plotly_chart(fig1, use_container_width=True)
            with col_b:
                fig2 = px.scatter(df, x='CRA', y='SPAD', color='MANEJO', 
                                 title="Relación CRA vs Fotosíntesis",
                                 trendline="ols",
                                 color_discrete_map={'Microbióticos (TN)': '#004d26', 'Control': '#cccccc'})
                st.plotly_chart(fig2, use_container_width=True)

            # --- INFORME DETALLADO ESTILO MADRIGAL FARM ---
            st.write("---")
            st.subheader("📋 Conclusiones Clínicas")
            
            if idfl > 0.5:
                st.error("### ORIGEN HÍDRICO DOMINANTE")
                st.markdown(f"""
                **Análisis:** El sistema no está fallando por una causa metabólica primaria. El IDFL de **{idfl:.2f}** confirma una limitación directa en la hidratación celular.
                
                **Ruta Fisiológica:**
                - La planta mantiene transpiración, pero sobre una base hídrica deficiente.
                - Esto genera una restricción estomática progresiva.
                
                **Recomendaciones SEIDV:**
                1. **Recuperar el Origen:** Corregir el CRA antes de cualquier fertilización.
                2. **Modulación Radicular:** Aplicar **Galahad** para mejorar absorción.
                3. **Prevención Biótica:** Riesgo inminente de **Ácaros/Trips** en los próximos 7-14 días.
                """)
            else:
                st.success("### EQUILIBRIO METABÓLICO ESTABLE")
                st.write("La ruta Hidratación → Estomas → Transpiración fluye correctamente.")

        except Exception as e:
            st.error(f"Error técnico en el análisis: {e}")
