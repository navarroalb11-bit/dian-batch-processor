import os
import glob
from lxml import etree
import pandas as pd
from datetime import datetime

class BatchProcessor:
    def __init__(self):
        """
        Inicializa el procesador masivo de base de datos.
        Ya no requiere plantillas Excel, funciona de forma autónoma con Pandas.
        """
        # Las 6 columnas exactas requeridas por el cliente
        self.target_columns = [
            "Fecha de Emisión",
            "Número de la Factura",
            "Monto del Subtotal",
            "Monto del IVA",
            "Total",
            "NIT del Proveedor"
        ]
        
        # Mapeo interno hacia etiquetas UBL 2.1 estándar de la DIAN
        self.mapping = {
            "Fecha de Emisión": "IssueDate",
            "Número de la Factura": "ID",
            "Monto del Subtotal": "LineExtensionAmount",
            "Monto del IVA": "TaxAmount",
            "Total": "PayableAmount",
            "NIT del Proveedor": "CompanyID",
        }
        
        self.namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }

    def _extract_numeric(self, str_value: str) -> float:
        if not str_value: return 0.0
        try:
            if '.' in str_value and str_value.replace('.', '', 1).isdigit():
                return float(str_value)
            elif str_value.isdigit():
                return float(str_value)
            return 0.0
        except:
            return 0.0

    def _clean_nit(self, nit_str: str) -> str:
        if not nit_str: return ""
        clean = nit_str.replace(".", "").replace(",", "").replace("-", "")
        clean = ''.join(c for c in clean if c.isdigit())
        return clean
        
    def _format_date(self, date_str: str) -> str:
        """Mantiene un formato estándar legible para base de datos"""
        if not date_str: return ""
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.strftime("%Y-%m-%d") # Estándar ISO para Pandas/Excel
        except:
            return date_str

    def parse_single_xml(self, xml_path: str) -> dict:
        """
        Procesa el XML y extrae la información en un diccionario plano de 6 llaves.
        """
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            row_data = {col: None for col in self.target_columns}
            
            for excel_col, xml_tag in self.mapping.items():
                xpath_expr = f"//*[local-name()='{xml_tag}']"
                elements = root.xpath(xpath_expr, namespaces=self.namespaces)
                
                value = None
                if elements:
                    for el in elements:
                        if el.text and el.text.strip():
                            value = el.text.strip()
                            break
                            
                # Limpiezas y tipados
                if "Monto" in excel_col or "Total" in excel_col:
                    value = self._extract_numeric(value)
                elif "NIT" in excel_col:
                    value = self._clean_nit(value)
                elif "Fecha" in excel_col:
                    value = self._format_date(value)
                    
                row_data[excel_col] = value
                
            return row_data
            
        except Exception as e:
            print(f"[Error] Falló la extracción en {os.path.basename(xml_path)}: {str(e)}")
            return None

    def process_folder(self, folder_path: str, output_excel_path: str):
        """
        Lee 1 o N archivos, genera una base de datos tabular y la exporta a Excel puro.
        """
        search_pattern = os.path.join(folder_path, '*.xml')
        xml_files = glob.glob(search_pattern)
        
        if not xml_files:
            raise FileNotFoundError(f"⚠️ No se encontraron archivos XML en: {folder_path}")
            
        results = []
        for xml_file in xml_files:
            data = self.parse_single_xml(xml_file)
            if data:
                results.append(data)
                
        if results:
            # Creación del DataFrame y exportación de alta velocidad
            df = pd.DataFrame(results, columns=self.target_columns)
            df.to_excel(output_excel_path, index=False)
            print(f"✅ Base de datos generada exitosamente: {len(results)} registros.")
        else:
            raise ValueError("No se pudo extraer información válida de los XML proporcionados.")
