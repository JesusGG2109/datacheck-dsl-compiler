"""Tabla de simbolos del analizador lexico.

La tabla almacena un registro por cada token aceptado por su AFD. No realiza
validaciones por si misma: el lexer la llena solo despues de una aceptacion
formal.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EntradaTablaSimbolos:
    """Registro formal de un token valido."""

    lexema: str
    token: str
    tipo: str
    valor: object
    linea: int
    columna: int


class TablaSimbolos:
    """Coleccion ordenada de tokens aceptados."""

    def __init__(self):
        self.entradas = []

    def agregar(self, lexema, token, tipo, valor, linea, columna):
        entrada = EntradaTablaSimbolos(
            lexema=lexema,
            token=token,
            tipo=tipo,
            valor=valor,
            linea=linea,
            columna=columna,
        )
        self.entradas.append(entrada)
        return entrada

    def imprimir(self):
        print("\nTABLA DE SIMBOLOS")
        print("-" * 96)
        print(
            "{0:<18} | {1:<22} | {2:<16} | {3:<16} | {4:<6} | {5:<7}".format(
                "LEXEMA", "TOKEN", "TIPO", "VALOR", "LINEA", "COLUMNA"
            )
        )
        print("-" * 96)
        for entrada in self.entradas:
            print(
                "{0:<18} | {1:<22} | {2:<16} | {3:<16} | {4:<6} | {5:<7}".format(
                    entrada.lexema,
                    entrada.token,
                    entrada.tipo,
                    str(entrada.valor),
                    entrada.linea,
                    entrada.columna,
                )
            )

