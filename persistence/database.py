"""
Módulo para gestionar la base de datos SQLite con soporte JSON
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class DatabaseManager:
    """Gestor de base de datos para personajes con características en JSON"""

    def __init__(self, db_path: str = "database/personajes.db"):
        """
        Inicializa el gestor de base de datos

        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self.connection = None
        self._connect()
        self._create_tables()

    def _ensure_db_directory(self):
        """Asegura que el directorio de la base de datos existe"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        """Establece conexión con la base de datos"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        # Habilitar soporte para operaciones JSON
        self.connection.execute("PRAGMA foreign_keys = ON")

    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        cursor = self.connection.cursor()

        # Tabla principal de personajes con columna JSON para características
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                caracteristicas TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla para registrar partidas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personaje_objetivo_id INTEGER NOT NULL,
                adivinado BOOLEAN NOT NULL,
                intentos INTEGER NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (personaje_objetivo_id) REFERENCES personajes(id)
            )
        """)

        # Tabla para registrar las preguntas y respuestas de cada partida
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partida_preguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_id INTEGER NOT NULL,
                caracteristica TEXT NOT NULL,
                valor_esperado TEXT NOT NULL,
                valor_usuario TEXT NOT NULL,
                orden INTEGER NOT NULL,
                FOREIGN KEY (partida_id) REFERENCES partidas(id)
            )
        """)

        self.connection.commit()

    def cerrar(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """Soporte para context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager"""
        self.cerrar()

    # ========== CRUD de Personajes ==========

    def agregar_personaje(self, nombre: str, caracteristicas: Dict[str, Any]) -> int:
        """
        Agrega un nuevo personaje a la base de datos

        Args:
            nombre: Nombre del personaje
            caracteristicas: Diccionario con las características del personaje

        Returns:
            ID del personaje insertado

        Raises:
            sqlite3.IntegrityError: Si el personaje ya existe
        """
        cursor = self.connection.cursor()
        caracteristicas_json = json.dumps(caracteristicas, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO personajes (nombre, caracteristicas)
            VALUES (?, ?)
        """, (nombre, caracteristicas_json))

        self.connection.commit()
        return cursor.lastrowid

    def obtener_personaje(self, personaje_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un personaje por su ID

        Args:
            personaje_id: ID del personaje

        Returns:
            Diccionario con los datos del personaje o None si no existe
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, nombre, caracteristicas, fecha_creacion, fecha_modificacion
            FROM personajes
            WHERE id = ?
        """, (personaje_id,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'nombre': row['nombre'],
                'caracteristicas': json.loads(row['caracteristicas']),
                'fecha_creacion': row['fecha_creacion'],
                'fecha_modificacion': row['fecha_modificacion']
            }
        return None

    def obtener_personaje_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un personaje por su nombre

        Args:
            nombre: Nombre del personaje

        Returns:
            Diccionario con los datos del personaje o None si no existe
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, nombre, caracteristicas, fecha_creacion, fecha_modificacion
            FROM personajes
            WHERE nombre = ?
        """, (nombre,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'nombre': row['nombre'],
                'caracteristicas': json.loads(row['caracteristicas']),
                'fecha_creacion': row['fecha_creacion'],
                'fecha_modificacion': row['fecha_modificacion']
            }
        return None

    def obtener_todos_personajes(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los personajes de la base de datos

        Returns:
            Lista de diccionarios con los datos de todos los personajes
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, nombre, caracteristicas, fecha_creacion, fecha_modificacion
            FROM personajes
            ORDER BY nombre
        """)

        personajes = []
        for row in cursor.fetchall():
            personajes.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'caracteristicas': json.loads(row['caracteristicas']),
                'fecha_creacion': row['fecha_creacion'],
                'fecha_modificacion': row['fecha_modificacion']
            })

        return personajes

    def actualizar_personaje(self, personaje_id: int, nombre: Optional[str] = None,
                            caracteristicas: Optional[Dict[str, Any]] = None) -> bool:
        """
        Actualiza un personaje existente

        Args:
            personaje_id: ID del personaje a actualizar
            nombre: Nuevo nombre (opcional)
            caracteristicas: Nuevas características (opcional)

        Returns:
            True si se actualizó, False si no existe el personaje
        """
        cursor = self.connection.cursor()

        # Verificar que el personaje existe
        if not self.obtener_personaje(personaje_id):
            return False

        updates = []
        params = []

        if nombre is not None:
            updates.append("nombre = ?")
            params.append(nombre)

        if caracteristicas is not None:
            updates.append("caracteristicas = ?")
            params.append(json.dumps(caracteristicas, ensure_ascii=False))

        if updates:
            updates.append("fecha_modificacion = CURRENT_TIMESTAMP")
            params.append(personaje_id)

            query = f"""
                UPDATE personajes
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)
            self.connection.commit()

        return True

    def eliminar_personaje(self, personaje_id: int) -> bool:
        """
        Elimina un personaje de la base de datos

        Args:
            personaje_id: ID del personaje a eliminar

        Returns:
            True si se eliminó, False si no existe
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM personajes WHERE id = ?", (personaje_id,))
        self.connection.commit()

        return cursor.rowcount > 0

    def buscar_por_caracteristica(self, clave: str, valor: Any) -> List[Dict[str, Any]]:
        """
        Busca personajes que tengan una característica específica con un valor dado

        Args:
            clave: Nombre de la característica a buscar
            valor: Valor de la característica

        Returns:
            Lista de personajes que cumplen el criterio
        """
        cursor = self.connection.cursor()

        # Usar json_extract de SQLite para buscar en el JSON
        cursor.execute("""
            SELECT id, nombre, caracteristicas, fecha_creacion, fecha_modificacion
            FROM personajes
            WHERE json_extract(caracteristicas, ?) = ?
            ORDER BY nombre
        """, (f'$.{clave}', valor))

        personajes = []
        for row in cursor.fetchall():
            personajes.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'caracteristicas': json.loads(row['caracteristicas']),
                'fecha_creacion': row['fecha_creacion'],
                'fecha_modificacion': row['fecha_modificacion']
            })

        return personajes

    def contar_personajes(self) -> int:
        """
        Cuenta el total de personajes en la base de datos

        Returns:
            Número total de personajes
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM personajes")
        return cursor.fetchone()['total']

    # ========== Importación y Exportación ==========

    def importar_desde_json(self, json_path: str) -> Dict[str, int]:
        """
        Importa personajes desde un archivo JSON

        Args:
            json_path: Ruta al archivo JSON

        Returns:
            Diccionario con estadísticas de la importación
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        importados = 0
        errores = 0
        actualizados = 0

        for personaje_data in data.get('personajes', []):
            nombre = personaje_data.get('nombre')
            caracteristicas = personaje_data.get('caracteristicas', {})

            if not nombre or not caracteristicas:
                errores += 1
                continue

            try:
                # Verificar si el personaje ya existe
                existente = self.obtener_personaje_por_nombre(nombre)

                if existente:
                    # Actualizar personaje existente
                    self.actualizar_personaje(existente['id'], caracteristicas=caracteristicas)
                    actualizados += 1
                else:
                    # Agregar nuevo personaje
                    self.agregar_personaje(nombre, caracteristicas)
                    importados += 1

            except Exception as e:
                print(f"Error al importar {nombre}: {e}")
                errores += 1

        return {
            'importados': importados,
            'actualizados': actualizados,
            'errores': errores,
            'total': importados + actualizados
        }

    def exportar_a_json(self, json_path: str) -> bool:
        """
        Exporta todos los personajes a un archivo JSON

        Args:
            json_path: Ruta donde guardar el archivo JSON

        Returns:
            True si se exportó correctamente
        """
        personajes = self.obtener_todos_personajes()

        # Convertir al formato del JSON original
        data = {
            'personajes': [
                {
                    'id': p['id'],
                    'nombre': p['nombre'],
                    'caracteristicas': p['caracteristicas']
                }
                for p in personajes
            ],
            'metadata': {
                'version': '1.0',
                'fecha_exportacion': datetime.now().isoformat(),
                'total_personajes': len(personajes)
            }
        }

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

    # ========== Gestión de Partidas ==========

    def registrar_partida(self, personaje_id: int, adivinado: bool, intentos: int) -> int:
        """
        Registra una partida jugada

        Args:
            personaje_id: ID del personaje objetivo
            adivinado: Si se adivinó correctamente
            intentos: Número de intentos realizados

        Returns:
            ID de la partida registrada
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO partidas (personaje_objetivo_id, adivinado, intentos)
            VALUES (?, ?, ?)
        """, (personaje_id, adivinado, intentos))

        self.connection.commit()
        return cursor.lastrowid

    def registrar_pregunta_partida(self, partida_id: int, caracteristica: str,
                                   valor_esperado: str, valor_usuario: str, orden: int):
        """
        Registra una pregunta de una partida

        Args:
            partida_id: ID de la partida
            caracteristica: Nombre de la característica preguntada
            valor_esperado: Valor correcto de la característica
            valor_usuario: Valor que respondió el usuario
            orden: Orden de la pregunta en la partida
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO partida_preguntas
            (partida_id, caracteristica, valor_esperado, valor_usuario, orden)
            VALUES (?, ?, ?, ?, ?)
        """, (partida_id, caracteristica, valor_esperado, valor_usuario, orden))

        self.connection.commit()

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del juego

        Returns:
            Diccionario con estadísticas
        """
        cursor = self.connection.cursor()

        # Total de partidas
        cursor.execute("SELECT COUNT(*) as total FROM partidas")
        total_partidas = cursor.fetchone()['total']

        # Partidas ganadas
        cursor.execute("SELECT COUNT(*) as ganadas FROM partidas WHERE adivinado = 1")
        partidas_ganadas = cursor.fetchone()['ganadas']

        # Promedio de intentos
        cursor.execute("SELECT AVG(intentos) as promedio FROM partidas")
        promedio_intentos = cursor.fetchone()['promedio'] or 0

        # Personaje más jugado
        cursor.execute("""
            SELECT p.nombre, COUNT(*) as veces
            FROM partidas pa
            JOIN personajes p ON pa.personaje_objetivo_id = p.id
            GROUP BY p.nombre
            ORDER BY veces DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        personaje_popular = row['nombre'] if row else "Ninguno"

        return {
            'total_partidas': total_partidas,
            'partidas_ganadas': partidas_ganadas,
            'tasa_exito': (partidas_ganadas / total_partidas * 100) if total_partidas > 0 else 0,
            'promedio_intentos': round(promedio_intentos, 2),
            'personaje_mas_jugado': personaje_popular,
            'total_personajes': self.contar_personajes()
        }
