import streamlit as st
import pandas as pd
import plotly.express as px
import difflib  # Librería para lectura inteligente de palabras

# --- 1. CONFIGURACIÓN DE INTERFAZ (BLANCO Y VERDE PROFUNDO) ---
st.set_page_config(page_title="SEIDV | Inteligencia Agrícola", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #013220; }
    [data-testid="stMetric"] { 
        background-color: #f8faf9 !important; 
        border-left: 5px solid #004d26 !important;
        border-radius: 10px !important;
    }
    .stButton>button { 
        background-color: #004d26 !important; 
        color: white !important; 
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 3.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIÓN DE LECTURA INTELIGENTE ---
def encontrar_columna(nombre_buscado, lista_columnas):
    """Busca la columna más parecida aunque falten letras o cambien mayúsculas"""
    lista_normalizada = [c.upper().strip() for c in lista_columnas]
    coincidencias = difflib.get_close_matches(nombre_buscado.upper(), lista_normalizada, n=1, cutoff=0.6)
    if coincidencias:
        idx = lista_normalizada.index(coincidencias[0])
        return lista_columnas[idx]
    return None

# --- 3. INTERFAZ ---
st.title("🌿 SEIDV: Diagnóstico Inteligente")
st.write("---")

with st.sidebar:
    st.header("⚙️ Configuración")
    cultivo = st.text_input("Cultivo", "Mamey")
    lote = st.text_input("Lote", "Madrigal Farm")
    st.info("La IA leerá su Excel aunque los nombres de las columnas no sean exactos.")

st.subheader("1. Carga de Archivo")
archivo = st.file_uploader("Subir Excel de Biometría", type=["xlsx"])

if archivo:
    st.success("✅ Archivo cargado.")
    
    if st.button("🚀 INICIAR ANÁLISIS EXPERTO"):
        try:
            df = pd.read_excel(archivo, engine='openpyxl')
            cols = list(df.columns)
            
            # Buscamos las columnas de forma inteligente
            col_pf = encontrar_columna("PESO FRESCO", cols)
            col_ps = encontrar_columna("PESO SECO", cols)
            col_pt = encontrar_columna("PESO TURGENTE", cols)
            col_spad = encontrar_columna("SPAD", cols)
            col_trat = encontrar_columna("TRATAMIENTO", cols)

            if all([col_pf, col_ps, col_pt, col_spad]):
                # Renombramos para trabajar fácil internamente
                df = df.rename(columns={col_pf: 'PF', col_ps: 'PS', col_pt: 'PT', col_spad: 'SPAD'})
                if col_trat: df = df.rename(columns={col_trat: 'TRATAMIENTO'})
                
                # --- CÁLCULOS SEIDV ---
                df = df.dropna(subset=['PF', 'PS', 'PT', 'SPAD'])
                df['CRA'] = ((df['PF'] - df['PS']) / (df['PT'] - df['PS'])) * 100
                
                # Manejo de Grupos
                if 'TRATAMIENTO' in df.columns:
                    df['MANEJO'] = df['TRATAMIENTO'].apply(lambda x: 'Microbióticos (TN)' if 'TN' in str(x).upper() else 'Control')
                else:
                    df['MANEJO'] = 'General'

                idfl = (df[df['CRA'] < 70].shape[0] / len(df))

                # --- RESULTADOS ---
                st.header(f"🔬 Análisis de {cultivo} - {lote}")
                m1, m2, m3 = st.columns(3)
                m1.metric("IDFL", f"{idfl:.2f}", "Dominancia Hídrica" if idfl > 0.5 else "Estable")
                m2.metric("Vigor (SPAD)", f"{df['SPAD'].mean():.1f}")
                m3.metric("Hidratación (CRA)", f"{df['CRA'].mean():.1f}%")

                # Gráficas Profesionales
                c_a, c_b = st.columns(2)
                with c_a:
                    fig1 = px.box(df, x='MANEJO', y='SPAD', color='MANEJO', title="Impacto en Vigor",
                                 color_discrete_map={'Microbióticos (TN)': '#004d26', 'Control': '#a8c9b9', 'General': '#004d26'})
                    st.plotly_chart(fig1, use_container_width=True)
                with c_b:
                    fig2 = px.scatter(df, x='CRA', y='SPAD', color='MANEJO', title="Ruta Fisiológica",
                                     trendline="ols", color_discrete_sequence=['#004d26', '#a8c9b9'])
                    st.plotly_chart(fig2, use_container_width=True)

                # --- EL INFORME MAESTRO (BASADO EN EL PDF) ---
                st.write("---")
                st.subheader("📋 Informe Clínico Detallado")
                
                if idfl > 0.5:
                    st.warning("### DIAGNÓSTICO: DESORDEN DE ORIGEN HÍDRICO DOMINANTE")
                    st.markdown(f"""
                    **Interpretación:** Con un IDFL de **{idfl:.2f}**, el sistema confirma que la falla no es metabólica primaria. 
                    El **{idfl*100:.0f}%** de las hojas están en condición crítica.
                    
                    **Ruta Detectada:** $Hidratación \rightarrow Estomas \downarrow \rightarrow Fotosíntesis \downarrow$
                    
                    **Acciones Inmediatas (Lógica Barrios):**
                    1. **Corregir Origen:** Recuperar el CRA mediante riego antes de cualquier nutrición.
                    2. **Reactivación:** Aplicar moduladores fisiológicos (Galahad) para mejorar la absorción.
                    3. **Alerta Biótica:** El estrés acumulado abre una ventana de riesgo de **Ácaros y Trips** en 7-14 días.
                    """)
                else:
                    st.success("### DIAGNÓSTICO: EQUILIBRIO METABÓLICO ESTABLE")
                    st.write("La planta mantiene turgencia óptima. La ruta fotosintética fluye sin restricciones.")

            else:
                faltan = []
                if not col_pf: faltan.append("Peso Fresco")
                if not col_ps: faltan.append("Peso Seco")
                if not col_pt: faltan.append("Peso Turgente")
                if not col_spad: faltan.append("SPAD")
                st.error(f"❌ No pude identificar estas columnas: {', '.join(faltan)}")
                st.info("Intenta que los nombres en tu Excel se parezcan a 'Peso Fresco', 'Peso Seco', etc.")

        except Exception as e:
            st.error(f"Ocurrió un error en el procesamiento: {e}")
