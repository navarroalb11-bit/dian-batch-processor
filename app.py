import streamlit as st
import os
import shutil
import tempfile
import base64
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="EXXO - Centralized Extraction Node",
    page_icon="⚡",
    layout="wide"
)

# === VARIABLES DE ESTILO Y DISEÑO ===
ST_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Background and text styling */
    .stApp {
        background-color: #161C24; /* Darker background resembling the image */
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }
    
    /* Center Container Wrapper */
    .block-container {
        padding: 2rem 5rem !important;
        max-width: 1200px;
    }

    /* Header text */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    .title-text {
        color: #FFFFFF;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    .title-highlight {
        color: #00D9FF; /* Electric Cyan-Blue */
    }
    
    .subtitle-text {
        color: #8C98A4; /* Cloud Gray */
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .format-text {
        color: #6200EA; /* Cyber Violet */
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: 1px;
    }

    /* Uploader Area Customization */
    .upload-container {
        border: 1px dashed rgba(0, 217, 255, 0.3); /* Cyan border with opacity */
        border-radius: 12px;
        padding: 3rem 2rem;
        background-color: transparent;
        margin-bottom: 3rem;
        position: relative;
    }
    
    /* Streamlit Uploader Override */
    .stFileUploader {
        background-color: transparent !important;
    }
    
    .stFileUploader > div, .stFileUploader > div > div {
        background-color: transparent !important;
    }
    
    .stFileUploader label {
        display: none !important;
    }
    
    div[data-testid="stFileUploadDropzone"] {
        border: 1px dashed rgba(0, 217, 255, 0.4) !important;
        border-radius: 12px !important;
        background-color: transparent !important;
        padding: 4rem 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #00D9FF !important;
        background-color: rgba(0, 217, 255, 0.05) !important;
    }

    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.4rem;
        color: #FFFFFF;
        font-weight: 600;
    }
    
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p:nth-child(2) {
        font-size: 1rem;
        color: #8C98A4;
        font-weight: 400;
    }
    
    /* Upload Button Override */
    div[data-testid="stFileUploadDropzone"] button {
        background-color: #00D9FF !important;
        color: #101010 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.8rem 1.5rem !important;
        border: none !important;
        margin-top: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"] button:hover {
        background-color: #00B8D9 !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.4) !important;
    }

    /* Process/Download Buttons */
    .stButton > button {
        background-color: #00D9FF !important;
        color: #101010 !important;
        font-weight: 700;
        border: none !important;
        border-radius: 8px !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.2);
    }
    .stButton > button:hover {
        background-color: #00B8D9 !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:disabled {
        background-color: #2D3748 !important;
        color: #718096 !important;
        box-shadow: none !important;
        cursor: not-allowed;
        transform: none !important;
    }
    
    .stDownloadButton > button {
        background-color: #00D9FF !important;
        color: #101010 !important;
        font-weight: 700;
        border: none !important;
        border-radius: 8px !important;
        padding: 1rem 2rem !important;
        font-size: 1.15rem !important;
        width: 100%;
        margin-top: 2rem;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }
    
    .stDownloadButton > button:hover {
        background-color: #00B8D9 !important;
        box-shadow: 0 0 25px rgba(0, 217, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Top Navbar Logo Area */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
    }
    
    .logo-title {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .logo-subtitle {
        color: #00D9FF;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .user-text {
        text-align: right;
    }
    
    .user-name {
        color: #FFFFFF;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .user-plan {
        color: #00D9FF;
        font-size: 0.75rem;
    }
    
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FAD961 0%, #F76B1C 100%); /* Placeholder avatar gradient */
    }
    
    /* Stats Table Simulation */
    .stats-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .stats-title {
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .stats-title::before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #00D9FF;
        border-radius: 50%;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #8C98A4;
        font-size: 0.8rem;
        margin-top: 5rem;
        letter-spacing: 2px;
    }
</style>
"""

def load_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Ruta del logo adaptada
logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exxo logo.jpg")
logo_b64 = load_image_as_base64(logo_path)
logo_img_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height: 40px; border-radius: 8px;">' if logo_b64 else '<div style="width:40px; height:40px; background-color:#00D9FF; border-radius:8px;"></div>'

# INYECCIÓN DEL CSS
st.markdown(ST_STYLE, unsafe_allow_html=True)

# TOP NAVBAR
navbar_html = f"""
<div class="top-navbar">
    <div class="logo-container">
        {logo_img_tag}
        <div class="logo-text">
            <span class="logo-title">EXXO</span>
            <span class="logo-subtitle">DATA EXTRACTION SYSTEMS</span>
        </div>
    </div>
    <div class="user-profile">
        <div class="user-text">
            <div class="user-name">Admin User</div>
            <div class="user-plan">Enterprise Plan</div>
        </div>
        <div class="avatar"></div>
    </div>
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# HEADERS PRINCIPALES
header_html = """
<div class="title-text">Centralized <span class="title-highlight">Extraction</span> Node</div>
<div class="subtitle-text">Securely process your financial documents. Supported formats:</div>
<div class="format-text">XML, TXT</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# --- SECTION 1: XML/TXT FILES UPLOAD ---
# Engañamos un poco el uploader con custom CSS
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
xml_files = st.file_uploader("Arraste y suelte sus archivos aquí", type=["xml", "txt"], accept_multiple_files=True, help="o haga clic para explorar en su ordenador")
st.markdown('</div>', unsafe_allow_html=True)

if xml_files:
    # Mostramos un status minimalista en verde al cargar
    success_msg = f"""
    <div style="background-color: rgba(39, 174, 96, 0.1); border-left: 4px solid #27AE60; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;">
        <span style="color: #27AE60; font-weight: 600;">✓ {len(xml_files)} archivos listos</span> para el nodo de extracción.
    </div>
    """
    st.markdown(success_msg, unsafe_allow_html=True)

# --- SECTION 2: PROCESS AND EXPORT ---
if st.button("🚀 Iniciar Extracción", disabled=not bool(xml_files)):
    with st.spinner(f"Procesando {len(xml_files)} documentos a través del nodo central..."):
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, "input_xmls")
        os.makedirs(input_dir, exist_ok=True)
        output_excel = os.path.join(temp_dir, "Extraccion_Centralizada_EXXO.xlsx")
        
        try:
            # 1. Guardar XMLs temporalmente
            for xml_f in xml_files:
                xml_path = os.path.join(input_dir, xml_f.name)
                with open(xml_path, "wb") as f:
                    f.write(xml_f.getvalue())
                    
            # 2. Iniciar el motor extractor
            processor = BatchProcessor()
            stats = processor.process_folder(input_dir, output_excel)
            
            # 3. Mostrar Componente Simulado de Monitor en Tiempo Real
            monitor_html = """
            <div class="stats-header">
                <div class="stats-title">Monitor de Extracción en Tiempo Real</div>
                <div style="background-color: rgba(255,255,255,0.05); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; color: #8C98A4;">
                    <span style="margin-right: 5px;">🔄</span> Actualizado hace un momento
                </div>
            </div>
            """
            st.markdown(monitor_html, unsafe_allow_html=True)
            
            # Descargar el reporte
            if os.path.exists(output_excel):
                with open(output_excel, "rb") as f:
                    processed_file_data = f.read()
                    
                # Componente de Resultado Exitoso
                success_html = f"""
                <div style="background-color: rgba(0, 217, 255, 0.05); border: 1px solid rgba(0, 217, 255, 0.2); padding: 1.5rem; border-radius: 12px; display: flex; align-items: center; margin-bottom: 2rem;">
                    <div style="background-color: rgba(0, 217, 255, 0.1); color: #00D9FF; border-radius: 50%; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; font-size: 1.5rem; margin-right: 1.5rem; box-shadow: 0 0 15px rgba(0, 217, 255, 0.2);">✦</div>
                    <div>
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.2rem; font-weight: 600;">Nodo de Extracción Completado</h4>
                        <p style="margin: 0; color: #8C98A4; font-size: 0.95rem; margin-top: 0.3rem;">Se procesaron exitosamente <span style="color: #00D9FF; font-weight: bold;">{stats['processed']}</span> registros de facturación.</p>
                    </div>
                </div>
                """
                st.markdown(success_html, unsafe_allow_html=True)
                
                # Botón de Descarga Grande y llamativo (Cyan)
                st.download_button(
                    label="Descargar Base de Datos en Excel",
                    data=processed_file_data,
                    file_name="Extraccion_Centralizada_EXXO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error en el nodo de procesamiento: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# FOOTER
st.markdown('<div class="footer">EXXO INDUSTRIAL INTELLIGENCE © 2024</div>', unsafe_allow_html=True)
