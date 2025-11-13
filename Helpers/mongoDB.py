from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import hashlib
from typing import Dict, List, Optional

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        """Inicializa conexión a MongoDB"""
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        
    def test_connection(self) -> bool:
        """Prueba la conexión a MongoDB"""
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False
    
    def validar_usuario(self, usuario: str, password: str, coleccion: str) -> Optional[Dict]:
        """Valida usuario y contraseña con MD5"""
        try:
            password_md5 = hashlib.md5(password.encode()).hexdigest()
            user = self.db[coleccion].find_one({
                'usuario': usuario,
                'password': password_md5
            })
            return user
        except Exception as e:
            print(f"Error al validar usuario: {e}")
            return None
    
    def obtener_usuario(self, usuario: str, coleccion: str) -> Optional[Dict]:
        """Obtiene información de un usuario"""
        try:
            return self.db[coleccion].find_one({'usuario': usuario})
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def listar_usuarios(self, coleccion: str) -> List[Dict]:
        """Lista todos los usuarios"""
        try:
            return list(self.db[coleccion].find({}, {'password': 0}))
        except Exception as e:
            print(f"Error al listar usuarios: {e}")
            return []
    
    def crear_usuario(self, usuario: str, password: str, permisos: Dict, coleccion: str) -> bool:
        """Crea un nuevo usuario"""
        try:
            password_md5 = hashlib.md5(password.encode()).hexdigest()
            documento = {
                'usuario': usuario,
                'password': password_md5,
                'permisos': permisos
            }
            self.db[coleccion].insert_one(documento)
            return True
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return False
    
    def actualizar_usuario(self, usuario: str, nuevos_datos: Dict, coleccion: str) -> bool:
        """Actualiza un usuario existente"""
        try:
            if 'password' in nuevos_datos:
                nuevos_datos['password'] = hashlib.md5(nuevos_datos['password'].encode()).hexdigest()
            
            self.db[coleccion].update_one(
                {'usuario': usuario},
                {'$set': nuevos_datos}
            )
            return True
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False
    
    def eliminar_usuario(self, usuario: str, coleccion: str) -> bool:
        """Elimina un usuario"""
        try:
            resultado = self.db[coleccion].delete_one({'usuario': usuario})
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    def close(self):
        """Cierra la conexión"""
        self.client.close()