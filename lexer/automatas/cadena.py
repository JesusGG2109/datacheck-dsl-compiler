"""AFD para literales de cadena.

Lenguaje reconocido:
    CADENA -> " CARACTER_CADENA* "

CARACTER_CADENA pertenece al alfabeto de DataCheck, excluyendo comillas y
saltos de linea. La cadena vacia "" es valida.
"""

from lexer.alfabeto import CategoriaCaracter
from lexer.automatas.base import ResultadoAFD


class AutomataCadena:
    """AFD determinista para cadenas delimitadas por comillas dobles."""

    nombre = "CADENA"

    def __init__(self, alfabeto):
        self.alfabeto = alfabeto
        self.estado_inicial = "q0"
        self.estado_final = "q_cierre"

    def evaluar(self, lexema, traza=None):
        estado = self.estado_inicial
        for caracter in lexema:
            categoria = self._categoria_cadena(caracter)
            destino = self._transicion(estado, caracter, categoria)
            if traza is not None:
                traza.transicion(self.nombre, estado, caracter, categoria, destino)
            if destino is None:
                if traza is not None:
                    traza.automata_rechaza(
                        self.nombre,
                        lexema,
                        estado,
                        "transicion inexistente en cadena",
                    )
                return ResultadoAFD(False, estado, motivo="transicion inexistente")
            estado = destino

        if estado == self.estado_final:
            if traza is not None:
                traza.automata_acepta(self.nombre, lexema, estado)
            return ResultadoAFD(True, estado, token="CADENA", tipo="TEXTO")

        if traza is not None:
            traza.automata_rechaza(self.nombre, lexema, estado, "cadena sin cierre")
        return ResultadoAFD(False, estado, motivo="estado no final")

    def _categoria_cadena(self, caracter):
        if self.alfabeto.es_comilla(caracter):
            return CategoriaCaracter.COMILLA
        if self.alfabeto.es_salto_linea(caracter):
            return CategoriaCaracter.SALTO_LINEA
        if self.alfabeto.es_caracter_cadena(caracter):
            return "CARACTER_CADENA"
        return CategoriaCaracter.DESCONOCIDO

    def _transicion(self, estado, caracter, categoria):
        if estado == "q0" and categoria == CategoriaCaracter.COMILLA:
            return "q_cuerpo"
        if estado == "q_cuerpo" and categoria == "CARACTER_CADENA":
            return "q_cuerpo"
        if estado == "q_cuerpo" and categoria == CategoriaCaracter.COMILLA:
            return "q_cierre"
        return None

