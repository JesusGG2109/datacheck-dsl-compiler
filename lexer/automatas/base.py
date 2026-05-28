"""Tipos comunes para los AFD del lexer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoAFD:
    """Resultado formal de ejecutar un AFD sobre un lexema."""

    aceptado: bool
    estado_final: str
    token: str = None
    tipo: str = None
    motivo: str = ""

