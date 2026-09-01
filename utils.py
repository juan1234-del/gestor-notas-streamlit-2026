"""
Funciones de Cálculo y Validación - Gestor Académico de Notas
"""

from typing import List, Dict, Tuple


def validar_porcentaje_cortes(porcentajes: List[float]) -> Tuple[bool, str]:
    """
    Valida que la suma de porcentajes de cortes sea exactamente 100%
    
    Args:
        porcentajes: Lista con 3 porcentajes
        
    Returns:
        (es_válido, mensaje)
    """
    if len(porcentajes) != 3:
        return False, "Debe haber exactamente 3 cortes"
    
    suma = sum(porcentajes)
    if abs(suma - 100.0) > 0.01:  # Permitir margen mínimo por redondeo
        return False, f"La suma de porcentajes es {suma:.2f}%, debe ser 100%"
    
    return True, "Porcentajes válidos"


def validar_porcentaje_actividades(porcentajes: List[float]) -> Tuple[bool, str]:
    """
    Valida que la suma de porcentajes de actividades sea válida (≤ 100%)
    
    Args:
        porcentajes: Lista con porcentajes de actividades
        
    Returns:
        (es_válido, mensaje)
    """
    if not porcentajes:
        return True, "Sin actividades"
    
    suma = sum(porcentajes)
    if suma > 100.01:  # Pequeño margen por redondeo
        return False, f"La suma de porcentajes ({suma:.2f}%) no puede exceder 100%"
    
    return True, f"Porcentajes válidos (total: {suma:.2f}%)"


def validar_nota(nota: float) -> Tuple[bool, str]:
    """
    Valida que la nota esté entre 0.0 y 5.0
    
    Args:
        nota: Nota a validar
        
    Returns:
        (es_válido, mensaje)
    """
    if nota is None:
        return True, "Sin nota"
    
    try:
        nota_float = float(nota)
    except (ValueError, TypeError):
        return False, "La nota debe ser un número"
    
    if nota_float < 0.0 or nota_float > 5.0:
        return False, "La nota debe estar entre 0.0 y 5.0"
    
    return True, f"Nota válida: {nota_float:.1f}"


def validar_nombre(nombre: str, nombres_existentes: List[str] = None) -> Tuple[bool, str]:
    """
    Valida el nombre de una entidad
    
    Args:
        nombre: Nombre a validar
        nombres_existentes: Lista de nombres ya usados
        
    Returns:
        (es_válido, mensaje)
    """
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    
    if len(nombre.strip()) > 255:
        return False, "El nombre no puede exceder 255 caracteres"
    
    if nombres_existentes and nombre.strip() in nombres_existentes:
        return False, "Este nombre ya existe"
    
    return True, "Nombre válido"


# ============ CÁLCULOS DE NOTAS ============

def calcular_nota_corte(actividades: List[Dict]) -> float:
    """
    Calcula la nota del corte = Σ(nota_actividad × porcentaje_actividad / 100)
    Solo incluye actividades con nota registrada
    
    Args:
        actividades: Lista de actividades del corte
        
    Returns:
        Nota del corte (0.0-5.0)
    """
    actividades_calificadas = [a for a in actividades if a.get("nota") is not None]
    
    if not actividades_calificadas:
        return 0.0
    
    suma = sum(
        float(a["nota"]) * float(a["porcentaje"]) / 100.0
        for a in actividades_calificadas
    )
    
    return round(suma, 1)


def calcular_porcentaje_evaluado_corte(actividades: List[Dict]) -> float:
    """
    Calcula el porcentaje de actividades evaluadas en el corte
    
    Args:
        actividades: Lista de actividades del corte
        
    Returns:
        Porcentaje de evaluación (0-100)
    """
    if not actividades:
        return 0.0
    
    suma_total = sum(float(a["porcentaje"]) for a in actividades)
    if suma_total == 0:
        return 0.0
    
    suma_evaluada = sum(
        float(a["porcentaje"]) for a in actividades
        if a.get("nota") is not None
    )
    
    porcentaje = (suma_evaluada / suma_total) * 100.0
    return round(porcentaje, 1)


def calcular_aporte_corte(nota_corte: float, porcentaje_corte: float) -> float:
    """
    Calcula el aporte del corte a la nota final
    aporte = nota_corte × porcentaje_corte / 100
    
    Args:
        nota_corte: Nota del corte
        porcentaje_corte: Porcentaje del corte
        
    Returns:
        Aporte a la nota final
    """
    aporte = float(nota_corte) * float(porcentaje_corte) / 100.0
    return round(aporte, 2)


