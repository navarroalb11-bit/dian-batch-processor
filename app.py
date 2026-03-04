import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import time
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO (BRANDING EXXO)
st.set_page_config(page_title="EXXO - Data Extraction Systems", layout="wide")

# Helpers
def load_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

base_dir = os.path.dirname(os.path.dirname(__file__))
logo_path = os.path.join(base_dir, "exxo logo isotipo_Mesa de trabajo 1.jpg")
logo_b64 = load_image_as_base64(logo_path)
logo_img_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" class="top-logo">' if logo_b64 else '<div class="top-logo-placeholder"></div>'

# ISOTIPO Y CSS ESTRICTO BASADO EN LA IMAGEN
EXXO_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #121A20 !important; /* Azul/Gris ultra oscuro de la imagen */
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }

    /* Ocultar elementos por defecto de Streamlit */
    header { visibility: hidden !important; }
    .css-15zrgzn { display: none !important; }

    /* Contenedor central (para que no ocupe todo el ancho exageradamente) */
    .block-container {
        max-width: 1000px !important;
        padding-top: 2rem !important;
    }

    /* TOP BAR EXACTA - NAVBAR */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 1rem;
        margin-bottom: 4rem;
    }

    .nav-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-titles {
        display: flex;
        flex-direction: column;
    }

    .nav-maintitle {
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #FFFFFF;
        line-height: 1;
    }

    .nav-subtitle {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: #00D9FF;
        margin-top: 4px;
        text-transform: uppercase;
    }

    .nav-right {
        display: flex;
        align-items: center;
    }

    /* Isotipo a la derecha */
    .top-logo {
        height: 45px;
        border-radius: 8px;
    }
    
    .top-logo-placeholder {
        width: 45px;
        height: 45px;
        border-radius: 8px;
        background: rgba(0, 217, 255, 0.1);
        border: 1px solid #00D9FF;
    }

    /* ANIMACIÓN DEL TÍTULO PRINCIPAL (GLOW PULSANTE) */
    @keyframes textGlow {
        0%, 100% { text-shadow: 0 0 10px rgba(0, 217, 255, 0.4); }
        50% { text-shadow: 0 0 30px rgba(0, 217, 255, 0.9), 0 0 10px rgba(0, 217, 255, 0.5); }
    }
    
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* HEADERS CENTRALES */
    .hero-section {
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) ease-out;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    .hero-title span {
        color: #00D9FF;
        animation: textGlow 3s infinite ease-in-out;
        display: inline-block;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #A1A1AA;
        font-weight: 400;
        animation: fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) ease-out;
    }

    .hero-subtitle span {
        color: #8B5CF6; /* Formatos en mora/violeta */
        font-weight: 600;
    }


    /* ZONA DE CARGA EXACTA */
    /* Uploader Dropzone */
    div[data-testid="stFileUploadDropzone"] {
        border: 1px dashed rgba(0, 217, 255, 0.4) !important;
        border-radius: 12px !important;
        background-color: rgba(255,255,255,0.02) !important;
        padding: 5rem 2rem !important;
        transition: all 0.3s ease !important;
        animation: fadeUp 1.4s cubic-bezier(0.16, 1, 0.3, 1) ease-out;
    }

    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #00D9FF !important;
        background-color: rgba(0, 217, 255, 0.05) !important;
    }

    /* Iconos falsos antes del texto st.uploader */
    div[data-testid="stFileUploadDropzone"]::before {
        content: "";
        display: block;
        width: 140px;
        height: 60px;
        margin: 0 auto 1.5rem auto;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40"><rect x="10" y="0" width="30" height="35" rx="6" fill="rgba(0,217,255,0.1)" stroke="%2300D9FF" stroke-width="1.5"/><rect x="60" y="0" width="30" height="35" rx="6" fill="rgba(139,92,246,0.1)" stroke="%238B5CF6" stroke-width="1.5"/></svg>') center/contain no-repeat;
    }

    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.25rem;
        color: #FFFFFF;
        font-weight: 600;
    }
    
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p:nth-child(2) {
        font-size: 0.9rem;
        color: #A1A1AA;
        font-weight: 400;
    }

    /* Modificando el botón Browse nativo de Streamlit para que luzca como Selection Button Cyan */
    div[data-testid="stFileUploadDropzone"] button {
        background-color: #00D9FF !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        margin-top: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.2) !important;
    }
    
    div[data-testid="stFileUploadDropzone"] button:hover {
        background-color: #00B8D9 !important;
        transform: translateY(-2px);
    }
    .stFileUploader > div > div { background-color: transparent !important; }

    /* TABLA DE MONITOR */
    .monitor-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 3.5rem;
        margin-bottom: 1rem;
    }

    .monitor-title h3 {
        margin: 0;
        font-size: 1.15rem;
        color: #FFFFFF;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .monitor-title h3::before {
        content: "";
        display: block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00D9FF;
    }

    .monitor-status {
        font-size: 0.8rem;
        color: #A1A1AA;
        background: rgba(255,255,255,0.05);
        padding: 5px 15px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Ajuste visual general al DataFrame de Streamlit */
    [data-testid="stDataFrame"] {
        background-color: rgba(13, 23, 28, 0.6) !important;
        border: 1px solid rgba(0, 217, 255, 0.1) !important;
        border-radius: 8px !important;
    }

    /* BOTONES GLOBALES (Incluido el de Descargas Final) */
    .stDownloadButton > button {
        background-color: #00D9FF !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 1rem 2rem !important;
        width: 100% !important;
        max-width: 400px;
        margin: 2rem auto 0 auto !important;
        display: block !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #00B8D9 !important;
        transform: translateY(-2px);
        box-shadow: 0 0 40px rgba(0, 217, 255, 0.6) !important;
    }
</style>
"""

st.markdown(EXXO_THEME, unsafe_allow_html=True)

# 2. INYECCIÓN DEL NAVBAR Y HERO
st.markdown(f"""
<div class="nav-bar">
    <div class="nav-left">
        <div class="nav-titles">
            <span class="nav-maintitle">EXXO</span>
            <span class="nav-subtitle">DATA EXTRACTION SYSTEMS</span>
        </div>
    </div>
    <div class="nav-right">
        {logo_img_tag}
    </div>
</div>

<div class="hero-section">
    <div class="hero-title">Centralized <span>Extraction</span> Node</div>
    <div class="hero-subtitle">Securely process your financial documents. Supported formats:<br><span>XML, TXT</span></div>
</div>
""", unsafe_allow_html=True)

# 3. LÓGICA DE EXTRACCIÓN Y ORDENAMIENTO DE LAS COLUMNAS EXACTAS QUE EL USUARIO PIDIÓ ANTES
def extract_data(files):
    data_list = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(files):
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            
            def find_text(tag_name):
                for elem in root.iter():
                    if elem.tag.endswith(f"}}{tag_name}") or elem.tag == tag_name:
                        return elem.text.strip() if elem.text else None
                return None
            
            fecha = find_text("IssueDate")
            factura = find_text("ID")
            nit = find_text("CompanyID")
            subtotal = find_text("LineExtensionAmount")
            iva = find_text("TaxAmount")
            total = find_text("PayableAmount")
            
            if nit: nit = nit.replace(".", "").replace(",", "").replace("-", "")
            
            try: subtotal = float(subtotal) if subtotal else 0.0
            except: subtotal = 0.0
            try: iva = float(iva) if iva else 0.0
            except: iva = 0.0
            try: total = float(total) if total else 0.0
            except: total = 0.0
            
            data_list.append({
                "NÚMERO DE FACTURA": factura if factura else "N/A",
                "NIT DEL PROVEEDOR": nit if nit else "N/A",
                "SUBTOTAL": subtotal,
                "IVA": iva,
                "VALOR TOTAL": total,
                "ESTADO": "Procesado"  # Simulación estética
            })
            
            progress = (i + 1) / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Evaluando Nodos... {int(progress*100)}%")
            time.sleep(0.05)
            
        except ET.ParseError:
            pass # Skip silently or log invalid for this UI
        except Exception as e:
            pass
            
    progress_bar.empty()
    status_text.empty()
    
    # Intento de Ordenar por Plantilla Base si existe (Lógica que pediste antes)
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Base_Datos_Facturas (2).xlsx")
    if os.path.exists(template_path) and data_list:
        try:
            template_df = pd.read_excel(template_path)
            template_cols = template_df.columns.tolist()
            
            mapped_data = []
            for row in data_list:
                new_row = {}
                for tcol in template_cols:
                    t_upper = str(tcol).upper()
                    if "FACTURA" in t_upper or ("NUM" in t_upper and "FACT" in t_upper): new_row[tcol] = row.get("NÚMERO DE FACTURA", "")
                    elif "NIT" in t_upper or "RUT" in t_upper or "ID " in t_upper: new_row[tcol] = row.get("NIT DEL PROVEEDOR", "")
                    elif "SUBTOTAL" in t_upper or "BASE" in t_upper: new_row[tcol] = row.get("SUBTOTAL", 0.0)
                    elif "IVA" in t_upper or "IMPUESTO" in t_upper: new_row[tcol] = row.get("IVA", 0.0)
                    elif "TOTAL" in t_upper: new_row[tcol] = row.get("VALOR TOTAL", 0.0)
                    else: new_row[tcol] = "" 
                mapped_data.append(new_row)
            return pd.DataFrame(mapped_data)
        except:
            return pd.DataFrame(data_list)
    else:
        return pd.DataFrame(data_list)

# 4. INTERACCION UI - DROPZONE
uploaded_files = st.file_uploader("Arrastre y suelte sus archivos aquí", accept_multiple_files=True, type=['xml', 'txt'])

# 5. TABLA DE DATOS RESULTADO
if uploaded_files:
    st.markdown("""
    <div class="monitor-title">
        <h3>Monitor de Extracción en Tiempo Real</h3>
        <span class="monitor-status">🔄 Actualizado hace un momento</span>
    </div>
    """, unsafe_allow_html=True)
    
    df = extract_data(uploaded_files)
    st.session_state['data'] = df
    
    # Muestra visual adaptativa (en caso de que la plantilla sea la real)
    # Mostramos el df directo para facilidad
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # BOTÓN DE DESCARGA GLOW CYAN (Centrado abajo, tal cual el mockup)
    towrite = BytesIO()
    try:
        st.session_state['data'].to_excel(towrite, index=False, engine='xlsxwriter')
    except ImportError:
        st.session_state['data'].to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    
    st.download_button(
        label="📥 Descargar Base de Datos en Excel",
        data=towrite,
        file_name=f"EXXO_Reporte_{int(time.time())}.xlsx",
        mime="application/vnd.ms-excel"
    )

# FOOTER MOCKUP
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.5; font-size: 10px; letter-spacing: 5px; color: #FFFFFF;'>EXXO INDUSTRIAL INTELLIGENCE © 2024</p>", unsafe_allow_html=True)
