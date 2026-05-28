"""Punto de entrada de DataCheck DSL.

La fase actual implementada es el analisis lexico formal. main.py no contiene
reglas de reconocimiento: delega al paquete lexer, donde viven el alfabeto,
lector caracter por caracter, generador de lexemas, AFD, tabla de simbolos y
pila de errores.
"""

import argparse

from lexer.lexemas import AnalizadorLexico


def analizar(ruta="entrada.txt", mostrar_traza=True):
    """Ejecuta la fase 1 sobre el archivo indicado."""
    analizador = AnalizadorLexico(mostrar_traza=mostrar_traza)
    return analizador.analizar(ruta)


def construir_argumentos():
    parser = argparse.ArgumentParser(description="Analizador lexico de DataCheck DSL")
    parser.add_argument(
        "archivo",
        nargs="?",
        default="entrada.txt",
        help="archivo fuente DataCheck DSL",
    )
    parser.add_argument(
        "--sin-traza",
        action="store_true",
        help="muestra solo el reporte final",
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = construir_argumentos()
    analizar(argumentos.archivo, mostrar_traza=not argumentos.sin_traza)

