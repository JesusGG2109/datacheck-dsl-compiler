"""Traza academica del analisis lexico.

Cada metodo imprime un evento observable del proceso: lectura caracter por
caracter, lexemas generados, transiciones de AFD, tokens aceptados y errores.
"""


class TrazaLexica:
    """Canal de salida para la traza formal del lexer."""

    def __init__(self, habilitada=True):
        self.habilitada = habilitada
        self.eventos = []

    def _emitir(self, mensaje):
        self.eventos.append(mensaje)
        if self.habilitada:
            print(mensaje)

    def caracter_leido(self, caracter):
        self._emitir(
            "[LECTURA] linea {0}, columna {1}: '{2}'".format(
                caracter.linea,
                caracter.columna,
                self.representar_caracter(caracter.caracter),
            )
        )

    def lexema_generado(self, lexema, linea, columna):
        self._emitir(
            "[LEXEMA] linea {0}, columna {1}: {2}".format(
                linea, columna, self.representar_lexema(lexema)
            )
        )

    def transicion(self, automata, estado_origen, simbolo, categoria, estado_destino):
        destino = estado_destino if estado_destino is not None else "RECHAZO"
        self._emitir(
            "[AFD:{0}] {1} -- {2}/{3} --> {4}".format(
                automata,
                estado_origen,
                self.representar_caracter(simbolo),
                categoria,
                destino,
            )
        )

    def automata_acepta(self, automata, lexema, estado_final):
        self._emitir(
            "[AFD:{0}] acepta {1} en estado {2}".format(
                automata, self.representar_lexema(lexema), estado_final
            )
        )

    def automata_rechaza(self, automata, lexema, estado_final, motivo):
        self._emitir(
            "[AFD:{0}] rechaza {1} en estado {2}: {3}".format(
                automata, self.representar_lexema(lexema), estado_final, motivo
            )
        )

    def token_aceptado(self, lexema, token, tipo):
        self._emitir(
            "[TOKEN] {0} -> token={1}, tipo={2}".format(
                self.representar_lexema(lexema), token, tipo
            )
        )

    def error_detectado(self, codigo, descripcion, linea, columna):
        self._emitir(
            "[ERROR] codigo {0}, linea {1}, columna {2}: {3}".format(
                codigo, linea, columna, descripcion
            )
        )

    @staticmethod
    def representar_caracter(caracter):
        if caracter == "\n":
            return "\\n"
        if caracter == "\r":
            return "\\r"
        if caracter == "\t":
            return "\\t"
        if caracter == '"':
            return '\\"'
        if caracter is None:
            return "EOF"
        if ord(caracter) < 32 or ord(caracter) > 126:
            return "\\u{0:04X}".format(ord(caracter))
        return caracter

    @classmethod
    def representar_lexema(cls, lexema):
        return '"' + "".join(cls.representar_caracter(c) for c in lexema) + '"'
