import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import time

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO (BRANDING EXXO)
st.set_page_config(page_title="EXXO - Data Intelligence", layout="wide")

# ISOTIPO Y CSS PARA IMPACTO VISUAL
EXXO_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0A0A0B !important;
        font-family: 'Inter', sans-serif;
        color: #D0D0D0;
    }

    /* HEADER */
    .exxo-header {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 40px;
    }

    /* CARGADOR DE ARCHIVOS ESTILIZADO */
    .stFileUploader {
        border: 2px dashed #00D9FF !important;
        border-radius: 30px !important;
        background: rgba(0, 217, 255, 0.02) !important;
        padding: 30px !important;
    }

    /* BOTONES EXXO */
    div.stButton > button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        padding: 15px 30px !important;
        width: 100% !important;
        transition: 0.3s all !important;
    }
    
    div.stButton > button:hover {
        background: #00D9FF !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.4) !important;
    }

    /* TABLAS */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 20px !important;
        overflow: hidden !important;
    }

    h1, h2 { color: #FFFFFF !important; font-weight: 900 !important; letter-spacing: -2px !important; }
    .cyan-text { color: #00D9FF; }
</style>
"""

st.markdown(EXXO_THEME, unsafe_allow_html=True)

# ISOTIPO SVG OFICIAL
ISOTIPO_SVG = """
<div class="exxo-header">
    <svg width="50" height="50" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="45" stroke="#00D9FF" stroke-width="8" />
        <path d="M30 60L50 40L70 60" stroke="#00D9FF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    <div>
        <h1 style="margin:0; font-size: 28px;">EXXO</h1>
        <p style="margin:0; font-size: 10px; color: #00D9FF; letter-spacing: 4px; font-weight: bold;">DATA INTELLIGENCE</p>
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
