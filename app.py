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

# Helpers
def load_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Cargar Logo / Isotipo
base_dir = os.path.dirname(os.path.dirname(__file__))
logo_path = os.path.join(base_dir, "exxo logo isotipo_Mesa de trabajo 1.jpg")
robot_path = os.path.join(base_dir, "referencia.png") # Nota: El robot debe venir de un crop transparente, vamos a usar CSS para simularlo en la maqueta si no hay robot aislado.

logo_b64 = load_image_as_base64(logo_path)
robot_b64 = load_image_as_base64(robot_path)

logo_img_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo-img">' if logo_b64 else '<div class="logo-placeholder">EXXO</div>'

# === VARIABLES DE ESTILO Y DISEÑO ===
ST_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Base */
    .stApp {
        background-color: #0d1117; 
        font-family: 'Inter', sans-serif;
        color: #E6EDF3;
        /* Simular el fondo radial teñido oscuro de la referencia */
        background-image: radial-gradient(circle at center, #1b263b 0%, #0d1117 100%);
    }

    /* Animaciones Eyes / Matrix */
    @keyframes matrixGlitch {
        0% { background-position: 0% 0%; }
        100% { background-position: 0% 100%; }
    }
    
    @keyframes pulseGlow {
        0% { filter: drop-shadow(0 0 5px rgba(0, 217, 255, 0.4)); opacity: 0.8; }
        50% { filter: drop-shadow(0 0 25px rgba(0, 217, 255, 0.9)); opacity: 1; }
        100% { filter: drop-shadow(0 0 5px rgba(0, 217, 255, 0.4)); opacity: 0.8; }
    }

    /* Ocultar barra de headers de Streamlit */
    header { visibility: hidden !important; }
    .css-15zrgzn { display: none !important; }

    /* Contenedor Principal Glassmorphism */
    .block-container {
        padding: 2rem !important;
        max-width: 1000px;
        margin-top: 4rem;
        background: rgba(13, 17, 23, 0.45);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        z-index: 10;
    }

    /* Top Bar: Logo + Status */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .logo-img {
        height: 45px;
        border-radius: 8px;
    }

    .logo-placeholder {
        width: 45px;
        height: 45px;
        background: #00D9FF;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000;
        font-weight: bold;
    }

    .brand-text {
        display: flex;
        flex-direction: column;
    }

    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        line-height: 1;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .brand-title span {
        color: #00D9FF;
    }

    .brand-subtitle {
        font-size: 0.75rem;
        color: #8C98A4;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    .status-badge {
        background: rgba(39, 174, 96, 0.1);
        border: 1px solid rgba(39, 174, 96, 0.3);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.85rem;
        color: #A3B1C6;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-badge span {
        color: #27AE60;
        font-weight: 700;
    }

    /* Titulos minimalistas */
    h1.hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0px;
        line-height: 1.2;
    }

    h1.hero-title span {
        color: #00D9FF;
    }

    p.hero-subtitle {
        color: #8C98A4;
        font-size: 1.1rem;
        margin-top: 5px;
        margin-bottom: 40px;
    }

    /* Grid Layout: Drag & Drop + Robot */
    .main-grid {
        display: grid;
        grid-template-columns: 1.5fr 1fr;
        gap: 30px;
        align-items: center;
        position: relative;
    }

    /* Uploader Area Customization Glassmorphism */
    /* Streamlit Uploader Override */
    .stFileUploader {
        background-color: transparent !important;
        width: 100%;
    }
    
    .stFileUploader > div, .stFileUploader > div > div {
        background-color: transparent !important;
    }
    
    .stFileUploader label { display: none !important; }
    
    div[data-testid="stFileUploadDropzone"] {
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        padding: 4rem 1rem !important;
        transition: all 0.4s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #00D9FF !important;
        background-color: rgba(0, 217, 255, 0.05) !important;
        box-shadow: inset 0 0 30px rgba(0, 217, 255, 0.1);
    }

    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.8rem;
        color: #FFFFFF;
        font-weight: 700;
        text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p:nth-child(2) {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.5);
        font-weight: 400;
    }
    
    div[data-testid="stFileUploadDropzone"] button {
        background-color: rgba(255,255,255,0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        margin-top: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stFileUploadDropzone"] button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.3) !important;
    }

    /* Robot Container Simulación (Ya que no poseemos el asset png suelto, usamos el concepto interactivo) */
    .robot-container {
        position: relative;
        height: 300px;
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle, rgba(0,217,255,0.05) 0%, transparent 70%);
        border-radius: 20px;
    }

    .robot-avatar {
        width: 180px;
        height: 220px;
        background: url('https://cdn-icons-png.flaticon.com/512/2065/2065181.png') center/contain no-repeat; /* Placeholder Robot vector */
        filter: grayscale(1) brightness(0.8) drop-shadow(0 10px 15px rgba(0,0,0,0.5));
        transition: all 0.5s ease;
        position: relative;
    }

    /* Ojos del Robot - Estado Reposo */
    .robot-eyes {
        position: absolute;
        top: 38%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 60px;
        height: 15px;
        background: #111;
        border-radius: 5px;
        border: 1px solid #333;
        transition: all 0.3s ease;
        overflow: hidden;
    }

    /* Ojos del Robot - Estado Activo (Activado mediante clase "active") */
    .robot-avatar.active {
        filter: grayscale(0.2) brightness(1.2) drop-shadow(0 10px 20px rgba(0, 217, 255, 0.3));
    }

    .robot-avatar.active .robot-eyes {
        background: repeating-linear-gradient(
            0deg,
            #00D9FF,
            #00D9FF 2px,
            #0088AA 2px,
            #0088AA 4px
        );
        background-size: 100% 20px;
        border-color: #00D9FF;
        box-shadow: 0 0 20px #00D9FF, inset 0 0 10px #00D9FF;
        animation: matrixGlitch 1s linear infinite, pulseGlow 1.5s infinite;
    }

    /* Action Process/Download Buttons Centered */
    .action-area {
        display: flex;
        justify-content: center;
        margin-top: 3rem;
    }

    .stButton > button, .stDownloadButton > button {
        background: transparent !important;
        color: #FFFFFF !important;
        font-weight: 700;
        border: 1px solid rgba(0, 217, 255, 0.5) !important;
        border-radius: 30px !important;
        padding: 1rem 3rem !important;
        font-size: 1.15rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        max-width: 400px;
        margin: 0 auto;
        display: block;
        box-shadow: inset 0 0 10px rgba(0, 217, 255, 0.1), 0 4px 15px rgba(0, 217, 255, 0.1) !important;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: rgba(0, 217, 255, 0.15) !important;
        border-color: #00D9FF !important;
        box-shadow: inset 0 0 15px rgba(0, 217, 255, 0.3), 0 8px 30px rgba(0, 217, 255, 0.3) !important;
        transform: translateY(-2px);
    }
    
    .stButton > button:disabled {
        border-color: rgba(255,255,255,0.1) !important;
        color: rgba(255,255,255,0.3) !important;
        box-shadow: none !important;
        cursor: not-allowed;
        transform: none !important;
    }

    /* Hide empty elements Streamlit generated */
    .stMarkdown p { margin-bottom: 0px; }

