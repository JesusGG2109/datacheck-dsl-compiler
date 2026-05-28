"""Parser academico inicial para DataCheck DSL.

Este modulo consume exclusivamente tokens producidos por el lexer Python. No
lee texto fuente ni repite reglas lexicas. La gramatica soportada por esta fase
es deliberadamente pequena y formal:

    PROGRAMA     -> SENTENCIA*
    SENTENCIA    -> DECLARACION | REGLA
    DECLARACION  -> CAMPO IDENTIFICADOR TIPO
    TIPO         -> NUMERICO | TEXTO
    REGLA        -> REGLA IDENTIFICADOR OPERADOR VALOR
    VALOR        -> NUMERO | CADENA
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeclaracionCampo:
    nombre: str
    tipo: str
    linea: int
    columna: int


@dataclass(frozen=True)
class ReglaFiltro:
    campo: str
    operador: str
    valor: object
    tipo_valor: str
    linea: int
    columna: int


class ParserDataCheck:
    """Parser descendente simple sobre la secuencia de tokens validos."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.declaraciones = []
        self.reglas = []
        self.errores = []
        self.traza = []

    def parsear(self):
        """Parsea el programa completo y retorna estructuras sintacticas."""
        self.traza.append("[PARSER] inicio del analisis sintactico")
        while self.posicion < len(self.tokens):
            token = self._actual()
            if token["token"] == "TOKEN_CAMPO":
                self._parsear_declaracion()
                continue
            if token["token"] == "TOKEN_REGLA":
                self._parsear_regla()
                continue

            self._error(
                201,
                token["linea"],
                token["columna"],
                "sentencia debe iniciar con CAMPO o REGLA",
            )
            self._sincronizar(token["linea"])

        self.traza.append("[PARSER] fin del analisis sintactico")
        return {
            "declaraciones": self.declaraciones,
            "reglas": self.reglas,
            "errores": self.errores,
            "traza": self.traza,
        }

    def _parsear_declaracion(self):
        inicio = self._actual()
        identificador = self._mirar(1)
        tipo = self._mirar(2)

        if not self._misma_linea(inicio, identificador, tipo):
            self._error(201, inicio["linea"], inicio["columna"], "declaracion CAMPO incompleta")
            self._sincronizar(inicio["linea"])
            return

        if identificador["token"] != "IDENTIFICADOR":
            self._error(201, identificador["linea"], identificador["columna"], "se esperaba IDENTIFICADOR")
            self._sincronizar(inicio["linea"])
            return

        if tipo["token"] not in {"TOKEN_NUMERICO", "TOKEN_TEXTO"}:
            self._error(201, tipo["linea"], tipo["columna"], "se esperaba tipo NUMERICO o TEXTO")
            self._sincronizar(inicio["linea"])
            return

        declaracion = DeclaracionCampo(
            nombre=identificador["lexema"],
            tipo=tipo["lexema"],
            linea=inicio["linea"],
            columna=inicio["columna"],
        )
        self.declaraciones.append(declaracion)
        self.traza.append(
            "[PARSER] acepta DECLARACION -> CAMPO {0} {1}".format(
                declaracion.nombre, declaracion.tipo
            )
        )
        self.posicion += 3

    def _parsear_regla(self):
        inicio = self._actual()
        campo = self._mirar(1)
        operador = self._mirar(2)
        valor = self._mirar(3)

        if not self._misma_linea(inicio, campo, operador, valor):
            self._error(202, inicio["linea"], inicio["columna"], "regla REGLA incompleta")
            self._sincronizar(inicio["linea"])
            return

        if campo["token"] != "IDENTIFICADOR":
            self._error(202, campo["linea"], campo["columna"], "se esperaba IDENTIFICADOR")
            self._sincronizar(inicio["linea"])
            return

        if operador["token"] != "OPERADOR_RELACIONAL":
            self._error(202, operador["linea"], operador["columna"], "se esperaba OPERADOR_RELACIONAL")
            self._sincronizar(inicio["linea"])
            return

        if valor["token"] not in {"NUMERO", "CADENA"}:
            self._error(202, valor["linea"], valor["columna"], "se esperaba NUMERO o CADENA")
            self._sincronizar(inicio["linea"])
            return

        regla = ReglaFiltro(
            campo=campo["lexema"],
            operador=operador["lexema"],
            valor=valor["valor"],
            tipo_valor="TEXTO" if valor["token"] == "CADENA" else "NUMERICO",
            linea=inicio["linea"],
            columna=inicio["columna"],
        )
        self.reglas.append(regla)
        self.traza.append(
            "[PARSER] acepta REGLA -> REGLA {0} {1} {2}".format(
                regla.campo, regla.operador, valor["lexema"]
            )
        )
        self.posicion += 4

    def _sincronizar(self, linea):
        """Descarta tokens restantes de la linea para evitar errores en cascada."""
        descartados = 0
        while self.posicion < len(self.tokens) and self.tokens[self.posicion]["linea"] == linea:
            self.posicion += 1
            descartados += 1
        if descartados > 0:
            self.traza.append(
                "[PARSER:SYNC] linea {0}: {1} token(s) descartados por recuperacion".format(
                    linea, descartados
                )
            )

    def _actual(self):
        return self.tokens[self.posicion]

    def _mirar(self, desplazamiento):
        indice = self.posicion + desplazamiento
        if indice >= len(self.tokens):
            actual = self._actual()
            return {
                "lexema": "EOF",
                "token": "EOF",
                "tipo": "EOF",
                "valor": None,
                "linea": actual["linea"],
                "columna": actual["columna"],
            }
        return self.tokens[indice]

    @staticmethod
    def _misma_linea(*tokens):
        if any(token["token"] == "EOF" for token in tokens):
            return False
        linea = tokens[0]["linea"]
        return all(token["linea"] == linea for token in tokens)

    def _error(self, codigo, linea, columna, descripcion):
        self.errores.append(
            {
                "codigo": codigo,
                "descripcion": descripcion,
                "linea": linea,
                "columna": columna,
            }
        )
        self.traza.append(
            "[PARSER:ERROR] codigo {0}, linea {1}, columna {2}: {3}".format(
                codigo, linea, columna, descripcion
            )
        )

