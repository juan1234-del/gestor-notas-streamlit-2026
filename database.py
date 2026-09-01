"""
Módulo de Base de Datos - Gestor Académico de Notas
Maneja todas las operaciones CRUD con SQLite
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

DB_PATH = "data/academico.db"


def get_connection():
    """Obtiene conexión a la base de datos"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Crea las tablas si no existen"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla Asignaturas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(255) UNIQUE NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla Cortes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura_id INTEGER NOT NULL,
            numero INTEGER NOT NULL CHECK(numero BETWEEN 1 AND 3),
            porcentaje DECIMAL(5, 2) NOT NULL,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id) ON DELETE CASCADE,
            UNIQUE(asignatura_id, numero)
        )
    """)
    
    # Tabla Actividades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corte_id INTEGER NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            porcentaje DECIMAL(5, 2) NOT NULL,
            nota DECIMAL(3, 1),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (corte_id) REFERENCES cortes(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


# ============ OPERACIONES CON ASIGNATURAS ============

def crear_asignatura(nombre: str) -> bool:
    """Crea una nueva asignatura"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO asignaturas (nombre) VALUES (?)", (nombre,))
        asignatura_id = cursor.lastrowid
        conn.commit()
        
        # Crear tres cortes vacíos (0% por defecto)
        for numero in range(1, 4):
            cursor.execute(
                "INSERT INTO cortes (asignatura_id, numero, porcentaje) VALUES (?, ?, ?)",
                (asignatura_id, numero, 0)
            )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error al crear asignatura: {e}")
        return False


def obtener_asignaturas() -> List[Dict]:
    """Obtiene todas las asignaturas"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM asignaturas ORDER BY fecha_creacion DESC")
    asignaturas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return asignaturas


def obtener_asignatura(asignatura_id: int) -> Optional[Dict]:
    """Obtiene una asignatura por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def eliminar_asignatura(asignatura_id: int) -> bool:
    """Elimina una asignatura (en cascada)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asignaturas WHERE id = ?", (asignatura_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al eliminar asignatura: {e}")
        return False


# ============ OPERACIONES CON CORTES ============

def obtener_cortes(asignatura_id: int) -> List[Dict]:
    """Obtiene los tres cortes de una asignatura"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, numero, porcentaje FROM cortes WHERE asignatura_id = ? ORDER BY numero",
        (asignatura_id,)
    )
    cortes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cortes


def actualizar_porcentaje_corte(corte_id: int, porcentaje: float) -> bool:
    """Actualiza el porcentaje de un corte"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE cortes SET porcentaje = ? WHERE id = ?", (porcentaje, corte_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar porcentaje: {e}")
        return False


def obtener_corte(corte_id: int) -> Optional[Dict]:
    """Obtiene un corte específico"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, asignatura_id, numero, porcentaje FROM cortes WHERE id = ?", (corte_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


# ============ OPERACIONES CON ACTIVIDADES ============

def crear_actividad(corte_id: int, nombre: str, porcentaje: float) -> bool:
    """Crea una nueva actividad"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO actividades (corte_id, nombre, porcentaje, nota) VALUES (?, ?, ?, NULL)",
            (corte_id, nombre, porcentaje)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al crear actividad: {e}")
        return False


def obtener_actividades(corte_id: int) -> List[Dict]:
    """Obtiene todas las actividades de un corte"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, porcentaje, nota FROM actividades WHERE corte_id = ? ORDER BY id",
        (corte_id,)
    )
    actividades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return actividades


def actualizar_nota_actividad(actividad_id: int, nota: Optional[float]) -> bool:
    """Actualiza la nota de una actividad"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE actividades SET nota = ? WHERE id = ?", (nota, actividad_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar nota: {e}")
        return False


def actualizar_actividad(actividad_id: int, nombre: str, porcentaje: float) -> bool:
    """Actualiza nombre y porcentaje de una actividad"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE actividades SET nombre = ?, porcentaje = ? WHERE id = ?",
            (nombre, porcentaje, actividad_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar actividad: {e}")
        return False


def eliminar_actividad(actividad_id: int) -> bool:
    """Elimina una actividad"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM actividades WHERE id = ?", (actividad_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al eliminar actividad: {e}")
        return False


def obtener_actividad(actividad_id: int) -> Optional[Dict]:
    """Obtiene una actividad específica"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, corte_id, nombre, porcentaje, nota FROM actividades WHERE id = ?",
        (actividad_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


# ============ OPERACIONES DE CONSULTA COMPLEJAS ============

def obtener_datos_completos(asignatura_id: int) -> Dict:
    """Obtiene asignatura, cortes y actividades en una estructura"""
    conn = get_connection()
    cursor = conn.cursor()
    
    datos = {
        "asignatura": None,
        "cortes": []
    }
    
    # Obtener asignatura
    cursor.execute("SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,))
    result = cursor.fetchone()
    if result:
        datos["asignatura"] = dict(result)
    
    # Obtener cortes y actividades
    cursor.execute(
        "SELECT id, numero, porcentaje FROM cortes WHERE asignatura_id = ? ORDER BY numero",
        (asignatura_id,)
    )
    
    for corte_row in cursor.fetchall():
        corte = dict(corte_row)
        cursor.execute(
            "SELECT id, nombre, porcentaje, nota FROM actividades WHERE corte_id = ? ORDER BY id",
            (corte["id"],)
        )
        corte["actividades"] = [dict(row) for row in cursor.fetchall()]
        datos["cortes"].append(corte)
    
    conn.close()
    return datos


def obtener_todas_asignaturas_con_datos() -> List[Dict]:
    """Obtiene todas las asignaturas con sus cortes y actividades"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre FROM asignaturas ORDER BY fecha_creacion DESC")
    asignaturas = []
    
    for asig_row in cursor.fetchall():
        asig = dict(asig_row)
        
        cursor.execute(
            "SELECT id, numero, porcentaje FROM cortes WHERE asignatura_id = ? ORDER BY numero",
            (asig["id"],)
        )
        asig["cortes"] = []
        
        for corte_row in cursor.fetchall():
            corte = dict(corte_row)
            cursor.execute(
                "SELECT id, nombre, porcentaje, nota FROM actividades WHERE corte_id = ? ORDER BY id",
                (corte["id"],)
            )
            corte["actividades"] = [dict(row) for row in cursor.fetchall()]
            asig["cortes"].append(corte)
        
        asignaturas.append(asig)
    
    conn.close()
    return asignaturas


# ============ LIMPIAR BASE DE DATOS (para pruebas) ============

def limpiar_base_datos():
    """Elimina y recrea la base de datos (SOLO PARA DESARROLLO)"""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_database()
        return True
    except Exception as e:
        print(f"Error al limpiar BD: {e}")
        return False


if __name__ == "__main__":
    # Inicializar BD
    init_database()
    print("Base de datos inicializada correctamente.")
