"""AFD para operadores relacionales de DataCheck DSL.

Operadores reconocidos:
    >, <, >=, <=, =, !=
"""

from lexer.automatas.base import ResultadoAFD


class AutomataOperador:
    """AFD determinista para operadores."""

    nombre = "OPERADOR"

    def __init__(self):
        self.estado_inicial = "q0"
        self.estados_finales = {
            "q_mayor": ("OPERADOR_RELACIONAL", "MAYOR_QUE"),
            "q_menor": ("OPERADOR_RELACIONAL", "MENOR_QUE"),
            "q_mayor_igual": ("OPERADOR_RELACIONAL", "MAYOR_IGUAL"),
            "q_menor_igual": ("OPERADOR_RELACIONAL", "MENOR_IGUAL"),
            "q_igual": ("OPERADOR_RELACIONAL", "IGUAL"),
            "q_diferente": ("OPERADOR_RELACIONAL", "DIFERENTE"),
        }
        self.transiciones = {
            "q0": {
                ">": "q_mayor",
                "<": "q_menor",
                "=": "q_igual",
                "!": "q_exclamacion",
            },
            "q_mayor": {"=": "q_mayor_igual"},
            "q_menor": {"=": "q_menor_igual"},
            "q_exclamacion": {"=": "q_diferente"},
        }

    def evaluar(self, lexema, traza=None):
        estado = self.estado_inicial
        for caracter in lexema:
            destino = self.transiciones.get(estado, {}).get(caracter)
            if traza is not None:
                traza.transicion(self.nombre, estado, caracter, "literal", destino)
            if destino is None:
                if traza is not None:
                    traza.automata_rechaza(
                        self.nombre,
                        lexema,
                        estado,
                        "no existe transicion para operador",
                    )
                return ResultadoAFD(False, estado, motivo="transicion inexistente")
            estado = destino

        if estado in self.estados_finales:
            token, tipo = self.estados_finales[estado]
            if traza is not None:
                traza.automata_acepta(self.nombre, lexema, estado)
            return ResultadoAFD(True, estado, token=token, tipo=tipo)

        if traza is not None:
            traza.automata_rechaza(self.nombre, lexema, estado, "estado no final")
        return ResultadoAFD(False, estado, motivo="estado no final")

