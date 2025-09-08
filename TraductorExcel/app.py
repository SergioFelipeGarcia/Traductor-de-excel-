import streamlit as st
import pandas as pd
import time
import io
from deep_translator import GoogleTranslator

# --- Configuración de la Página y Estado de la Sesión ---

st.set_page_config(page_title="Traductor de Excel Fiable", layout="wide")

# Inicializar el estado de la sesión para mantener los datos
if 'translated_df' not in st.session_state:
    st.session_state.translated_df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Lógica de Traducción ---

def translate_text(text, target_language, retries=3, delay=2):
    """
    Traduce un único texto usando deep-translator con reintentos.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Simplificar el código de idioma (ej. 'pt-BR' -> 'pt')
    simple_target_lang = target_language.split('-')[0]
    
    for attempt in range(retries):
        try:
            # Pequeña pausa para no sobrecargar el servicio
            time.sleep(0.2)
            return GoogleTranslator(source='auto', target=simple_target_lang).translate(text)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                st.warning(f"No se pudo traducir '{text[:30]}...': {e}")
                return f"ERROR: {e}"
    return "ERROR_TRADUCCION"

# --- Interfaz Principal de la Aplicación ---

st.title("🚀 Traductor de Excel Fiable")
st.markdown("Sube tu fichero Excel, elige qué traducir y obtén los resultados de forma segura. Este traductor usa el motor de Google Translate.")

# Componente para subir el fichero
uploaded_file = st.file_uploader(
    "1. Sube tu fichero Excel",
    type=["xlsx"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    # Si se sube un nuevo fichero, se resetea el estado
    if st.session_state.original_df is None or uploaded_file.name != st.session_state.file_name:
        df_loaded = pd.read_excel(uploaded_file)
        # Solución al ArrowTypeError: Convertir todas las columnas de tipo 'object' a 'string'
        # Esto previene errores de tipo mixto (ej. números en una columna de texto)
        for col in df_loaded.select_dtypes(include=['object']).columns:
            df_loaded[col] = df_loaded[col].astype(str).fillna('')
        
        st.session_state.original_df = df_loaded
        st.session_state.translated_df = st.session_state.original_df.copy()
        st.session_state.file_name = uploaded_file.name

    df = st.session_state.translated_df
    st.success(f"Fichero '{uploaded_file.name}' cargado. Columnas: {', '.join(df.columns)}")

    with st.form("translation_form"):
        st.subheader("2. Configura la Traducción")
        col1, col2 = st.columns(2)

        with col1:
            source_col = st.selectbox("Columna a traducir:", df.columns)
        with col2:
            target_langs_str = st.text_input("Idiomas de destino (separados por coma):", "es, fr, de")

        submitted = st.form_submit_button("✨ Iniciar Traducción")

    if submitted:
        target_langs = [lang.strip() for lang in target_langs_str.split(',')]
        
        # Forzar la columna de origen a ser de tipo string para evitar errores
        df[source_col] = df[source_col].astype(str)
        
        # --- Bucle principal de traducción ---
        for lang in target_langs:
            col_name = f"{source_col}_{lang}"
            if col_name not in df.columns:
                df[col_name] = pd.Series(dtype='str')

            # Filtrar filas que realmente necesitan traducción para este idioma
            source_has_text = (df[source_col].notna()) & (df[source_col] != '')
            target_needs_translation = (df[col_name].isna()) | (df[col_name] == '') | (df[col_name].str.startswith("ERROR"))
            rows_to_translate_lang = df[source_has_text & target_needs_translation]

            if rows_to_translate_lang.empty:
                st.write(f"No hay nada que traducir para el idioma '{lang}'. Saltando.")
                continue

            st.info(f"Traduciendo {len(rows_to_translate_lang)} textos a '{lang}'...")
            progress_bar = st.progress(0, text=f"Traduciendo a {lang}...")
            
            total_rows = len(rows_to_translate_lang)
            for i, (index, row) in enumerate(rows_to_translate_lang.iterrows()):
                text_to_translate = row[source_col]
                
                translated_text = translate_text(text_to_translate, lang)
                df.at[index, col_name] = translated_text
                
                # Actualizar UI
                progress_text = f"Traduciendo a {lang}... ({i+1}/{total_rows})"
                progress_bar.progress((i + 1) / total_rows, text=progress_text)

            progress_bar.empty()
        
        st.session_state.translated_df = df
        st.success("¡Traducción completada para todos los idiomas!")

# --- Mostrar resultados y opciones de descarga ---
if st.session_state.translated_df is not None:
    st.subheader("Vista Previa del Resultado")
    st.dataframe(st.session_state.translated_df)

    # Convertir DataFrame a formato Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.translated_df.to_excel(writer, index=False, sheet_name='Traducciones')
    
    st.download_button(
        label="📥 Descargar Excel Traducido",
        data=output.getvalue(),
        file_name=f"Traducido_{st.session_state.file_name}",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    if st.button("🧹 Empezar de nuevo con otro fichero"):
        # Resetear todo el estado para forzar la subida de un nuevo fichero
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()