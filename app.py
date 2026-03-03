import streamlit as st
import os
import shutil
import tempfile
from core.batch_processor import BatchProcessor

# PAGE CONFIG
st.set_page_config(
    page_title="Extractor Electrónico - DIAN",
    page_icon="⚡",
    layout="centered"
)

# PERSISTENT STORAGE
# Directorio local donde vivirá la plantilla del usuario para siempre
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
st.title("⚡ Procesador Batch DIAN")
st.markdown('<p class="muted-text">Automatización Contable Inteligente. Sube tus facturas y obtén tu reporte.</p>', unsafe_allow_html=True)

# Verifica si ya existe una plantilla guardada
has_template = os.path.exists(SAVED_TEMPLATE_PATH)

# --- SECTION 1: EXCEL TEMPLATE (OPCIONAL/MEMORIA) ---
st.markdown("### Configuración de Plantilla")

if has_template:
    st.markdown("""
    <div class="info-box">
        <b>✅ Tienes una plantilla Excel guardada y activa.</b><br>
        El sistema recordará tus columnas automáticamente. No necesitas subirla de nuevo a menos que quieras cambiarla.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️ Aún no tienes una plantilla configurada. Sube tu Excel vacío con los encabezados e intentaremos autodetectarlos.")

with st.expander("Actualizar / Subir nueva Plantilla Excel"):
    st.markdown('<p class="muted-text">Sube tu archivo .xlsx original. Mantendremos tus colores y diseño intactos.</p>', unsafe_allow_html=True)
    excel_file = st.file_uploader("Sube tu plantilla", type=["xlsx"], label_visibility="collapsed")
    
    if excel_file:
        # Guardamos la plantilla persistentemente
        with open(SAVED_TEMPLATE_PATH, "wb") as f:
            f.write(excel_file.getvalue())
        
        st.success("¡Plantilla actualizada y guardada exitosamente!")
        st.experimental_rerun() # Refresh app to show the "active template" box

st.markdown("---")

# --- SECTION 2: XML FILES UPLOAD ---
st.markdown("### Procesamiento de Facturas (XML)")
st.markdown('<p class="muted-text">Arrastra todos tus archivos XML aquí.</p>', unsafe_allow_html=True)
xml_files = st.file_uploader("Sube tus archivos XML", type=["xml"], accept_multiple_files=True, label_visibility="collapsed")

if xml_files:
    st.success(f"✅ {len(xml_files)} archivos XML listos para extraer.")

st.markdown("---")

# --- SECTION 3: PROCESS AND EXPORT ---
if st.button("🚀 Procesar y Generar Reporte", disabled=not (xml_files and has_template)):
    if not has_template:
        st.error("Por favor, sube una plantilla de Excel primero.")
    elif not xml_files:
        st.warning("Debes subir al menos un archivo XML.")
    else:
        with st.spinner("Leyendo facturas y anexando a tu Excel..."):
            temp_dir = tempfile.mkdtemp()
            input_dir = os.path.join(temp_dir, "input_xmls")
            os.makedirs(input_dir, exist_ok=True)
            output_excel = os.path.join(temp_dir, "Facturacion_Consolidada.xlsx")
            
            try:
                # 1. Guardar XMLs adjuntos en el temp dir
                for xml_f in xml_files:
                    xml_path = os.path.join(input_dir, xml_f.name)
                    with open(xml_path, "wb") as f:
                        f.write(xml_f.getvalue())
                        
                # 2. Iniciar el motor que preserva formato (apunta a la plantilla persistente)
                processor = BatchProcessor(SAVED_TEMPLATE_PATH)
                processor.process_folder(input_dir, output_excel)
                
                # 3. Mostrar la auto-detección (Opcional pero muy útil para el usuario)
                if processor.mapping:
                    mapeos_txt = ", ".join([f'"{k}"' for k in processor.mapping.keys()])
                    st.success(f"🤖 Extraímos exitosamente la data de estas columnas detectadas: {mapeos_txt}")
                else:
                    st.warning("No se encontraron coincidencias automáticas entre tus encabezados y nuestras reglas.")

                # 4. Ofrecer la descarga de la App
                if os.path.exists(output_excel):
                    with open(output_excel, "rb") as f:
                        processed_file_data = f.read()
                        
                    st.download_button(
                        label="⬇️ Descargar Reporte Final (Con Diseño Original)",
                        data=processed_file_data,
                        file_name="Facturas_Extraidas_Completadas.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            except Exception as e:
                st.error(f"Error procesando los archivos: {str(e)}")
            
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
