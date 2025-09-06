import pandas as pd
from deep_translator import GoogleTranslator
import time
import streamlit as st
import io
from streamlit.runtime.scriptrunner import add_script_run_ctx

# --- Lógica de Traducción ---

def translate_text(text_to_translate, target_language, retries=3, delay=2):
    """
    Traduce el texto usando el motor de Google Translate a través de deep-translator.
    Incluye reintentos para manejar errores de red.
    """
    if not isinstance(text_to_translate, str) or not text_to_translate.strip():
        return ""

    simple_target_lang = target_language.split('-')[0]

    for attempt in range(retries):
        try:
            translated_text = GoogleTranslator(source='auto', target=simple_target_lang).translate(text_to_translate)
            time.sleep(0.3)
            return translated_text
        except Exception as e:
            # Aquí usamos print, ya que estamos en una aplicación web y no en la terminal.
            # Este mensaje se verá en los logs de la consola del servidor.
            print(f"[ERROR] Intento {attempt + 1} fallido para '{text_to_translate}': {e}")
            if attempt < retries - 1:
                print(f"[INFO] Reintentando en {delay * (2 ** attempt)} segundos...")
                time.sleep(delay * (2 ** attempt))
            else:
                print(f"[CRÍTICO] Fallaron todos los intentos para traducir '{text_to_translate}'.")
                return f"ERROR_TRADUCCION_FALLIDA: {e}"
    return "ERROR_INESPERADO"

# --- Interfaz de Streamlit ---

st.set_page_config(
    page_title="Traductor de Excel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo para un tema oscuro y moderno
st.markdown("""
<style>
    .reportview-container {
        background: #111;
        color: #eee;
    }
    .css-1d391kg {
        background-color: #212529;
    }
    h1, h2, h3 {
        color: #fca311;
    }
    .stButton>button {
        background-color: #fca311;
        color: black;
        border-radius: 10px;
        padding: 10px;
        border: none;
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #e59500;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Título y descripción
st.title("🌐 Asistente de Traducción de Archivos Excel")
st.markdown("""
    ¡Hola! Bienvenido a tu herramienta de traducción automática. Este programa te permite traducir rápidamente cualquier columna de texto en un archivo Excel (`.xlsx`) a múltiples idiomas.
    
    Está diseñado para ser **simple**, **robusto** y **didáctico**. Sigue los pasos numerados a continuación para ver la magia en acción.
""")

st.divider()

# --- Sección para descargar el archivo de ejemplo ---
st.subheader("1. 📂 Descarga nuestro archivo de ejemplo")
st.markdown("Para comenzar, descarga este archivo modelo. Así puedes familiarizarte con el formato requerido por la aplicación.")

sample_data = {
    'es': ['Hola mundo', 'La programación es divertida.', 'Una nueva oportunidad laboral.', 'Este es un gran producto.'],
    'en': ['Hello world', 'Programming is fun.', 'A new job opportunity.', 'This is a great product.']
}
sample_df = pd.DataFrame(sample_data)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    sample_df.to_excel(writer, index=False, sheet_name='Ejemplo')
excel_buffer.seek(0)

st.download_button(
    label="Descargar archivo de ejemplo (.xlsx)",
    data=excel_buffer,
    file_name="ejemplo_traduccion.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# --- Sección principal de la aplicación ---
st.subheader("2. ⬆️ Sube tu archivo y traduce")
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df_source = pd.read_excel(uploaded_file)
        st.success("🎉 ¡Archivo cargado con éxito! Aquí puedes ver una vista previa.")
        st.dataframe(df_source.head())

        col1, col2 = st.columns(2)

        with col1:
            # Selección de columna de origen
            columns = df_source.columns.tolist()
            source_col = st.selectbox("3. Elige la columna que quieres traducir:", options=columns)

        with col2:
            # Selección de idiomas de destino
            target_langs_str = st.text_input("4. Introduce los idiomas de destino (separados por comas)",
                                             placeholder="Ej: es, en, fr, de")
            target_langs = [lang.strip() for lang in target_langs_str.split(',') if lang.strip()]

        # Botón para iniciar la traducción
        if st.button("5. Iniciar Traducción"):
            if not source_col:
                st.error("Por favor, selecciona una columna de origen.")
            elif not target_langs:
                st.error("Por favor, introduce al menos un idioma de destino.")
            else:
                # Preparación del DataFrame para la salida
                df_output = df_source.copy()
                
                # Añadir columnas de destino si no existen
                for lang in target_langs:
                    col_name = f"{source_col}_{lang}"
                    if col_name not in df_output.columns:
                        df_output[col_name] = ""

                # Proceso de traducción
                total_rows = len(df_output)
                
                with st.status("Traducción en curso...", expanded=True) as status_bar:
                    for i, index in enumerate(df_output.index):
                        text_to_translate = str(df_source.at[index, source_col])
                        
                        status_bar.write(f"Traduciendo fila {i+1} de {total_rows}...")

                        for lang in target_langs:
                            col_name = f"{source_col}_{lang}"
                            try:
                                translated_text = translate_text(text_to_translate, lang)
                                df_output.at[index, col_name] = translated_text
                                status_bar.write(f"- Traducido a '{lang}' con éxito.")
                            except Exception as e:
                                translated_text = f"ERROR: {e}"
                                df_output.at[index, col_name] = translated_text
                                status_bar.write(f"- [ERROR] Fallo al traducir a '{lang}': {e}")
                                
                    status_bar.update(label="¡Traducción completada!", state="complete", expanded=False)

                st.success("✅ ¡Traducción completada!")
                st.dataframe(df_output)

                # Opción para descargar el archivo traducido
                excel_buffer_final = io.BytesIO()
                with pd.ExcelWriter(excel_buffer_final, engine='xlsxwriter') as writer:
                    df_output.to_excel(writer, index=False, sheet_name='Traducciones')
                excel_buffer_final.seek(0)
                
                st.download_button(
                    label="Descargar archivo traducido (.xlsx)",
                    data=excel_buffer_final,
                    file_name="traducciones_completadas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
    except Exception as e:
        st.error(f"❌ ¡Ocurrió un error al procesar el archivo! Por favor, verifica que el formato sea correcto. Detalles: {e}")

st.divider()

# --- Sección de demostración de tecnologías para reclutadores ---
with st.expander("Acerca de esta aplicación y su tecnología"):
    st.markdown("""
    Este programa está construido sobre una base robusta de bibliotecas de Python que demuestran conocimiento en **manipulación de datos** y **desarrollo web con Python**.

    * **Streamlit**: Utilizado para crear la interfaz web interactiva con solo unas pocas líneas de código. Permite transformar un script de Python en una aplicación completa, haciendo que el programa sea accesible para cualquier persona.
    * **Pandas**: La biblioteca estándar de Python para el análisis y la manipulación de datos. Se utiliza para leer el archivo Excel en una estructura de datos `DataFrame`, facilitando la selección y procesamiento de columnas.
    * **deep-translator**: Una biblioteca ligera que utiliza la API pública de Google Translate para la traducción, implementando reintentos automáticos para manejar posibles fallos de red.
    
    El programa está diseñado para ser eficiente y escalable, con una clara separación entre la lógica de negocio (la traducción) y la capa de presentación (la interfaz de usuario).
    """)