"""Procesamiento CSV real para DataCheck Studio.

Usa el modulo csv de la biblioteca estandar para respetar comillas, comas
escapadas y saltos de linea dentro de celdas. No usa particiones manuales por
coma como mecanismo principal.
"""

import csv
from io import StringIO


def parsear_csv(contenido):
    """Convierte texto CSV en headers y filas tipo diccionario."""
    if not contenido:
        return {"headers": [], "rows": []}

    lector = csv.DictReader(StringIO(contenido))
    headers = lector.fieldnames or []
    filas = []
    for fila in lector:
        filas.append({header: fila.get(header, "") or "" for header in headers})
    return {"headers": headers, "rows": filas}


def filtrar_csv(filas, reglas, declaraciones):
    """Aplica las reglas semanticas ya validadas sobre filas CSV."""
    declaraciones_por_nombre = {declaracion.nombre: declaracion for declaracion in declaraciones}
    resultado = []

    for fila in filas:
        if _fila_cumple(fila, reglas, declaraciones_por_nombre):
            resultado.append(fila)
    return resultado


def _fila_cumple(fila, reglas, declaraciones):
    for regla in reglas:
        declaracion = declaraciones.get(regla.campo)
        if declaracion is None:
            return False

        valor_fila = fila.get(regla.campo, "")
        if declaracion.tipo == "NUMERICO":
            try:
                izquierdo = float(valor_fila)
                derecho = float(regla.valor)
            except (TypeError, ValueError):
                return False
            if not _comparar(izquierdo, derecho, regla.operador):
                return False
            continue

        if not _comparar(str(valor_fila), str(regla.valor), regla.operador):
            return False

    return True


def _comparar(izquierdo, derecho, operador):
    if operador == ">":
        return izquierdo > derecho
    if operador == "<":
        return izquierdo < derecho
    if operador == ">=":
        return izquierdo >= derecho
    if operador == "<=":
        return izquierdo <= derecho
    if operador == "=":
        return izquierdo == derecho
    if operador == "!=":
        return izquierdo != derecho
    return False

