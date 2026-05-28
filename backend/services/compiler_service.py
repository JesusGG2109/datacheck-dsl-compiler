"""Servicio orquestador del compilador DataCheck.

Este es el unico punto del backend que coordina lexer, parser, analisis
semantico y CSV. El frontend no reproduce ninguna de estas fases.
"""

from dataclasses import asdict

from lexer.lexemas import AnalizadorLexico

from backend.services.csv_service import filtrar_csv, parsear_csv
from backend.services.parser_service import ParserDataCheck
from backend.services.semantic_service import AnalizadorSemantico


def analyze_source(source, csv_text=None):
    """Ejecuta el pipeline academico completo y retorna JSON serializable."""
    lexer = AnalizadorLexico(mostrar_traza=False)
    resultado_lexico = lexer.analizar_texto(source or "", imprimir_reporte=False)

    tokens = _serializar_tokens(resultado_lexico.tabla_simbolos.entradas)
    errores_lexicos = _serializar_errores(resultado_lexico.pila_errores)

    parser = ParserDataCheck(tokens)
    resultado_parser = parser.parsear()

    csv_data = parsear_csv(csv_text or "")
    semantico = AnalizadorSemantico(
        resultado_parser["declaraciones"],
        resultado_parser["reglas"],
        csv_headers=csv_data["headers"],
    )
    resultado_semantico = semantico.analizar()

    puede_filtrar = (
        len(errores_lexicos) == 0
        and len(resultado_parser["errores"]) == 0
        and len(resultado_semantico["errores"]) == 0
    )
    csv_resultado = []
    if puede_filtrar and csv_data["rows"]:
        csv_resultado = filtrar_csv(
            csv_data["rows"],
            resultado_parser["reglas"],
            resultado_parser["declaraciones"],
        )

    traza = []
    traza.extend(lexer.traza.eventos)
    traza.extend(resultado_parser["traza"])
    traza.extend(resultado_semantico["traza"])
    if csv_text:
        traza.append(
            "[CSV] filas leidas: {0}, columnas: {1}".format(
                len(csv_data["rows"]), len(csv_data["headers"])
            )
        )
        traza.append("[CSV] filas aceptadas: {0}".format(len(csv_resultado)))

    return {
        "tokens": tokens,
        "errores_lexicos": errores_lexicos,
        "errores_sintacticos": resultado_parser["errores"],
        "errores_semanticos": resultado_semantico["errores"],
        "tabla_simbolos": _construir_tabla_simbolos(
            tokens,
            resultado_parser["declaraciones"],
            resultado_parser["reglas"],
        ),
        "traza": traza,
        "csv_resultado": csv_resultado,
        "csv_headers": csv_data["headers"],
        "csv_total_filas": len(csv_data["rows"]),
        "declaraciones": [asdict(declaracion) for declaracion in resultado_parser["declaraciones"]],
        "reglas": [asdict(regla) for regla in resultado_parser["reglas"]],
    }


def _construir_tabla_simbolos(tokens, declaraciones, reglas):
    """Tabla de simbolos real: solo identificadores con atributos semanticos."""
    dec_por_nombre = {d.nombre: d for d in declaraciones}
    campos_en_regla = {r.campo for r in reglas}

    vistos = {}
    for tok in tokens:
        if tok["token"] != "IDENTIFICADOR":
            continue
        nombre = tok["lexema"]
        if nombre in vistos:
            continue

        declaracion = dec_por_nombre.get(nombre)
        en_decl = declaracion is not None
        en_regla = nombre in campos_en_regla

        tipo_semantico = declaracion.tipo if declaracion else "NO_DECLARADO"

        if en_decl and en_regla:
            categoria = "CAMPO+REGLA"
        elif en_decl:
            categoria = "CAMPO"
        elif en_regla:
            categoria = "REGLA"
        else:
            categoria = "NO_DECLARADO"

        vistos[nombre] = {
            "lexema": nombre,
            "token": tok["token"],
            "tipo": tok["tipo"],
            "tipo_semantico": tipo_semantico,
            "categoria": categoria,
            "en_regla": en_regla,
            "linea": tok["linea"],
            "columna": tok["columna"],
        }

    return list(vistos.values())


def _serializar_tokens(entradas):
    tokens = []
    for entrada in entradas:
        tokens.append(
            {
                "lexema": entrada.lexema,
                "token": entrada.token,
                "tipo": entrada.tipo,
                "valor": entrada.valor,
                "linea": entrada.linea,
                "columna": entrada.columna,
            }
        )
    return tokens


def _serializar_errores(pila_errores):
    errores = []
    for error in pila_errores:
        errores.append(
            {
                "codigo": error.codigo,
                "descripcion": error.descripcion,
                "linea": error.linea,
                "columna": error.columna,
            }
        )
    return errores