</style>
"""

# INYECCIÓN DEL CSS
st.markdown(ST_STYLE, unsafe_allow_html=True)

# 1. TOP BAR
st.markdown(f"""
<div class="header-bar">
    <div class="brand">
        {logo_img_tag}
        <div class="brand-text">
            <div class="brand-title"><span>⚡</span>EXXO</div>
            <div class="brand-subtitle">Inteligencia Tributaria</div>
        </div>
    </div>
    <div class="status-badge">
        Motor de Extracción: <span>ACTIVO</span> - 6 Campos Clave
    </div>
</div>
""", unsafe_allow_html=True)

# 2. HEROS TEXT
st.markdown("""
<h1 class="hero-title"># Extractor Maestro de <span>XML</span></h1>
<p class="hero-subtitle">## Convierte facturas DIAN en bases de datos de Excel al instante.</p>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC & THE ROBOT ---
xml_files = st.file_uploader("Arrastra tus archivos aquí", type=["xml", "txt"], accept_multiple_files=True)

# Definir la clase activa para el robot usando CSS/HTML puro en base a si hay archivos
robot_state_class = "active" if xml_files and len(xml_files) > 0 else ""

st.markdown(f"""
<div class="robot-container">
    <div class="robot-avatar {robot_state_class}">
        <div class="robot-eyes"></div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 4. SUCCESS STATE COMPONENT ---
if xml_files:
    success_html = f"""
    <div style="background-color: rgba(39, 174, 96, 0.1); border: 1px solid rgba(39, 174, 96, 0.3); border-radius: 10px; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; margin-top: 1.5rem; backdrop-filter: blur(5px);">
        <div style="color: #E6EDF3; font-size: 0.95rem;">Archivos listos: <b>{len(xml_files)}</b></div>
        <div style="color: #27AE60; font-weight: bold; font-size: 0.95rem;">• Listo para extraer</div>
    </div>
    """
    st.markdown(success_html, unsafe_allow_html=True)


# --- 5. ACTION AREA (Generate Excel) ---
st.markdown('<div class="action-area">', unsafe_allow_html=True)
if st.button("Generar Base de Datos Excel", disabled=not bool(xml_files)):
    with st.spinner("EXXO leyendo y clasificando datos a velocidad Matrix..."):
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, "input_xmls")
        os.makedirs(input_dir, exist_ok=True)
        output_excel = os.path.join(temp_dir, "Extraccion_EXXO.xlsx")
        
        try:
            # A) Save files
            for xml_f in xml_files:
                xml_path = os.path.join(input_dir, xml_f.name)
                with open(xml_path, "wb") as f:
                    f.write(xml_f.getvalue())
                    
            # B) Process logic (UNCHANGED 6 fields)
            processor = BatchProcessor()
            stats = processor.process_folder(input_dir, output_excel)
            
            # C) Output
            if os.path.exists(output_excel):
                with open(output_excel, "rb") as f:
                    processed_file_data = f.read()
                    
                final_html = f"""
                <div style="text-align: center; margin-top: 1.5rem; color: #00D9FF; font-weight: 600; font-size: 1.1rem; filter: drop-shadow(0 0 10px rgba(0, 217, 255, 0.4));">
                    ¡Misión Cumplida! {stats['processed']} registros indexados con éxito.
                </div>
                """
                st.markdown(final_html, unsafe_allow_html=True)
                
                st.download_button(
                    label="Descargar Archivo .XLSX",
                    data=processed_file_data,
                    file_name="Extraccion_EXXO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error sistémico: {str(e)}")
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
st.markdown('</div>', unsafe_allow_html=True)
