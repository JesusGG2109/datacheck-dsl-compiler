"""Esquemas Pydantic para la API de DataCheck Studio."""

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Entrada principal para analizar DSL y opcionalmente filtrar CSV."""

    source: str = Field(default="", description="Codigo fuente DataCheck DSL")
    csv: str | None = Field(default=None, description="Contenido CSV opcional")


class TokenResponse(BaseModel):
    lexema: str
    token: str
    tipo: str
    valor: Any
    linea: int
    columna: int


class ErrorResponse(BaseModel):
    codigo: int
    descripcion: str
    linea: int
    columna: int


class SimboloEntry(BaseModel):
    lexema: str
    token: str
    tipo: str
    tipo_semantico: str
    categoria: str
    en_regla: bool
    linea: int
    columna: int


class DeclarationResponse(BaseModel):
    nombre: str
    tipo: str
    linea: int
    columna: int


class RuleResponse(BaseModel):
    campo: str
    operador: str
    valor: Any
    tipo_valor: str
    linea: int
    columna: int


class AnalyzeResponse(BaseModel):
    tokens: list[TokenResponse]
    errores_lexicos: list[ErrorResponse]
    errores_sintacticos: list[ErrorResponse]
    errores_semanticos: list[ErrorResponse]
    tabla_simbolos: list[SimboloEntry] = []
    traza: list[str]
    csv_resultado: list[dict[str, str]]
    csv_headers: list[str] = []
    csv_total_filas: int = 0
    declaraciones: list[DeclarationResponse] = []
    reglas: list[RuleResponse] = []

