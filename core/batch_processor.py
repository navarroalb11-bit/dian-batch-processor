import os
import glob
from lxml import etree
import openpyxl

class BatchProcessor:
    # Diccionario inteligente para autodetectar columnas sin intervención humana.
    # Ajustado específicamente para la plantilla "Modelo de importación de comprobantes contables" de Siigo
    ALIAS_DICT = {
        "tercero": "CompanyID", # NIT
        "identificaci\u00f3n tercero": "CompanyID",
        "descripci": "ID",         # Número factura
        "fecha de elaboraci": "IssueDate", 
        "d\u00e9bito": "LineExtensionAmount",  # Base (Débito)
        "debito": "LineExtensionAmount", 
        "cr\u00e9dito": "PayableAmount",     # Total (Crédito)
        "credito": "PayableAmount",
        # Auto-relleno fijo según requerimiento del cliente:
        "tipo de comprobante": "_FIXED_CC",
        "sigla moneda": "_FIXED_COP",
        "tasa de cambio": "_FIXED_1",
    }
    
    # Campo oculto de IVA que el UBL2.1 trae por defecto a nivel cabecera
    IVA_XML_TAG = "TaxAmount"

    def __init__(self, template_path: str):
        """
        Inicializa el procesador leyendo directamente la plantilla de Excel del usuario (Siigo).
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
            
        self.template_path = template_path
        
        # Leemos los encabezados usando openpyxl para mapearlos a los tags
        wb = openpyxl.load_workbook(self.template_path, data_only=True)
        sheet = wb.active
        
        self.columns_order = []
        self.col_indices = {}
        
        # Asumimos que la fila 1 tiene los encabezados
        for cell in sheet[1]:
            if cell.value:
                col_name = str(cell.value).strip()
                self.columns_order.append(col_name)
                self.col_indices[col_name] = cell.column
                
        # Construimos el mapeo automático usando inteligencia de alias
        self.mapping = {}
        for col_name in self.columns_order:
            xml_tag_or_fixed = self._infer_tag(col_name)
            if xml_tag_or_fixed:
                self.mapping[col_name] = xml_tag_or_fixed
                
        # Guardamos referencias a las columnas Débito y Crédito para manipularlas
        self.debito_col = next((col for col in self.mapping if "debito" in col.lower() or "d\u00e9bito" in col.lower()), None)
        self.credito_col = next((col for col in self.mapping if "credito" in col.lower() or "cr\u00e9dito" in col.lower()), None)
        
        # Namespaces comunes usados en la DIAN (UBL 2.1)
        self.namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }

    def _infer_tag(self, col_name: str) -> str:
        """Busca coincidencias lógicas entre el nombre de la columna y los campos XML o fijos"""
        col_lower = col_name.lower()
        for key, tag in self.ALIAS_DICT.items():
            if key in col_lower:
                return tag
        return None

    def _extract_numeric(self, str_value: str) -> float:
        """Helper para parsear texto a número de forma segura."""
        if not str_value:
            return 0.0
        try:
            if '.' in str_value and str_value.replace('.', '', 1).isdigit():
                return float(str_value)
            elif str_value.isdigit():
                return float(str_value)
            return 0.0
        except:
            return 0.0

    def parse_single_xml_totals(self, xml_path: str) -> list:
        """
        Procesa el XML y extrae la información.
        Genera TRES filas para la contabilidad (Gasto, Impuesto, Pago) 
        y autocompleta los campos estáticos.
        """
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            # --- 1. Extraer los datos compartidos (Cabecera) ---
            shared_data = {}
            for excel_col, xml_tag in self.mapping.items():
                
                # Manejar valores fijos primero
                if xml_tag == "_FIXED_CC":
                    shared_data[excel_col] = "CC"
                    continue
                elif xml_tag == "_FIXED_COP":
                    shared_data[excel_col] = "COP"
                    continue
                elif xml_tag == "_FIXED_1":
                    shared_data[excel_col] = 1
                    continue
                
                # Búsqueda XPath para tags dinámicos
                xpath_expr = f"//*[local-name()='{xml_tag}']"
                elements = root.xpath(xpath_expr, namespaces=self.namespaces)
                
                value = None
                if elements:
                    for el in elements:
                        if el.text and el.text.strip():
                            value = el.text.strip()
                            break
                shared_data[excel_col] = value

            # --- 2. Encontrar valores monetarios críticos ---
            # El alias dict dice que el DÉBITO mapeaba al Subtotal (Base)
            base_val = 0.0
            if self.debito_col and self.debito_col in shared_data:
                base_val = self._extract_numeric(shared_data[self.debito_col])
                
            # El alias dict dice que el CRÉDITO mapeaba al Total (Pago)
            total_val = 0.0
            if self.credito_col and self.credito_col in shared_data:
                total_val = self._extract_numeric(shared_data[self.credito_col])
                
            # Extraemos manualmente el IVA (TaxAmount no está en el Excel directamente, lo forzamos)
            iva_val = 0.0
            iva_elements = root.xpath(f"//*[local-name()='{self.IVA_XML_TAG}']", namespaces=self.namespaces)
            if iva_elements:
                for el in iva_elements:
                    if el.text and el.text.strip():
                        iva_val = self._extract_numeric(el.text.strip())
                        break

            # --- 3. Construir las 3 filas (Triple Entry Ledger para Siigo) ---
            rows_to_insert = []
            
            # Fila A (Gasto): Base al Débito, Crédito = 0
            row_gasto = shared_data.copy()
            if self.debito_col: row_gasto[self.debito_col] = base_val
            if self.credito_col: row_gasto[self.credito_col] = 0.0
            rows_to_insert.append(row_gasto)
            
            # Fila B (Impuesto): IVA al Débito, Crédito = 0
            row_iva = shared_data.copy()
            if self.debito_col: row_iva[self.debito_col] = iva_val
            if self.credito_col: row_iva[self.credito_col] = 0.0
            # (Opcionalmente, Siigo recomienda que la Descripción de la fila de IVA diga "IVA"...)
            # Si quieres que la descripción diga IVA, se añadiría aquí, pero lo dejamos idéntico 
            # a la cabecera (número de factura) según tus lineamientos.
            rows_to_insert.append(row_iva)
            
            # Fila C (Pago): Crédito al Total, Débito = 0
            row_pago = shared_data.copy()
            if self.credito_col: row_pago[self.credito_col] = total_val
            if self.debito_col: row_pago[self.debito_col] = 0.0
            rows_to_insert.append(row_pago)
                
            return rows_to_insert
            
        except Exception as e:
            print(f"\n[Error] falló el procesamiento de {xml_path}: {str(e)}")
            return []

    def process_folder(self, folder_path: str, output_excel_path: str):
        """
        Extrae data de los XMLs y los inserta en el Excel preservando diseño y formato.
        Añade múltiples filas (3) por comprobante.
        """
        search_pattern = os.path.join(folder_path, '*.xml')
        xml_files = glob.glob(search_pattern)
        
        total_files = len(xml_files)
        if total_files == 0:
            print(f"⚠️ No se encontraron archivos XML en: {folder_path}")
            return
            
        # 1. Cargamos el Excel original SIN romper formatos
        wb = openpyxl.load_workbook(self.template_path)
        sheet = wb.active
        start_row = sheet.max_row + 1
        
        # 2. Procesamos y AÑADIMOS (append)
        for i, xml_file in enumerate(xml_files):
            data_rows = self.parse_single_xml_totals(xml_file)
            
            for data_row in data_rows:
                if data_row:
                    for col_name, value in data_row.items():
                        if col_name in self.col_indices:
                            col_idx = self.col_indices[col_name]
                            sheet.cell(row=start_row, column=col_idx, value=value)
                    
                    if "_Archivo_Origen" in self.col_indices:
                        col_idx = self.col_indices["_Archivo_Origen"]
                        sheet.cell(row=start_row, column=col_idx, value=os.path.basename(xml_file))
                        
                    start_row += 1
                
        # 3. Guardado final preservado
        wb.save(output_excel_path)
        print(f"\n✅ Archivo guardado correctamente en: {output_excel_path}")
