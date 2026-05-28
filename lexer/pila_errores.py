"""Pila de errores lexicos de DataCheck DSL.

Cada error conserva codigo, descripcion, linea y columna. Se modela como pila
porque el compilador puede apilar hallazgos durante el recorrido del archivo y
reportarlos al final de la fase.
"""

from dataclasses import dataclass


CATALOGO_ERRORES = {
    100: "Caracter invalido: no pertenece al alfabeto del lenguaje",
    101: "Identificador invalido segun el AFD de identificadores",
    102: "Cadena mal formada segun el AFD de cadenas",
    103: "Numero invalido segun el AFD numerico",
    104: "Operador invalido segun el AFD de operadores",
    105: "Lexema no reconocido por ningun AFD lexico",
}


@dataclass(frozen=True)
class ErrorLexico:
    """Error lexico con posicion exacta."""

    codigo: int
    descripcion: str
    linea: int
    columna: int


class PilaErrores:
    """Estructura LIFO para errores lexicos."""

    def __init__(self):
        self._errores = []

    def apilar(self, codigo, linea, columna, detalle=""):
        descripcion = CATALOGO_ERRORES.get(codigo, "Error lexico no catalogado")
        if detalle:
            descripcion = descripcion + ". Detalle: " + detalle
        error = ErrorLexico(
            codigo=codigo,
            descripcion=descripcion,
            linea=linea,
            columna=columna,
        )
        self._errores.append(error)
        return error

    def esta_vacia(self):
        return len(self._errores) == 0

    def cima(self):
        """Retorna el ultimo error apilado sin removerlo."""
        if self.esta_vacia():
            return None
        return self._errores[-1]

    def desapilar(self):
        """Remueve y retorna el ultimo error apilado."""
        if self.esta_vacia():
            return None
        return self._errores.pop()

    def __len__(self):
        return len(self._errores)

    def __iter__(self):
        return iter(self._errores)

    def imprimir(self):
        print("\nPILA DE ERRORES LEXICOS")
        print("-" * 96)
        if self.esta_vacia():
            print("No se detectaron errores lexicos.")
            return

        print("{0:<8} | {1:<6} | {2:<7} | {3}".format("CODIGO", "LINEA", "COLUMNA", "DESCRIPCION"))
        print("-" * 96)
        for error in self._errores:
            print(
                "{0:<8} | {1:<6} | {2:<7} | {3}".format(
                    error.codigo,
                    error.linea,
                    error.columna,
                    error.descripcion,
                )
            )
