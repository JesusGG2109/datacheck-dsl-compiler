"""AFD para constantes numericas.

Lenguaje reconocido:
    NUMERO -> DIGITO+ (. DIGITO+)?

El automata acepta enteros y decimales con al menos un digito antes y despues
del punto decimal. Casos como 12., .5, 12..3 o 123abc son rechazados.
"""

from lexer.alfabeto import CategoriaCaracter
from lexer.automatas.base import ResultadoAFD


class AutomataNumero:
    """AFD determinista para numeros enteros y decimales."""

    nombre = "NUMERO"

    def __init__(self, alfabeto):
        self.alfabeto = alfabeto
        self.estado_inicial = "q0"
        self.estados_finales = {
            "q_entero": "ENTERO",
            "q_decimal": "DECIMAL",
        }
        self.transiciones = {
            "q0": {CategoriaCaracter.DIGITO: "q_entero"},
            "q_entero": {
                CategoriaCaracter.DIGITO: "q_entero",
                CategoriaCaracter.PUNTO: "q_punto",
            },
            "q_punto": {CategoriaCaracter.DIGITO: "q_decimal"},
            "q_decimal": {CategoriaCaracter.DIGITO: "q_decimal"},
        }

    def evaluar(self, lexema, traza=None):
        estado = self.estado_inicial
        for caracter in lexema:
            categoria = self.alfabeto.categoria(caracter)
            destino = self.transiciones.get(estado, {}).get(categoria)
            if traza is not None:
                traza.transicion(self.nombre, estado, caracter, categoria, destino)
            if destino is None:
                if traza is not None:
                    traza.automata_rechaza(
                        self.nombre,
                        lexema,
                        estado,
                        "no existe transicion para la categoria " + categoria,
                    )
                return ResultadoAFD(False, estado, motivo="transicion inexistente")
            estado = destino

        if estado in self.estados_finales:
            tipo = self.estados_finales[estado]
            if traza is not None:
                traza.automata_acepta(self.nombre, lexema, estado)
            return ResultadoAFD(True, estado, token="NUMERO", tipo=tipo)

        if traza is not None:
            traza.automata_rechaza(self.nombre, lexema, estado, "estado no final")
        return ResultadoAFD(False, estado, motivo="estado no final")

