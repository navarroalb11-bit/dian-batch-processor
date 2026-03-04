import streamlit as st
import os
import shutil
import tempfile
import base64
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="EXXO - Nodo de Extracción Centralizado",
    page_icon="⚡",
    layout="wide"
)

# === VARIABLES DE ESTILO Y DISEÑO ===
ST_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Background Transparent for Video */
    .stApp {
        background-color: transparent !important;
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }
    
    /* Video Background Container */
    #background-video {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1;
        object-fit: cover;
        opacity: 0.8; /* Slightly dim the video */
    }

    /* Video Overlay for Darkness */
    #video-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.4);
        z-index: 0;
    }

    /* Animation Keyframes */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Cinematic Center App Container with Glassmorphism */
    .block-container {
        padding: 4rem 5rem !important;
        max-width: 1100px;
        background-color: rgba(22, 28, 36, 0.3) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-top: 4rem;
        margin-bottom: 4rem;
        z-index: 10;
        position: relative;
        /* Triggering Fade In */
        animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Header text */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    .title-text {
        color: #FFFFFF;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .title-highlight {
        color: #00D9FF; /* Electric Cyan-Blue */
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
    }
    
    .subtitle-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.2rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 0.2rem;
        text-shadow: 0 1px 5px rgba(0,0,0,0.5);
    }

    .format-text {
        color: #00D9FF;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 3.5rem;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
    }

    /* Uploader Area Customization Glassmorphism */
    .upload-container {
        border-radius: 15px;
        background-color: rgba(0, 0, 0, 0.2);
        margin-bottom: 3rem;
        position: relative;
        backdrop-filter: blur(5px);
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
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        background-color: rgba(0, 0, 0, 0.2) !important;
        padding: 5rem 2rem !important;
        transition: all 0.4s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #00D9FF !important;
        background-color: rgba(0, 217, 255, 0.05) !important;
        box-shadow: inset 0 0 30px rgba(0, 217, 255, 0.1);
    }

    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.6rem;
        color: #FFFFFF;
        font-weight: 600;
        text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p:nth-child(2) {
        font-size: 1rem;
        color: rgba(255,255,255,0.6);
        font-weight: 400;
    }
    
    /* Upload Button Override */
    div[data-testid="stFileUploadDropzone"] button {
        background-color: rgba(255,255,255,0.1) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.8rem 2rem !important;
        margin-top: 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"] button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.4) !important;
    }

    /* Process/Download Premium Button */
    .stButton > button {
        background: linear-gradient(90deg, #00D9FF 0%, #0077FF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700;
        border: none !important;
        border-radius: 10px !important;
        padding: 1.2rem 2rem !important;
        font-size: 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100%;
        margin-top: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 162, 255, 0.4) !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #00F0FF 0%, #0099FF 100%) !important;
        box-shadow: 0 8px 30px rgba(0, 162, 255, 0.7) !important;
        transform: translateY(-3px) scale(1.01);
    }
    
    .stButton > button:disabled {
        background: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
        cursor: not-allowed;
        transform: none !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00D9FF 0%, #0077FF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700;
        border: none !important;
        border-radius: 10px !important;
        padding: 1.2rem 2rem !important;
        font-size: 1.2rem !important;
        width: 100%;
        margin-top: 2rem;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 162, 255, 0.4) !important;
        letter-spacing: 0.5px;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #00F0FF 0%, #0099FF 100%) !important;
        box-shadow: 0 8px 30px rgba(0, 162, 255, 0.7) !important;
        transform: translateY(-3px) scale(1.01);
    }

    /* Top Navbar Logo Area */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
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
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: 2px;
    }
    
    .logo-subtitle {
        color: #00D9FF;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        opacity: 0.8;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
        margin-top: 5rem;
        letter-spacing: 3px;
        font-weight: 500;
        text-transform: uppercase;
    }
</style>
"""

# INYECCIÓN DEL VIDEO BACKGROUND (Desde URL pública minimalista tech o un stock de data flow)
# Nota: Puedes configurar una variable o url estática para un video de server o S3.
VIDEO_URL = "https://cdn.pixabay.com/video/2018/02/25/14441-257643564_large.mp4" # Background placeholder cinemático de red

video_html = f"""
    <div id="video-overlay"></div>
    <video autoplay loop muted playsinline id="background-video">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
