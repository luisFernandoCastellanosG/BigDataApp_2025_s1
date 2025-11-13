import os
import zipfile
import requests
from typing import Dict, List
from werkzeug.utils import secure_filename

class Funciones:
    @staticmethod
    def crear_carpeta(ruta: str) -> bool:
        """Crea una carpeta si no existe"""
        try:
            if not os.path.exists(ruta):
                os.makedirs(ruta)
            return True
        except Exception as e:
            print(f"Error al crear carpeta: {e}")
            return False
    
    @staticmethod
    def descomprimir_zip_local(ruta_file_zip: str, ruta_descomprimir: str) -> List[Dict]:
        """Descomprime un archivo ZIP y retorna info de archivos"""
        archivos = []
        try:
            with zipfile.ZipFile(ruta_file_zip, 'r') as zip_ref:
                for file_info in zip_ref.namelist():
                    if not file_info.endswith('/'):
                        # Extraer carpeta padre
                        carpeta = os.path.dirname(file_info)
                        nombre_archivo = os.path.basename(file_info)
                        extension = os.path.splitext(nombre_archivo)[1].lower()
                        
                        # Solo procesar txt y pdf
                        if extension in ['.txt', '.pdf']:
                            zip_ref.extract(file_info, ruta_descomprimir)
                            archivos.append({
                                'carpeta': carpeta if carpeta else 'raiz',
                                'nombre': nombre_archivo,
                                'ruta': os.path.join(ruta_descomprimir, file_info),
                                'extension': extension
                            })
            return archivos
        except Exception as e:
            print(f"Error al descomprimir ZIP: {e}")
            return []
    
    @staticmethod
    def descargar_y_descomprimir_zip(url: str, carpeta_destino: str, tipoArchivo: str = '') -> List[Dict]:
        """Descarga y descomprime un ZIP desde URL"""
        try:
            Funciones.crear_carpeta(carpeta_destino)
            
            # Descargar archivo
            response = requests.get(url, stream=True)
            zip_path = os.path.join(carpeta_destino, 'temp.zip')
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Descomprimir
            archivos = Funciones.descomprimir_zip_local(zip_path, carpeta_destino)
            
            # Eliminar ZIP temporal
            os.remove(zip_path)
            
            return archivos
        except Exception as e:
            print(f"Error al descargar y descomprimir: {e}")
            return []
    
    @staticmethod
    def allowed_file(filename: str, extensions: List[str]) -> bool:
        """Verifica si un archivo tiene extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions