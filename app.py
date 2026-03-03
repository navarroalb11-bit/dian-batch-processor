import streamlit as st
import pandas as pd
import json
import os
import shutil
import tempfile
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="Extractor Electrónico - DIAN",
    page_icon="⚡",
    layout="centered"
)

# INJECTION OF CUSTOM CSS FOR DARK/PROFESSIONAL THEME
st.markdown("""
<style>
    /* Global Background and text styling */
    .stApp {
        background-color: #1c1c1f;
        color: #ffffff;
    }
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Uploader Border & Colors */
    .stFileUploader {
        background-color: #2b2b2e;
        border-radius: 10px;
        padding: 10px;
    }
    .stFileUploader > div > div {
        background-color: transparent;
    }
    /* Selectboxes */
    div[data-baseweb="select"] > div {
        background-color: #2b2b2e;
        color: white;
        border-radius: 4px;
        border: 1px solid #1f538d;
    }    
    /* Buttons */
    .stButton > button {
        background-color: #1f538d !important;
        color: white !important;
        font-weight: bold;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        transition: background-color 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #14375e !important;
        color: white !important;
        border: none !important;
    }
    /* Success Button/Download */
    .stDownloadButton > button {
        background-color: #00a859 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
    }
    .stDownloadButton > button:hover {
        background-color: #008f4c !important;
    }
    /* Muted Text */
    .muted-text {
        color: #a0a0a0;
        font-size: 0.9em;
    }
    /* Box wrapper for matcher */
    .matcher-box {
        background-color: #2b2b2e;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("⚡ Procesador Batch de Facturas XML")
st.markdown('<p class="muted-text">Herramienta profesional de automatización para contabilidad.</p>', unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'mapping_config' not in st.session_state:
    st.session_state.mapping_config = {}
if 'columns_order' not in st.session_state:
    st.session_state.columns_order = []
if 'excel_uploaded' not in st.session_state:
    st.session_state.excel_uploaded = False

# --- SECTION 1: XML UPLOAD (DRAG & DROP) ---
st.markdown("### 1. Carga de Facturas (XML)")
st.markdown('<p class="muted-text">Arrastra aquí todos los XML proporcionados por la DIAN.</p>', unsafe_allow_html=True)
xml_files = st.file_uploader("Sube tus archivos XML", type=["xml"], accept_multiple_files=True, label_visibility="collapsed")

if xml_files:
    st.success(f"✅ {len(xml_files)} archivos XML listos.")

st.markdown("---")

# --- SECTION 2: EXCEL TEMPLATE & MATCHER ---
st.markdown("### 2. Plantilla de Excel y Mapeo")
st.markdown('<p class="muted-text">Sube la plantilla de Excel donde deseas extraer la información.</p>', unsafe_allow_html=True)
excel_file = st.file_uploader("Sube tu plantilla Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")

if excel_file:
    # Leer las columnas del excel en la primera hoja
    try:
        df_template = pd.read_excel(excel_file, nrows=0) # Solo lee la cabecera
        st.session_state.columns_order = list(df_template.columns)
        st.session_state.excel_uploaded = True
        st.success(f"✅ Plantilla '{excel_file.name}' cargada correctamente.")
    except Exception as e:
        st.error(f"Error al leer el Excel: {str(e)}")

# VISUAL MATCHER
if st.session_state.excel_uploaded:
    st.markdown('<div class="matcher-box">', unsafe_allow_html=True)
    st.markdown("#### Configuración de Columnas")
    st.markdown("Empareja las columnas de tu Excel con las etiquetas del XML de la DIAN.")
    
    # Algunas etiquetas comunes para facilitar la selección. El usuario puede escribir otras también
    xml_tags_suggestions = [
        "[Ignorar esta columna]",
        "ID", "IssueDate", "DueDate", "PayableAmount",
        "LineExtensionAmount", "TaxExclusiveAmount", "TaxInclusiveAmount",
        "CompanyID", "RegistrationName", "CitySubdivisionName",
        "TaxAmount", "TaxableAmount", "MultiplierFactorNumeric"
    ]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Columna Excel**")
    with col2:
        st.markdown("**Etiqueta XML a extraer**")
        
    for col_name in st.session_state.columns_order:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write(col_name)
        with c2:
            # We use a selectbox but allow the user to type to search or add custom (if streamlit allowed natively, we stick to common list and a text input option)
            # For simplicity, we provide a list, but also a way to map exactly.
            selected = st.selectbox(
                f"XML Tag for {col_name}", 
                options=xml_tags_suggestions, 
                key=f"match_{col_name}", 
                label_visibility="collapsed"
            )
            if selected != "[Ignorar esta columna]":
                st.session_state.mapping_config[col_name] = selected
            else:
                st.session_state.mapping_config.pop(col_name, None)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- SECTION 3: PROCESS AND EXPORT ---
st.markdown("### 3. Procesamiento")

# Check if ready
is_ready = bool(xml_files) and st.session_state.excel_uploaded and len(st.session_state.mapping_config) > 0

if st.button("🚀 Procesar Facturas", disabled=not is_ready):
    if not is_ready:
        st.warning("Asegúrate de cargar XMLs, un Excel y configurar al menos una columna.")
    else:
        with st.spinner("Procesando archivos y generando Excel..."):
            # Create a temporary directory structure safely
            temp_dir = tempfile.mkdtemp()
            input_dir = os.path.join(temp_dir, "input_xmls")
            os.makedirs(input_dir, exist_ok=True)
            output_excel = os.path.join(temp_dir, "resultado.xlsx")
            mapping_file = os.path.join(temp_dir, "temp_mapping.json")
            
            try:
                # 1. Save all uploaded XMLs to input_dir
                for xml_f in xml_files:
                    xml_path = os.path.join(input_dir, xml_f.name)
                    with open(xml_path, "wb") as f:
                        f.write(xml_f.getvalue())
                        
                # 2. Generate Mapping JSON exactly as BatchProcessor expects
                mapping_schema = {
                    "columns_order": st.session_state.columns_order,
                    "mapping": st.session_state.mapping_config
                }
                with open(mapping_file, "w", encoding="utf-8") as f:
                    json.dump(mapping_schema, f, ensure_ascii=False, indent=4)
                    
                # 3. Init BatchProcessor and run
                processor = BatchProcessor(mapping_file)
                processor.process_folder(input_dir, output_excel)
                
                # 4. Put the output file into Session State to provide download button
                if os.path.exists(output_excel):
                    with open(output_excel, "rb") as f:
                        processed_file_data = f.read()
                        
                    st.success("✅ ¡Procesamiento Exitoso! Puedes descargar tu archivo a continuación.")
                    
                    st.download_button(
                        label="⬇️ Descargar Excel Consolidado",
                        data=processed_file_data,
                        file_name="Facturas_Extraidas_DIAN.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Hubo un error al generar el archivo final.")
            
            except Exception as e:
                st.error(f"Error procesando los archivos: {str(e)}")
            
            finally:
                # Cleanup temp files cleanly
                shutil.rmtree(temp_dir, ignore_errors=True)
