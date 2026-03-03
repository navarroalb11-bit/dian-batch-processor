import os
import glob
import json
import pandas as pd
from lxml import etree
import sys

class BatchProcessor:
    def __init__(self, mapping_file: str):
        """
        Inicializa el procesador cargando las reglas de mapeo del usuario.
        """
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"No se encontró el archivo de mapeo: {mapping_file}")
            
        with open(mapping_file, 'r', encoding='utf-8') as f:
            self.mapping_schema = json.load(f)
            
        self.columns_order = self.mapping_schema.get("columns_order", [])
        self.mapping = self.mapping_schema.get("mapping", {})
        
        # Namespaces comunes usados en la DIAN (UBL 2.1)
        self.namespaces = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        }

    def parse_single_xml_totals(self, xml_path: str) -> dict:
        """
        Procesa un único XML y extrae la información a nivel de cabecera (Totales).
        """
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            extracted_data = {}
            
            # Recorremos el mapeo configurado por el usuario
            for excel_col, xml_tag in self.mapping.items():
                # Búsqueda XPath agnóstica de namespace exacto, pero
                # apuntando específicamente al nombre del tag. Esto da mucha flexibilidad
                # si el XML viene con prefijos irregulares.
                xpath_expr = f"//*[local-name()='{xml_tag}']"
                elements = root.xpath(xpath_expr, namespaces=self.namespaces)
                
                if elements:
                    # MVP: Tomamos la primera ocurrencia no vacía. 
                    # (Más adelante refinaremos para manejar tags duplicados como 'CompanyID' que pueden ser emisor o receptor)
                    value = None
                    for el in elements:
                        if el.text and el.text.strip():
                            value = el.text.strip()
                            break
                    extracted_data[excel_col] = value
                else:
                    extracted_data[excel_col] = None
                    
            return extracted_data
            
        except Exception as e:
            # En producción, usar logging en lugar de print
            print(f"\n[Error] falló el procesamiento de {xml_path}: {str(e)}")
            return None

    def process_folder(self, folder_path: str, output_excel_path: str):
        """
        Toma una carpeta con N archivos XML, extrae la data y la exporta a Excel.
        Incluye una barra de progreso nativa en consola.
        """
        search_pattern = os.path.join(folder_path, '*.xml')
        xml_files = glob.glob(search_pattern)
        
        total_files = len(xml_files)
        if total_files == 0:
            print(f"⚠️ No se encontraron archivos XML en: {folder_path}")
            return
            
        print(f"🚀 Iniciando procesamiento batch de {total_files} facturas electrónicas (XML)...\n")
        
        results = []
        
        for i, xml_file in enumerate(xml_files):
            data_row = self.parse_single_xml_totals(xml_file)
            
            if data_row is not None:
                # Agregamos el nombre del archivo nativo para propósitos de auditoría
                data_row['_Archivo_Origen'] = os.path.basename(xml_file)
                results.append(data_row)
                
            self._print_progress_bar(i + 1, total_files, prefix='Progreso:', suffix='Completado', length=40)
            
        print("\n\n📊 Generando consolidado en Excel...")
        
        # Convertimos la lista de diccionarios a un DataFrame
        df = pd.DataFrame(results)
        
        # Garantizamos que las columnas respeten el orden original de la plantilla del usuario
        cols_present = [c for c in self.columns_order if c in df.columns]
        other_cols = [c for c in df.columns if c not in cols_present]
        final_columns = cols_present + other_cols
        
        df = df[final_columns]
        
        # Guardado final a un archivo .xlsx
        df.to_excel(output_excel_path, index=False, engine='openpyxl')
        print(f"✅ ¡Éxito! Archivo guardado correctamente en: {output_excel_path}")

    def _print_progress_bar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        Barra de progreso visual en consola para no depender de librerías externas (como tqdm) en el core MVP.
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix} ({iteration}/{total})')
        sys.stdout.flush()

if __name__ == "__main__":
    # Prueba rápida de escritorio si ejecutas el script directamente
    # Asume que existe un mapping y carpetas de test
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_mapping_file = os.path.join(current_dir, '..', 'templates', 'user_mapping.json')
    test_input_folder = os.path.join(current_dir, '..', 'data', 'input_xmls')
    test_output_excel = os.path.join(current_dir, '..', 'data', 'output', 'resultado_contable.xlsx')
    
    if os.path.exists(test_mapping_file) and os.path.exists(test_input_folder):
        processor = BatchProcessor(test_mapping_file)
        processor.process_folder(test_input_folder, test_output_excel)
    else:
        print("💡 Para probar, crea las carpetas correspondientes y el user_mapping.json.")
