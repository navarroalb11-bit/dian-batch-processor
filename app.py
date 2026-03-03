import streamlit as st
import os
import shutil
import tempfile
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="Extractor Electrónico - DIAN a Siigo",
    page_icon="⚡",
    layout="centered"
)

# PERSISTENT STORAGE
PERSISTENT_DIR = os.path.join(os.path.dirname(__file__), "saved_template")
os.makedirs(PERSISTENT_DIR, exist_ok=True)
SAVED_TEMPLATE_PATH = os.path.join(PERSISTENT_DIR, "plantilla_activa.xlsx")

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
    /* Text Inputs and Number Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #2b2b2e;
        color: white;
        border: 1px solid #1f538d;
        border-radius: 6px;
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
        height: 50px;
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
        height: 50px;
    }
    .stDownloadButton > button:hover {
        background-color: #008f4c !important;
    }
    /* Muted Text */
    .muted-text {
        color: #a0a0a0;
        font-size: 0.9em;
    }
    /* Info Box */
    .info-box {
        background-color: #14375e;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00a859;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("⚡ Integración Facturas a Siigo")
st.markdown('<p class="muted-text">Automatización Contable Inteligente. Sube tus facturas y obtén tu comprobante configurado para Siigo.</p>', unsafe_allow_html=True)

has_template = os.path.exists(SAVED_TEMPLATE_PATH)

# --- SECTION 1: EXCEL TEMPLATE ---
st.markdown("### 1. Plantilla Siigo")

if has_template:
    st.markdown("""
    <div class="info-box">
        <b>✅ Plantilla Activa.</b><br>
        El sistema ya conoce tu modelo de importación de Siigo.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️ Sube tu Excel 'Modelo de importación de comprobantes' (con los encabezados de Siigo).")

with st.expander("Actualizar / Subir nueva Plantilla Excel"):
    excel_file = st.file_uploader("Sube tu plantilla", type=["xlsx"], label_visibility="collapsed")
    if excel_file:
        with open(SAVED_TEMPLATE_PATH, "wb") as f:
            f.write(excel_file.getvalue())
        st.success("¡Plantilla actualizada y guardada exitosamente!")
        st.experimental_rerun()

st.markdown("---")

# --- SECTION 2: XML FILES UPLOAD ---
st.markdown("### 2. Facturas de la DIAN (XML)")
xml_files = st.file_uploader("Sube tus archivos XML", type=["xml"], accept_multiple_files=True, label_visibility="collapsed")

if xml_files:
    st.success(f"✅ {len(xml_files)} archivos XML listos.")

st.markdown("---")

# --- SECTION 3: CONFIGURACIÓN CONTABLE & MATCH ---
st.markdown("### 3. Configuración del Comprobante")
st.markdown('<p class="muted-text">Define los parámetros contables para este lote de facturas.</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1.5])
with col1:
    debit_acc = st.text_input("Cuenta Gasto/Costo (Débito)", placeholder="Ej. 513505")
with col2:
    credit_acc = st.text_input("Cuenta por Pagar (Crédito)", placeholder="Ej. 233595")
with col3:
    start_consec = st.number_input("🚨 Consecutivo Inicial", min_value=1, value=1, step=1, help="El número del comprobante con el que empezará el lote de facturas.")

st.markdown("---")

# --- SECTION 4: PROCESS AND EXPORT ---
if st.button("🚀 Iniciar Extracción y Generar Comprobante", disabled=not (xml_files and has_template)):
    if not has_template:
        st.error("Por favor, sube una plantilla de Excel primero.")
    elif not xml_files:
        st.warning("Debes subir al menos un archivo XML.")
    elif not debit_acc or not credit_acc:
        st.warning("⚠️ Debes digitar la Cuenta Débito y la Cuenta Crédito para asegurar que la partida doble cuadre en Siigo.")
    else:
        with st.spinner("Construyendo Comprobante de Siigo por partida doble..."):
            temp_dir = tempfile.mkdtemp()
            input_dir = os.path.join(temp_dir, "input_xmls")
            os.makedirs(input_dir, exist_ok=True)
            output_excel = os.path.join(temp_dir, "Comprobante_Siigo_Automatizado.xlsx")
            
            try:
                for xml_f in xml_files:
                    xml_path = os.path.join(input_dir, xml_f.name)
                    with open(xml_path, "wb") as f:
                        f.write(xml_f.getvalue())
                        
                # Inicializamos el motor con cuentas y el consecutivo inicial elegido por el usuario
                processor = BatchProcessor(
                    template_path=SAVED_TEMPLATE_PATH,
                    debit_account=debit_acc.strip(),
                    credit_account=credit_acc.strip(),
                    start_consecutive=start_consec
                )
                
                processor.process_folder(input_dir, output_excel)
                
                if processor.mapping:
                    st.success("🤖 Extracción finalizada. Formato y codificación de Siigo aplicada con éxito.")

                if os.path.exists(output_excel):
                    with open(output_excel, "rb") as f:
                        processed_file_data = f.read()
                        
                    st.download_button(
                        label="⬇️ Descargar Comprobante Contable (.xlsx)",
                        data=processed_file_data,
                        file_name="Comprobante_Siigo_Automatizado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            except Exception as e:
                st.error(f"Error procesando los archivos: {str(e)}")
            
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
