import streamlit as st
import os
import shutil
import tempfile
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="Extractor Base de Datos XML",
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
    /* Buttons */
    .stButton > button {
        background-color: #1f538d !important;
        color: white !important;
        font-weight: bold;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.8rem 1rem !important;
        font-size: 1.1rem !important;
        transition: background-color 0.3s ease;
        width: 100%;
        height: 60px;
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
        height: 60px;
        font-size: 1.1rem !important;
    }
    .stDownloadButton > button:hover {
        background-color: #008f4c !important;
    }
    /* Muted Text */
    .muted-text {
        color: #a0a0a0;
        font-size: 1.1em;
        margin-bottom: 2rem;
    }
    /* Big icon intro */
    .hero-icon {
        font-size: 4rem;
        text-align: center;
        margin-bottom: -1rem;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<div class="hero-icon">📄➡️📊</div>', unsafe_allow_html=True)
st.title("Extractor de Base de Datos XML", anchor=False)
st.markdown('<p class="muted-text">Convierte cientos de facturas electrónicas (.xml) en un Excel limpio al instante.</p>', unsafe_allow_html=True)

# --- SECTION 1: XML/TXT FILES UPLOAD ---
xml_files = st.file_uploader("Arrastra tus archivos aquí (.xml, .txt)", type=["xml", "txt"], accept_multiple_files=True, label_visibility="collapsed")

if xml_files:
    st.success(f"✅ {len(xml_files)} archivos XML cargados y listos para extraer.")

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SECTION 2: PROCESS AND EXPORT ---
if st.button("🚀 Descargar Base de Datos", disabled=not bool(xml_files)):
    with st.spinner(f"Extrayendo datos de {len(xml_files)} facturas a alta velocidad..."):
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, "input_xmls")
        os.makedirs(input_dir, exist_ok=True)
        output_excel = os.path.join(temp_dir, "Base_Datos_Facturas.xlsx")
        
        try:
            # 1. Guardar XMLs temporalmente
            for xml_f in xml_files:
                xml_path = os.path.join(input_dir, xml_f.name)
                with open(xml_path, "wb") as f:
                    f.write(xml_f.getvalue())
                    
            # 2. Iniciar el motor extractor limpio
            processor = BatchProcessor()
            stats = processor.process_folder(input_dir, output_excel)
            
            # 3. Descargar el reporte
            if os.path.exists(output_excel):
                with open(output_excel, "rb") as f:
                    processed_file_data = f.read()
                    
                st.success(f"🤖 ¡Extracción finalizada! Procesadas {stats['processed']} facturas exitosamente.")
                
                # Reporte de Errores Amigable para el usuario
                if stats['failed_not_xml'] > 0:
                    st.warning(f"⚠️ {stats['failed_not_xml']} archivo(s) .txt no contenían una estructura válida de Factura Electrónica y fueron ignorados.")
                if stats['failed_not_invoice'] > 0:
                    st.warning(f"⚠️ {stats['failed_not_invoice']} archivo(s) tenían forma de XML pero no contenían datos contables (ej. Acuses de Recibo) y fueron omitidos.")
                    
                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=processed_file_data,
                    file_name="Base_Datos_Facturas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Ocurrió un error al procesar la base de datos: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
