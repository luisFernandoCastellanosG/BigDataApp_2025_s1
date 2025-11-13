from elasticsearch import Elasticsearch
from typing import Dict, List, Optional, Any
import json

class ElasticSearch:
    def __init__(self, cloud_url: str, api_key: str):
        """
        Inicializa conexión a ElasticSearch Cloud
        
        Args:
            cloud_url: URL del cluster de Elastic Cloud
            api_key: API Key para autenticación
        """
        self.client = Elasticsearch(
            cloud_url,
            api_key=api_key,
            verify_certs=True
        )
        
    def test_connection(self) -> bool:
        """Prueba la conexión a ElasticSearch"""
        try:
            info = self.client.info()
            print(f"✅ Conectado a Elastic: {info['version']['number']}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con Elastic: {e}")
            return False
    
    def ejecutar_comando(self, comando_json: str) -> Dict:
        """
        Ejecuta un comando JSON en ElasticSearch
        
        Args:
            comando_json: Comando en formato JSON string
            
        Returns:
            Resultado de la ejecución o error
        """
        try:
            comando = json.loads(comando_json)
            
            # Extraer operación y parámetros
            operacion = comando.get('operacion')
            index = comando.get('index')
            
            if operacion == 'crear_index':
                # Crear índice
                mappings = comando.get('mappings', {})
                settings = comando.get('settings', {})
                
                response = self.client.indices.create(
                    index=index,
                    mappings=mappings,
                    settings=settings
                )
                return {'success': True, 'data': response}
                
            elif operacion == 'eliminar_index':
                # Eliminar índice
                response = self.client.indices.delete(index=index)
                return {'success': True, 'data': response}
                
            elif operacion == 'actualizar_mappings':
                # Actualizar mappings
                mappings = comando.get('mappings', {})
                response = self.client.indices.put_mapping(
                    index=index,
                    body=mappings
                )
                return {'success': True, 'data': response}
                
            elif operacion == 'info_index':
                # Obtener información del índice
                response = self.client.indices.get(index=index)
                return {'success': True, 'data': response}
                
            elif operacion == 'listar_indices':
                # Listar todos los índices
                response = self.client.cat.indices(format='json')
                return {'success': True, 'data': response}
                
            else:
                return {'success': False, 'error': f'Operación no soportada: {operacion}'}
                
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON inválido: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def crear_index(self, nombre_index: str, mappings: Dict = None, settings: Dict = None) -> bool:
        """
        Crea un nuevo índice
        
        Args:
            nombre_index: Nombre del índice
            mappings: Definición de campos (opcional)
            settings: Configuración del índice (opcional)
        """
        try:
            body = {}
            if mappings:
                body['mappings'] = mappings
            if settings:
                body['settings'] = settings
                
            self.client.indices.create(index=nombre_index, body=body)
            return True
        except Exception as e:
            print(f"Error al crear índice: {e}")
            return False
    
    def eliminar_index(self, nombre_index: str) -> bool:
        """Elimina un índice"""
        try:
            self.client.indices.delete(index=nombre_index)
            return True
        except Exception as e:
            print(f"Error al eliminar índice: {e}")
            return False
    
    def listar_indices(self) -> List[Dict]:
        """Lista todos los índices"""
        try:
            indices = self.client.cat.indices(format='json')
            return indices
        except Exception as e:
            print(f"Error al listar índices: {e}")
            return []
    
    def indexar_documento(self, index: str, documento: Dict, doc_id: str = None) -> bool:
        """
        Indexa un documento en ElasticSearch
        
        Args:
            index: Nombre del índice
            documento: Documento a indexar
            doc_id: ID del documento (opcional)
        """
        try:
            if doc_id:
                self.client.index(index=index, id=doc_id, document=documento)
            else:
                self.client.index(index=index, document=documento)
            return True
        except Exception as e:
            print(f"Error al indexar documento: {e}")
            return False
    
    def indexar_bulk(self, index: str, documentos: List[Dict]) -> Dict:
        """
        Indexa múltiples documentos de forma masiva
        
        Args:
            index: Nombre del índice
            documentos: Lista de documentos a indexar
            
        Returns:
            Diccionario con estadísticas de indexación
        """
        from elasticsearch.helpers import bulk
        
        try:
            # Preparar acciones para bulk
            acciones = []
            for doc in documentos:
                accion = {
                    '_index': index,
                    '_source': doc
                }
                acciones.append(accion)
            
            # Ejecutar bulk
            success, failed = bulk(self.client, acciones, raise_on_error=False)
            
            return {
                'success': True,
                'indexados': success,
                'fallidos': len(failed) if failed else 0,
                'errores': failed if failed else []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def buscar(self, index: str, query: Dict, size: int = 10) -> Dict:
        """
        Realiza una búsqueda en ElasticSearch
        
        Args:
            index: Nombre del índice
            query: Query de búsqueda
            size: Número de resultados
        """
        try:
            response = self.client.search(index=index, body=query, size=size)
            return {
                'success': True,
                'total': response['hits']['total']['value'],
                'resultados': response['hits']['hits']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def buscar_texto(self, index: str, texto: str, campos: List[str] = None, size: int = 10) -> Dict:
        """
        Búsqueda simple de texto en campos específicos
        
        Args:
            index: Nombre del índice
            texto: Texto a buscar
            campos: Lista de campos donde buscar (si es None, busca en todos)
            size: Número de resultados
        """
        try:
            if campos:
                query = {
                    "query": {
                        "multi_match": {
                            "query": texto,
                            "fields": campos,
                            "type": "best_fields"
                        }
                    }
                }
            else:
                query = {
                    "query": {
                        "query_string": {
                            "query": texto
                        }
                    }
                }
            
            return self.buscar(index, query, size)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def obtener_documento(self, index: str, doc_id: str) -> Optional[Dict]:
        """Obtiene un documento por su ID"""
        try:
            response = self.client.get(index=index, id=doc_id)
            return response['_source']
        except Exception as e:
            print(f"Error al obtener documento: {e}")
            return None
    
    def actualizar_documento(self, index: str, doc_id: str, datos: Dict) -> bool:
        """Actualiza un documento existente"""
        try:
            self.client.update(index=index, id=doc_id, doc=datos)
            return True
        except Exception as e:
            print(f"Error al actualizar documento: {e}")
            return False
    
    def eliminar_documento(self, index: str, doc_id: str) -> bool:
        """Elimina un documento"""
        try:
            self.client.delete(index=index, id=doc_id)
            return True
        except Exception as e:
            print(f"Error al eliminar documento: {e}")
            return False
    
    def close(self):
        """Cierra la conexión"""
        self.client.close()