"""
st.markdown(video_html, unsafe_allow_html=True)


def load_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Ruta del logo adaptada al isotipo
logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exxo logo isotipo_Mesa de trabajo 1.jpg")
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
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# HEADERS PRINCIPALES
header_html = """
<div class="title-text">Nodo de <span class="title-highlight">Extracción</span></div>
<div class="subtitle-text">Procese de forma segura sus documentos financieros.</div>
<div class="format-text">XML / TXT</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# --- SECTION 1: XML/TXT FILES UPLOAD ---
# Engañamos un poco el uploader con custom CSS
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
xml_files = st.file_uploader("Arrastre y suelte sus archivos aquí", type=["xml", "txt"], accept_multiple_files=True, help="o haga clic para explorar en su ordenador")
st.markdown('</div>', unsafe_allow_html=True)

if xml_files:
    # Mostramos un status minimalista en verde al cargar (con glassmorphism)
    success_msg = f"""
    <div style="background-color: rgba(39, 174, 96, 0.2); border-left: 4px solid #00F0FF; padding: 1.2rem; border-radius: 8px; margin-bottom: 2rem; backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <span style="color: #00F0FF; font-weight: 600; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);">✓ {len(xml_files)} archivos en cola</span> <span style="color: rgba(255,255,255,0.8);">para análisis del nodo de capa profunda.</span>
    </div>
    """
    st.markdown(success_msg, unsafe_allow_html=True)

# --- SECTION 2: PROCESS AND EXPORT ---
if st.button("INICIAR EXTRACCIÓN ALGORÍTMICA 🚀", disabled=not bool(xml_files)):
    with st.spinner(f"Sintetizando {len(xml_files)} documentos a través de la red neuronal..."):
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, "input_xmls")
        os.makedirs(input_dir, exist_ok=True)
        output_excel = os.path.join(temp_dir, "Matrix_Financiera_EXXO.xlsx")
        
        try:
            # 1. Guardar XMLs temporalmente
            for xml_f in xml_files:
                xml_path = os.path.join(input_dir, xml_f.name)
                with open(xml_path, "wb") as f:
                    f.write(xml_f.getvalue())
                    
            # 2. Iniciar el motor extractor (INTACTO)
            processor = BatchProcessor()
            stats = processor.process_folder(input_dir, output_excel)
            
            # Descargar el reporte
            if os.path.exists(output_excel):
                with open(output_excel, "rb") as f:
                    processed_file_data = f.read()
                    
                # Componente de Resultado Exitoso Cinematográfico
                success_html = f"""
                <div style="background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 50, 100, 0.3) 100%); border: 1px solid rgba(0, 217, 255, 0.3); padding: 2rem; border-radius: 15px; display: flex; align-items: center; margin-bottom: 2rem; backdrop-filter: blur(10px); box-shadow: inset 0 0 20px rgba(0, 217, 255, 0.1), 0 10px 30px rgba(0,0,0,0.5); animation: fadeInUp 0.5s ease forwards;">
                    <div style="background-color: rgba(0, 217, 255, 0.15); color: #00D9FF; border-radius: 50%; width: 60px; height: 60px; display: flex; justify-content: center; align-items: center; font-size: 1.8rem; margin-right: 1.5rem; box-shadow: 0 0 20px rgba(0, 217, 255, 0.4); text-shadow: 0 0 10px #00D9FF;">✦</div>
                    <div>
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 5px rgba(0,0,0,0.5);">Secuencia Finalizada</h4>
                        <p style="margin: 0; color: rgba(255,255,255,0.7); font-size: 1rem; margin-top: 0.4rem;">Registros financieros exitosos: <span style="color: #00D9FF; font-weight: 800; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);">{stats['processed']}</span></p>
                    </div>
                </div>
                """
                st.markdown(success_html, unsafe_allow_html=True)
                
                # Botón de Descarga
                st.download_button(
                    label="DESCARGAR MATRIZ EXCEL ⚡",
                    data=processed_file_data,
                    file_name="Extraccion_Centralizada_EXXO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Falla de síntesis en el nodo de procesamiento: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

# FOOTER
st.markdown('<div class="footer">EXXO DATA SYSTEMS © 2026<br><span style="font-size: 0.6rem; opacity: 0.5;">Advanced Algorithmic Extractor</span></div>', unsafe_allow_html=True)