def calcular_nota_acumulada(cortes: List[Dict]) -> Tuple[float, float]:
    """
    Calcula la nota acumulada de la asignatura
    Retorna (nota_acumulada, porcentaje_evaluado)
    
    Args:
        cortes: Lista de cortes con sus datos
        
    Returns:
        (nota_acumulada, porcentaje_evaluado)
    """
    suma_aportes = 0.0
    porcentaje_total_evaluado = 0.0
    
    # Calcular aportes de cortes que tienen al menos una actividad calificada
    for corte in cortes:
        actividades = corte.get("actividades", [])
        
        if any(a.get("nota") is not None for a in actividades):
            nota_corte = calcular_nota_corte(actividades)
            aporte = calcular_aporte_corte(nota_corte, corte["porcentaje"])
            suma_aportes += aporte
            
            # Calcular porcentaje evaluado del corte
            porcentaje_corte_evaluado = calcular_porcentaje_evaluado_corte(actividades)
            porcentaje_total_evaluado += (
                float(corte["porcentaje"]) * porcentaje_corte_evaluado / 100.0
            )
    
    return round(suma_aportes, 2), round(porcentaje_total_evaluado, 1)


def calcular_promedio_general(asignaturas: List[Dict]) -> float:
    """
    Calcula el promedio general de todas las asignaturas
    Solo incluye asignaturas que tienen al menos una nota registrada
    
    Args:
        asignaturas: Lista de todas las asignaturas con sus datos
        
    Returns:
        Promedio general (0.0-5.0)
    """
    notas_acumuladas = []
    
    for asig in asignaturas:
        cortes = asig.get("cortes", [])
        nota_acumulada, _ = calcular_nota_acumulada(cortes)
        
        # Solo incluir si tiene al menos una nota
        if nota_acumulada > 0.0:
            notas_acumuladas.append(nota_acumulada)
    
    if not notas_acumuladas:
        return 0.0
    
    promedio = sum(notas_acumuladas) / len(notas_acumuladas)
    return round(promedio, 2)


def obtener_estado_nota_asignatura(asignatura: Dict) -> Dict:
    """
    Obtiene información completa del estado de notas de una asignatura
    
    Args:
        asignatura: Diccionario con datos de asignatura
        
    Returns:
        Diccionario con nota_acumulada, porcentaje_evaluado, nota_final, estado
    """
    cortes = asignatura.get("cortes", [])
    nota_acumulada, porcentaje_evaluado = calcular_nota_acumulada(cortes)
    
    # Mostrar nota final solo si está prácticamente completa (≥95%)
    mostrar_final = porcentaje_evaluado >= 95.0
    
    return {
        "nota_acumulada": nota_acumulada,
        "porcentaje_evaluado": porcentaje_evaluado,
        "nota_final": nota_acumulada if mostrar_final else None,
        "completada": mostrar_final
    }


# ============ VALIDACIONES COMPLEJAS ============

def validar_guardar_corte(cortes_actuales: List[Dict], porcentajes_nuevos: List[float]) -> Tuple[bool, str]:
    """
    Valida antes de guardar los porcentajes de cortes
    
    Args:
        cortes_actuales: Cortes actuales
        porcentajes_nuevos: Nuevos porcentajes (3 valores)
        
    Returns:
        (es_válido, mensaje)
    """
    if len(porcentajes_nuevos) != 3:
        return False, "Debe haber exactamente 3 cortes"
    
    # Validar cada porcentaje individualmente
    for i, p in enumerate(porcentajes_nuevos, 1):
        try:
            porcentaje = float(p)
            if porcentaje < 0 or porcentaje > 100:
                return False, f"Corte {i}: El porcentaje debe estar entre 0 y 100"
        except (ValueError, TypeError):
            return False, f"Corte {i}: El porcentaje debe ser un número"
    
    # Validar suma
    es_válido, msg = validar_porcentaje_cortes(porcentajes_nuevos)
    return es_válido, msg


def validar_guardar_actividad(
    actividades_existentes: List[Dict],
    nombre: str,
    porcentaje: float,
    nota: float = None
) -> Tuple[bool, str]:
    """
    Valida antes de guardar/actualizar una actividad
    
    Args:
        actividades_existentes: Actividades actuales del corte
        nombre: Nombre de la actividad
        porcentaje: Porcentaje de la actividad
        nota: Nota (opcional)
        
    Returns:
        (es_válido, mensaje)
    """
    # Validar nombre
    es_válido, msg = validar_nombre(nombre)
    if not es_válido:
        return False, msg
    
    # Validar porcentaje
    try:
        porcentaje_float = float(porcentaje)
        if porcentaje_float < 0 or porcentaje_float > 100:
            return False, "El porcentaje debe estar entre 0 y 100"
    except (ValueError, TypeError):
        return False, "El porcentaje debe ser un número"
    
    # Validar nota si existe
    if nota is not None:
        es_válido, msg = validar_nota(nota)
        if not es_válido:
            return False, msg
    
    # Validar suma de porcentajes (sin incluir la actividad que se está editando)
    suma_otros = sum(a["porcentaje"] for a in actividades_existentes)
    if (suma_otros + porcentaje_float) > 100.01:
        return False, f"La suma de porcentajes ({suma_otros + porcentaje_float:.2f}%) excedería 100%"
    
    return True, "Actividad válida"
