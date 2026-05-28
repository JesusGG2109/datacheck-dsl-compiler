"""AFD para palabras reservadas.

Este modulo no valida mediante una consulta directa de pertenencia. Construye
un AFD determinista tipo trie, donde cada arista consume exactamente un
caracter. Una palabra reservada se acepta solo si el recorrido termina en un
estado final etiquetado.
"""

from lexer.automatas.base import ResultadoAFD


class AutomataPalabrasReservadas:
    """AFD determinista para las palabras reservadas de DataCheck DSL."""

    nombre = "RESERVADA"

    ESPECIFICACION = {
        "CAMPO": ("TOKEN_CAMPO", "DECLARACION_CAMPO"),
        "NUMERICO": ("TOKEN_NUMERICO", "TIPO_DATO"),
        "TEXTO": ("TOKEN_TEXTO", "TIPO_DATO"),
        "REGLA": ("TOKEN_REGLA", "DECLARACION_REGLA"),
        "Y": ("TOKEN_Y", "OPERADOR_LOGICO"),
        "O": ("TOKEN_O", "OPERADOR_LOGICO"),
    }

    def __init__(self):
        self.estado_inicial = "q0"
        self.transiciones = {}
        self.estados_finales = {}
        self._construir_automata()

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
                        "no existe arista literal para '" + caracter + "'",
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

    def _construir_automata(self):
        for palabra, etiqueta in self.ESPECIFICACION.items():
            estado = self.estado_inicial
            prefijo = ""
            for caracter in palabra:
                prefijo += caracter
                destino = "q_res_" + prefijo
                self.transiciones.setdefault(estado, {})
                if caracter not in self.transiciones[estado]:
                    self.transiciones[estado][caracter] = destino
                estado = self.transiciones[estado][caracter]
            self.estados_finales[estado] = etiqueta

