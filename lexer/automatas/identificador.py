"""AFD para identificadores.

Lenguaje reconocido:
    ID -> LETRA (LETRA | DIGITO | _)*

El automata recibe un lexema completo, recorre sus caracteres y retorna
aceptacion solo si termina en q_id.
"""

from lexer.alfabeto import CategoriaCaracter
from lexer.automatas.base import ResultadoAFD


class AutomataIdentificador:
    """AFD determinista para la clase IDENTIFICADOR."""

    nombre = "IDENTIFICADOR"

    def __init__(self, alfabeto):
        self.alfabeto = alfabeto
        self.estado_inicial = "q0"
        self.estados_finales = {"q_id"}
        self.transiciones = {
            "q0": {CategoriaCaracter.LETRA: "q_id"},
            "q_id": {
                CategoriaCaracter.LETRA: "q_id",
                CategoriaCaracter.DIGITO: "q_id",
                CategoriaCaracter.GUION_BAJO: "q_id",
            },
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
            if traza is not None:
                traza.automata_acepta(self.nombre, lexema, estado)
            return ResultadoAFD(True, estado, token="IDENTIFICADOR", tipo="ID")

        if traza is not None:
            traza.automata_rechaza(self.nombre, lexema, estado, "estado no final")
        return ResultadoAFD(False, estado, motivo="estado no final")

