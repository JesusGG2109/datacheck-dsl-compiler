"""Endpoints HTTP de DataCheck Studio."""

from fastapi import APIRouter

from backend.models.schemas import AnalyzeRequest, AnalyzeResponse
from backend.services.compiler_service import analyze_source


router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """Ejecuta lexer, parser, semantica y CSV en Python."""
    return analyze_source(request.source, request.csv)


@router.post("/tokens")
def get_tokens(request: AnalyzeRequest):
    """Extrae tokens del pipeline de compilacion Python."""
    return {"tokens": analyze_source(request.source, request.csv)["tokens"]}


@router.post("/errors")
def get_errors(request: AnalyzeRequest):
    """Retorna errores clasificados por fase: lexico, sintactico, semantico."""
    result = analyze_source(request.source, request.csv)
    return {
        "errores_lexicos": result["errores_lexicos"],
        "errores_sintacticos": result["errores_sintacticos"],
        "errores_semanticos": result["errores_semanticos"],
    }


@router.post("/symbols")
def get_symbols(request: AnalyzeRequest):
    """Retorna la tabla de simbolos con identificadores y tipos semanticos."""
    return {"tabla_simbolos": analyze_source(request.source, request.csv)["tabla_simbolos"]}


@router.post("/filter")
def filter_csv(request: AnalyzeRequest):
    """Aplica las reglas del compilador sobre el CSV y retorna filas filtradas."""
    result = analyze_source(request.source, request.csv)
    return {
        "csv_resultado": result["csv_resultado"],
        "csv_headers": result["csv_headers"],
        "csv_total_filas": result["csv_total_filas"],
    }

