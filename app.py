import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import time

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO (BRANDING EXXO)
st.set_page_config(page_title="EXXO - Data Intelligence", layout="wide")

# ISOTIPO Y CSS PARA IMPACTO VISUAL B2B / ENTERPRISE
EXXO_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #09090b !important; /* Zinc 950 - Ultra dark gray/black */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #fafafa;
    }

    /* Ocultar barra de headers de Streamlit */
    header { visibility: hidden !important; }
    .css-15zrgzn { display: none !important; }

    /* HEADER CORPORATIVO */
    .exxo-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-top: 10px;
        padding-bottom: 24px;
        border-bottom: 1px solid #27272a; /* Zinc 800 */
        margin-bottom: 32px;
    }

    /* CARGADOR DE ARCHIVOS ESTILIZADO - SAAS LOOK */
    .stFileUploader {
        border: 1px dashed #3f3f46 !important; /* Zinc 700 */
        border-radius: 8px !important;
        background-color: #18181b !important; /* Zinc 900 */
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }
    
    div[data-testid="stFileUploadDropzone"] {
        padding: 40px !important;
    }

    .stFileUploader:hover {
        border-color: #0284c7 !important; /* Sky 600 - Acción */
        background-color: #0c0a09 !important;
    }
    
    /* Textos del Uploader */
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        color: #e4e4e7;
        font-weight: 500;
    }
    
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p:nth-child(2) {
        font-size: 0.85rem;
        color: #a1a1aa; /* Zinc 400 */
        font-weight: 400;
        margin-top: 4px;
    }

    /* BOTONES EXXO - SOLID & TRUSTWORTHY */
    div.stButton > button, .stDownloadButton > button {
        background-color: #fafafa !important; /* Zinc 50 */
        color: #09090b !important; /* Texto Oscuro */
        border: 1px solid #e4e4e7 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    
    div.stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #f4f4f5 !important; /* Zinc 100 hover */
        border-color: #d4d4d8 !important;
        transform: translateY(-1px);
    }
    
    .stDownloadButton > button {
        background-color: #0284c7 !important; /* Principal Primary Call to Action */
        color: #ffffff !important;
        border: none !important;
        margin-top: 24px;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.2), 0 2px 4px -2px rgba(2, 132, 199, 0.2) !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #0369a1 !important; /* Darker Primary */
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.3), 0 4px 6px -4px rgba(2, 132, 199, 0.3) !important;
    }

    /* TABLAS - CORPORATE DATA GRID */
    [data-testid="stDataFrame"] {
        border: 1px solid #27272a !important; /* Zinc 800 */
        border-radius: 8px !important;
        background-color: #18181b !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1) !important;
    }

    /* TITULOS REDUCIDOS, ELEGANTES */
    h1, h2, h3 { 
        color: #fafafa !important; 
        font-weight: 600 !important; 
        letter-spacing: -0.025em !important; 
    }
    
    h2 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
    h3 { font-size: 1.1rem !important; border-bottom: 1px solid #27272a; padding-bottom: 12px; margin-bottom: 16px !important; color: #e4e4e7 !important; }
    
    p {
        color: #a1a1aa; /* Zinc 400 */
        font-size: 0.95rem;
    }
    
    /* ACENTOS SOBRIOS */
    .cyan-text { color: #0284c7; } /* Deep Sky Blue en lugar de Neon Cyan */
    
    /* Success / Alerts B2B */
    div[data-testid="stAlert"] {
        background-color: rgba(22, 163, 74, 0.1) !important;
        border: 1px solid rgba(22, 163, 74, 0.2) !important;
        color: #4ade80 !important;
        border-radius: 6px !important;
    }

</style>
"""

st.markdown(EXXO_THEME, unsafe_allow_html=True)

# ISOTIPO SVG OFICIAL - REFINADO (Trazo más fino, tipografía ajustada)
ISOTIPO_SVG = """
<div class="exxo-header">
    <svg width="36" height="36" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="42" stroke="#fafafa" stroke-width="4" />
        <path d="M30 65L50 35L70 65" stroke="#0ea5e9" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    <div>
        <h1 style="margin:0; font-size: 20px; font-weight: 700; letter-spacing: 0.5px;">EXXO</h1>
        <p style="margin:0; font-size: 10px; color: #a1a1aa; letter-spacing: 1px; font-weight: 500; text-transform: uppercase;">Data Intelligence</p>
    </div>
</div>
"""
st.markdown(ISOTIPO_SVG, unsafe_allow_html=True)

# 2. MOTOR DE EXTRACCIÓN (Lógica de los 6 campos)
def extract_data(files):
    data_list = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(files):
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            
            # Buscador recursivo agnóstico a los prefijos de espacios de nombres (namespaces) UBL 2.1
            def find_text(tag_name):
                for elem in root.iter():
                    if elem.tag.endswith(f"}}{tag_name}") or elem.tag == tag_name:
                        return elem.text.strip() if elem.text else None
                return None
            
            # Mapeo a etiquetas DIAN UBL 2.1
            fecha = find_text("IssueDate")
            factura = find_text("ID")
            nit = find_text("CompanyID")
            subtotal = find_text("LineExtensionAmount")
            iva = find_text("TaxAmount")
            total = find_text("PayableAmount")
            
            # Limpieza y conversión de Numeros (NIT sin puntos, guiones, y montos en floats)
            if nit: nit = nit.replace(".", "").replace(",", "").replace("-", "")
            
            try: subtotal = float(subtotal) if subtotal else 0.0
            except: subtotal = 0.0
            
            try: iva = float(iva) if iva else 0.0
            except: iva = 0.0
            
            try: total = float(total) if total else 0.0
            except: total = 0.0
            
            data_list.append({
                "Fecha": fecha if fecha else "N/A",
                "Factura": factura if factura else "N/A",
                "NIT": nit if nit else "N/A",
                "Subtotal": subtotal,
                "IVA": iva,
                "Total": total
            })
            
            progress = (i + 1) / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Sincronizando Nodo... {int(progress*100)}%")
            time.sleep(0.05) # Para efecto visual
            
        except ET.ParseError:
            st.error(f"El archivo '{file.name}' no tiene una estructura XML/TXT válida para procesar.")
        except Exception as e:
            st.error(f"Error sistémico en {file.name}: {str(e)}")
            
    progress_bar.empty()
    status_text.empty()
    
    # 2.1 ORDENAMIENTO BASADO EN PLANTILLA
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
                    if "FECHA" in t_upper: new_row[tcol] = row.get("Fecha", "")
                    elif "FACTURA" in t_upper or ("NUM" in t_upper and "FACT" in t_upper): new_row[tcol] = row.get("Factura", "")
                    elif "NIT" in t_upper or "RUT" in t_upper or "ID " in t_upper: new_row[tcol] = row.get("NIT", "")
                    elif "SUBTOTAL" in t_upper or "BASE" in t_upper: new_row[tcol] = row.get("Subtotal", 0.0)
                    elif "IVA" in t_upper or "IMPUESTO" in t_upper: new_row[tcol] = row.get("IVA", 0.0)
                    elif "TOTAL" in t_upper: new_row[tcol] = row.get("Total", 0.0)
                    else: new_row[tcol] = "" # Columna vacía si no machea
                mapped_data.append(new_row)
            return pd.DataFrame(mapped_data)
        except Exception as e:
            st.warning(f"Aviso: Plantilla encontrada pero no se pudo aplicar formato ({str(e)}). Usando estándar.")
            return pd.DataFrame(data_list)
    else:
        return pd.DataFrame(data_list)

# 3. INTERFAZ DE USUARIO
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown('## Nodo de <span class="cyan-text">Extracción</span>', unsafe_allow_html=True)
    st.write("Transformación masiva de facturación electrónica XML y TXT.")
    
    uploaded_files = st.file_uploader("Arrastra tus archivos aquí", accept_multiple_files=True, type=['xml', 'txt'])
    
    if uploaded_files:
        df = extract_data(uploaded_files)
        st.session_state['data'] = df
        st.success(f"✓ {len(uploaded_files)} documentos mapeados.")

with col2:
    st.markdown('### <span class="cyan-text">Monitor</span> de Datos', unsafe_allow_html=True)
    if 'data' in st.session_state:
        st.dataframe(st.session_state['data'], use_container_width=True)
        
        # BOTÓN DE DESCARGA REAL
        towrite = BytesIO()
        try:
            st.session_state['data'].to_excel(towrite, index=False, engine='xlsxwriter')
        except ImportError:
            # Fallback en caso de que xlsxwriter no esté instalado
            st.session_state['data'].to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        
        st.download_button(
            label="Generar Base de Datos Excel",
            data=towrite,
            file_name=f"EXXO_Reporte_{int(time.time())}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("Esperando flujo de entrada de datos...")

# FOOTER
st.markdown("<br><br><hr style='opacity:0.1'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.3; font-size: 10px; letter-spacing: 5px;'>EXXO INDUSTRIAL SYSTEMS // MEDELLÍN // 2026</p>", unsafe_allow_html=True)
