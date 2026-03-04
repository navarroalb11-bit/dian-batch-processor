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

import base64

def load_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Ruta del logo adaptada a la estructura de carpetas
logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exxo logo.jpg")
logo_b64 = load_image_as_base64(logo_path)
logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="max-height: 80px; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">' if logo_b64 else ''

# INJECTION OF CUSTOM CSS FOR LIGHT/PREMIUM THEME
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global Background and text styling */
    .stApp {{
        background-color: #F4F7F9;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Center Container Wrapper */
    .block-container {{
        background-color: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.06);
        padding: 3.5rem 2.5rem !important;
        margin-top: 3rem;
        margin-bottom: 3rem;
        max-width: 800px;
    }}

    /* Header text */
    h1, h2, h3 {{
        color: #2C3E50 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }}

    .title-text {{
        color: #2C3E50;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }}
    
    .subtitle-text {{
        color: #7F8C8D;
        font-size: 1.15rem;
        font-weight: 400;
        margin-bottom: 2.5rem;
    }}

    /* Uploader Border & Colors */
    .stFileUploader {{
        background-color: rgba(44, 62, 80, 0.02);
        border: 2px dashed #3498DB;
        border-radius: 15px;
        padding: 2.5rem 1rem;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        background-color: rgba(44, 62, 80, 0.05);
        border-color: #2C3E50;
    }}
    
    .stFileUploader > div > div {{
        background-color: transparent;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: #2C3E50 !important;
        color: white !important;
        font-weight: 600;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
        height: 60px;
        box-shadow: 0 4px 10px rgba(44, 62, 80, 0.15);
        margin-top: 1rem;
    }}
    .stButton > button:hover {{
        background-color: #1A252F !important;
        box-shadow: 0 6px 15px rgba(44, 62, 80, 0.25);
        transform: translateY(-2px);
    }}
    
    .stButton > button:disabled {{
        background-color: #BDC3C7 !important;
        box-shadow: none !important;
        transform: none !important;
        color: #ECF0F1 !important;
        cursor: not-allowed;
    }}

    /* Success Button/Download */
    .stDownloadButton > button {{
        background-color: #27AE60 !important;
        color: white !important;
        font-weight: 600;
        width: 100%;
        height: 65px;
        font-size: 1.15rem !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 15px rgba(39, 174, 96, 0.2);
        margin-top: 1.5rem;
    }}
    .stDownloadButton > button:hover {{
        background-color: #219653 !important;
        box-shadow: 0 8px 20px rgba(39, 174, 96, 0.3);
        transform: translateY(-2px);
    }}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown(f'''
<div style="text-align: center; margin-bottom: 1.5rem;">
    {logo_html}
    <div class="title-text">Extractor de Datos XML</div>
    <div class="subtitle-text">Extractor Maestro de Facturación Electrónica</div>
</div>
''', unsafe_allow_html=True)

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
                    
                success_html = f"""
                <div style="background-color: #F8FFF9; border: 1px solid #E3FBEA; padding: 1.2rem 1.5rem; border-radius: 12px; display: flex; align-items: center; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(39, 174, 96, 0.08);">
                    <div style="background-color: #27AE60; color: white; border-radius: 50%; width: 44px; height: 44px; display: flex; justify-content: center; align-items: center; font-size: 1.4rem; margin-right: 1.2rem; flex-shrink: 0; box-shadow: 0 4px 10px rgba(39, 174, 96, 0.2);">✓</div>
                    <div>
                        <h4 style="margin: 0; color: #1E8449; font-size: 1.1rem; font-weight: 600; font-family: 'Inter', sans-serif;">¡Extracción Completada!</h4>
                        <p style="margin: 0; color: #5D6D7E; font-size: 0.95rem; font-family: 'Inter', sans-serif; margin-top: 0.2rem;">Se extrajeron exitosamente <b>{stats['processed']}</b> facturas.</p>
                    </div>
                </div>
                """
                st.markdown(success_html, unsafe_allow_html=True)
                
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
