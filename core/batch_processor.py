import os
import glob
from lxml import etree
import openpyxl
import sys

class BatchProcessor:
    # Diccionario inteligente para autodetectar columnas sin intervención humana.
    ALIAS_DICT = {
        "fecha": "IssueDate",
        "emision": "IssueDate",
        "nit": "CompanyID",
        "cedula": "CompanyID",
        "identificacion": "CompanyID",
        "razon social": "RegistrationName",
        "nombre": "RegistrationName",
        "proveedor": "RegistrationName",
        "cliente": "RegistrationName",
        "subtotal": "LineExtensionAmount",
        "base": "TaxableAmount",
        "iva": "TaxAmount",
        "impuesto": "TaxAmount",
        "total": "PayableAmount",
        "numero": "ID",
        "factura": "ID",
        "consecutivo": "ID",
        "vencimiento": "DueDate",
    }

    def __init__(self, template_path: str):
        """
        Inicializa el procesador leyendo directamente la plantilla de Excel del usuario.
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
            
        self.template_path = template_path
        
        # Leemos los encabezados usando openpyxl para mapearlos a los tags
        wb = openpyxl.load_workbook(self.template_path, data_only=True)
        sheet = wb.active
        
        self.columns_order = []
        self.col_indices = {}
        
        # Asumimos que la fila 1 tiene los encabezados (estándar contable)
        for cell in sheet[1]:
            if cell.value:
                col_name = str(cell.value).strip()
                self.columns_order.append(col_name)
                self.col_indices[col_name] = cell.column
                
        # Construimos el mapeo automático usando inteligencia de alias
        self.mapping = {}
        for col_name in self.columns_order:
            xml_tag = self._infer_tag(col_name)
            if xml_tag:
                self.mapping[col_name] = xml_tag
        
        # Namespaces comunes usados en la DIAN (UBL 2.1)
        self.namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }

    def _infer_tag(self, col_name: str) -> str:
        """Busca coincidencias lógicas entre el nombre de la columna y los campos XML"""
        col_lower = col_name.lower()
        for key, tag in self.ALIAS_DICT.items():
            if key in col_lower:
                return tag
        return None

    def parse_single_xml_totals(self, xml_path: str) -> dict:
        """
        Procesa un único XML y extrae la información dictada por el automapeo.
        """
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            extracted_data = {}
            
            for excel_col, xml_tag in self.mapping.items():
                xpath_expr = f"//*[local-name()='{xml_tag}']"
                elements = root.xpath(xpath_expr, namespaces=self.namespaces)
                
                if elements:
                    value = None
                    for el in elements:
                        if el.text and el.text.strip():
                            value = el.text.strip()
                            # Convertimos numéricos si es posible para un Excel limpio
                            try:
                                if '.' in value and value.replace('.', '', 1).isdigit():
                                    value = float(value)
                                elif value.isdigit():
                                    value = int(value)
                            except:
                                pass
                            break
                    extracted_data[excel_col] = value
                else:
                    extracted_data[excel_col] = None
                    
            return extracted_data
            
        except Exception as e:
            print(f"\n[Error] falló el procesamiento de {xml_path}: {str(e)}")
            return None

    def process_folder(self, folder_path: str, output_excel_path: str):
        """
        Extrae data de los XMLs y los inserta en el Excel preservando diseño y formato.
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
            data_row = self.parse_single_xml_totals(xml_file)
            
            if data_row is not None:
                # Opcional: Agregar nombre del archivo si hay columna para ello (evitamos si no está mapeada)
                if "_Archivo_Origen" in self.col_indices:
                     data_row["_Archivo_Origen"] = os.path.basename(xml_file)
                
                # Insertamos la data en las columnas exactas usando índices
                for col_name, value in data_row.items():
                    if col_name in self.col_indices:
                        col_idx = self.col_indices[col_name]
                        sheet.cell(row=start_row, column=col_idx, value=value)
                start_row += 1
                
        # 3. Guardado final preservado
        wb.save(output_excel_path)
        print(f"\n✅ Archivo guardado correctamente en: {output_excel_path}")
