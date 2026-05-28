"""Compatibilidad historica para versiones anteriores del proyecto.

La implementacion formal de la fase lexica esta en el paquete lexer. Este
modulo se conserva para no romper imports antiguos, pero ya no contiene reglas
de reconocimiento.
"""

from lexer.pila_errores import CATALOGO_ERRORES, PilaErrores
from lexer.tabla_simbolos import TablaSimbolos


class CompiladorDataCheck:
    """Adaptador minimo sobre TablaSimbolos y PilaErrores."""

    def __init__(self):
        self.tabla = TablaSimbolos()
        self.errores = PilaErrores()

    def agregar_error(self, codigo, linea, posicion, detalle=""):
        self.errores.apilar(codigo, linea, posicion, detalle)

    def agregar_simbolo(self, lexema, categoria, linea):
        self.tabla.agregar(lexema, categoria, categoria, lexema, linea, 1)

    def generar_reporte(self):
        self.tabla.imprimir()
        self.errores.imprimir()

