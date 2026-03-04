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
        Soporta archivos .xml y .txt (siempre y cuando contengan estructura de factura válida).
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

    def parse_single_file(self, file_path: str) -> dict:
        """
        Procesa el archivo (XML o TXT) y extrae la información en un diccionario plano de 6 llaves.
        Si el archivo es un TXT sin etiquetas XML válidas de factura, retorna un código de error controlado.
        """
        try:
            # En lxml.etree.parse, no importa la extensión del archivo, 
            # solo le importa que el contenido tenga sintaxis XML válida.
            # Por tanto, si es un TXT con XML adentro, funcionará. 
            # Si es un TXT con "Hola Mundo", tirará una excepción XMLSyntaxError.
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Validación secundaria: ¿Al menos tiene etiquetas Invoice o CreditNote típicas de la DIAN?
            # En UBL, el root tag suele verse como {urn:oasis:...}Invoice. 
            # Una validación rápida es buscar si conseguimos al menos un 'cbc:ID' o simplemente intentamos mapear.
            
            row_data = {col: None for col in self.target_columns}
            found_data = False # Para verificar si extrajimos algo útil
            
            for excel_col, xml_tag in self.mapping.items():
                xpath_expr = f"//*[local-name()='{xml_tag}']"
                elements = root.xpath(xpath_expr, namespaces=self.namespaces)
                
                value = None
                if elements:
                    for el in elements:
                        if el.text and el.text.strip():
                            value = el.text.strip()
                            found_data = True # Sí había datos XML válidos
                            break
                            
                # Limpiezas y tipados
                if "Monto" in excel_col or "Total" in excel_col:
                    value = self._extract_numeric(value)
                elif "NIT" in excel_col:
                    value = self._clean_nit(value)
                elif "Fecha" in excel_col:
                    value = self._format_date(value)
                    
                row_data[excel_col] = value
            
            if not found_data:
                # El archivo tenía sintaxis XML pero no era una factura (ej. un archivo SVG)
                return {"_error_": "NOT_AN_INVOICE"}
                
            return row_data
            
        except etree.XMLSyntaxError:
            # Esto captura los archivos TXT que son puro texto (ej. "Lista de compras del super")
            return {"_error_": "NOT_XML"}
        except Exception as e:
            # Otros errores inesperados
            print(f"[Error] Falló la extracción en {os.path.basename(file_path)}: {str(e)}")
            return {"_error_": "UNKNOWN"}

    def process_folder(self, folder_path: str, output_excel_path: str) -> dict:
        """
        Lee los archivos, genera una base de datos tabular y la exporta a Excel puro.
        Retorna un diccionario con estadísticas de éxito/error para mostrarlas en la interfaz.
        """
        # Buscar tanto XMLs como TXTs
        search_pattern_xml = os.path.join(folder_path, '*.xml')
        search_pattern_txt = os.path.join(folder_path, '*.txt')
        
        all_files = glob.glob(search_pattern_xml) + glob.glob(search_pattern_txt)
        
        if not all_files:
            raise FileNotFoundError(f"⚠️ No se encontraron archivos (.xml o .txt) en: {folder_path}")
            
        results = []
        stats = {
            "processed": 0,
            "failed_not_xml": 0,
            "failed_not_invoice": 0,
            "failed_unknown": 0
        }
        
        for file_path in all_files:
            data = self.parse_single_file(file_path)
            
            if data and "_error_" in data:
                if data["_error_"] == "NOT_XML":
                    stats["failed_not_xml"] += 1
                elif data["_error_"] == "NOT_AN_INVOICE":
                    stats["failed_not_invoice"] += 1
                else:
                    stats["failed_unknown"] += 1
                continue
                
            if data:
                results.append(data)
                stats["processed"] += 1
                
        if results:
            # Creación del DataFrame y exportación de alta velocidad
            df = pd.DataFrame(results, columns=self.target_columns)
            df.to_excel(output_excel_path, index=False)
            print(f"✅ Base de datos generada exitosamente: {len(results)} registros.")
        else:
            raise ValueError("No se pudo extraer información válida de los archivos proporcionados. Asegúrate de que contengan estructura de Factura Electrónica.")
            
        return stats
