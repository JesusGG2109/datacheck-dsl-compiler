"""Analisis semantico para DataCheck DSL.

El analizador semantico recibe el arbol sintactico reducido producido por el
parser: declaraciones de campos y reglas. Su trabajo es validar coherencia de
tipos, referencias a campos y compatibilidad basica con el CSV.
"""


class AnalizadorSemantico:
    """Valida reglas semanticas de DataCheck."""

    def __init__(self, declaraciones, reglas, csv_headers=None):
        self.declaraciones = declaraciones
        self.reglas = reglas
        self.csv_headers = csv_headers or []
        self.errores = []
        self.traza = []

    def analizar(self):
        self.traza.append("[SEMANTICO] inicio del analisis semantico")
        tabla_declaraciones = self._validar_declaraciones()
        self._validar_reglas(tabla_declaraciones)
        self._validar_csv(tabla_declaraciones)
        self.traza.append("[SEMANTICO] fin del analisis semantico")
        return {
            "errores": self.errores,
            "traza": self.traza,
        }

    def _validar_declaraciones(self):
        tabla = {}
        for declaracion in self.declaraciones:
            if declaracion.nombre in tabla:
                self._error(
                    301,
                    declaracion.linea,
                    declaracion.columna,
                    "campo duplicado '{0}'".format(declaracion.nombre),
                )
                continue
            tabla[declaracion.nombre] = declaracion
            self.traza.append(
                "[SEMANTICO] registra campo {0}:{1}".format(
                    declaracion.nombre, declaracion.tipo
                )
            )
        return tabla

    def _validar_reglas(self, tabla_declaraciones):
        for regla in self.reglas:
            declaracion = tabla_declaraciones.get(regla.campo)
            if declaracion is None:
                self._error(
                    302,
                    regla.linea,
                    regla.columna,
                    "campo no declarado '{0}'".format(regla.campo),
                )
                continue

            if declaracion.tipo != regla.tipo_valor:
                self._error(
                    303,
                    regla.linea,
                    regla.columna,
                    "tipo incompatible para '{0}': {1} contra {2}".format(
                        regla.campo, declaracion.tipo, regla.tipo_valor
                    ),
                )
                continue

            if declaracion.tipo == "TEXTO" and regla.operador not in {"=", "!="}:
                self._error(
                    303,
                    regla.linea,
                    regla.columna,
                    "operador '{0}' no es valido para TEXTO".format(regla.operador),
                )
                continue

            self.traza.append(
                "[SEMANTICO] regla valida {0} {1} {2}".format(
                    regla.campo, regla.operador, regla.valor
                )
            )

    def _validar_csv(self, tabla_declaraciones):
        if not self.csv_headers:
            return

        headers = set(self.csv_headers)
        for nombre, declaracion in tabla_declaraciones.items():
            if nombre not in headers:
                self._error(
                    304,
                    declaracion.linea,
                    declaracion.columna,
                    "columna CSV ausente '{0}'".format(nombre),
                )

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
            "[SEMANTICO:ERROR] codigo {0}, linea {1}, columna {2}: {3}".format(
                codigo, linea, columna, descripcion
            )
        )

