import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import time
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO (BRANDING EXXO)
st.set_page_config(page_title="EXXO - Data Extraction Systems", layout="wide", initial_sidebar_state="collapsed")

# Helpers: Búsqueda dinámica para Streamlit Cloud (varios paths posibles)
def load_image_as_base64(filename):
    paths_to_try = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), filename),
        os.path.join(os.path.dirname(__file__), filename),
        filename
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import time
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO (BRANDING EXXO)
st.set_page_config(page_title="EXXO - Data Extraction Systems", layout="wide", initial_sidebar_state="collapsed")

# Hardcoded Base64 for the logo (isotipo oxxo png_Mesa de trabajo 1.png) to guarantee Cloud Rendering
LOGO_BASE64 = "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

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

    /* ANIMACIÓN DEL TÍTULO PRINCIPAL Y LOGO (GLOW PULSANTE) */
    @keyframes textGlow {
        0%, 100% { filter: drop-shadow(0 0 10px rgba(0, 217, 255, 0.4)); text-shadow: 0 0 10px rgba(0, 217, 255, 0.4); }
        50% { filter: drop-shadow(0 0 25px rgba(0, 217, 255, 0.9)); text-shadow: 0 0 30px rgba(0, 217, 255, 0.9), 0 0 10px rgba(0, 217, 255, 0.5); }
    }
    
    .glow-logo {
        animation: textGlow 3s infinite ease-in-out;
    }

    /* Isotipo a la izquierda/derecha */
    .top-logo {
        height: 45px;
        border-radius: 8px; /* Opcional por si la imagen tiene fondos duros */
    }
    
    .top-logo-placeholder {
        width: 45px;
        height: 45px;
        border-radius: 8px;
        background: rgba(0, 217, 255, 0.1);
        border: 1px solid #00D9FF;
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

    /* ZONA DE CARGA EXACTA - OVERRIDE FORZADO A BLANCOS DE STREAMLIT */
    .stFileUploader > div:first-child {
        background-color: transparent !important; 
    }
    
    section[data-testid="stFileUploadDropzone"],
    div[data-testid="stFileUploadDropzone"] {
        border: 1px dashed rgba(0, 217, 255, 0.4) !important;
        border-radius: 12px !important;
        background-color: rgba(255,255,255,0.03) !important; /* Forza fondo oscuro en vez del blanco */
        padding: 4rem 2rem !important;
        transition: all 0.3s ease !important;
        animation: fadeUp 1.4s cubic-bezier(0.16, 1, 0.3, 1) ease-out;
    }

    section[data-testid="stFileUploadDropzone"]:hover,
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #00D9FF !important;
        background-color: rgba(0, 217, 255, 0.08) !important;
    }

    /* Ocultar iconos de nube/basura default de Streamlit */
    div[data-testid="stFileUploadDropzone"] svg {
        display: none !important;
    }
    
    /* Reemplazar con iconos corporativos */
    div[data-testid="stFileUploadDropzone"]::before {
        content: "";
        display: block;
        width: 140px;
        height: 60px;
        margin: 0 auto 1.5rem auto;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40"><rect x="10" y="0" width="30" height="35" rx="6" fill="rgba(0,217,255,0.1)" stroke="%2300D9FF" stroke-width="1.5"/><rect x="60" y="0" width="30" height="35" rx="6" fill="rgba(139,92,246,0.1)" stroke="%238B5CF6" stroke-width="1.5"/></svg>') center/contain no-repeat;
    }

    div[data-testid="stFileUploadDropzone"] span, 
    div[data-testid="stFileUploadDropzone"] p,
    div[data-testid="stFileUploadDropzone"] small {
        color: #A1A1AA !important; /* Fuerza grises frente al texto negro default */
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
        {logo_img_tag}
        <div class="nav-titles">
            <span class="nav-maintitle">EXXO</span>
            <span class="nav-subtitle">DATA EXTRACTION SYSTEMS</span>
        </div>
    </div>
    <div class="nav-right">
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
