"""Generacion manual de lexemas y coordinacion de la fase lexica.

El analizador lee caracteres desde LectorArchivo, construye lexemas caracter
por caracter y delega su validacion a AFD especificos. No delega el
reconocimiento lexico a librerias externas de parsing.
"""

from dataclasses import dataclass

from lexer.alfabeto import AlfabetoDataCheck
from lexer.automatas.cadena import AutomataCadena
from lexer.automatas.identificador import AutomataIdentificador
from lexer.automatas.numero import AutomataNumero
from lexer.automatas.operador import AutomataOperador
from lexer.automatas.reservada import AutomataPalabrasReservadas
from lexer.lector import LectorArchivo, LectorTexto
from lexer.pila_errores import PilaErrores
from lexer.tabla_simbolos import TablaSimbolos
from lexer.traza import TrazaLexica


@dataclass(frozen=True)
class ResultadoAnalisisLexico:
    """Resultado completo de la fase lexica."""

    tabla_simbolos: TablaSimbolos
    pila_errores: PilaErrores


class AnalizadorLexico:
    """Lexer academico para DataCheck DSL."""

    def __init__(self, mostrar_traza=True):
        self.alfabeto = AlfabetoDataCheck()
        self.traza = TrazaLexica(habilitada=mostrar_traza)
        self.tabla_simbolos = TablaSimbolos()
        self.pila_errores = PilaErrores()
        self.afd_reservadas = AutomataPalabrasReservadas()
        self.afd_identificador = AutomataIdentificador(self.alfabeto)
        self.afd_numero = AutomataNumero(self.alfabeto)
        self.afd_cadena = AutomataCadena(self.alfabeto)
        self.afd_operador = AutomataOperador()

    def analizar(self, ruta, imprimir_reporte=True):
        """Ejecuta la fase lexica completa sobre un archivo fuente."""
        self._reiniciar()
        try:
            with LectorArchivo(ruta, traza=self.traza) as lector:
                self._analizar_con_lector(lector)
        except FileNotFoundError:
            self._registrar_error(100, 1, 1, "No existe el archivo: " + ruta)

        if imprimir_reporte:
            self.imprimir_reporte()
        return ResultadoAnalisisLexico(self.tabla_simbolos, self.pila_errores)

    def analizar_texto(self, texto, imprimir_reporte=False):
        """Ejecuta la fase lexica sobre codigo fuente recibido como cadena."""
        self._reiniciar()
        with LectorTexto(texto, traza=self.traza) as lector:
            self._analizar_con_lector(lector)

        if imprimir_reporte:
            self.imprimir_reporte()
        return ResultadoAnalisisLexico(self.tabla_simbolos, self.pila_errores)

    def imprimir_reporte(self):
        """Imprime tabla de simbolos y pila de errores."""
        print("\n" + "=" * 96)
        print("RESULTADO FORMAL DEL ANALISIS LEXICO")
        print("=" * 96)
        self.tabla_simbolos.imprimir()
        self.pila_errores.imprimir()

    def _reiniciar(self):
        self.tabla_simbolos = TablaSimbolos()
        self.pila_errores = PilaErrores()

    def _analizar_con_lector(self, lector):
        while True:
            siguiente = lector.mirar()
            if siguiente is None:
                break

            caracter = siguiente.caracter

            if not self.alfabeto.pertenece(caracter):
                leido = lector.leer()
                self._registrar_error(
                    100,
                    leido.linea,
                    leido.columna,
                    "simbolo '" + self.traza.representar_caracter(caracter) + "'",
                )
                continue

            if self.alfabeto.es_espacio(caracter) or self.alfabeto.es_salto_linea(caracter):
                lector.leer()
                continue

            if self.alfabeto.es_letra(caracter) or self.alfabeto.es_guion_bajo(caracter):
                self._procesar_identificador_o_reservada(lector)
                continue

            if self.alfabeto.es_digito(caracter) or self.alfabeto.es_punto(caracter):
                self._procesar_numero(lector)
                continue

            if self.alfabeto.es_comilla(caracter):
                self._procesar_cadena(lector)
                continue

            if self.alfabeto.es_operador(caracter):
                self._procesar_operador(lector)
                continue

            leido = lector.leer()
            self._registrar_error(105, leido.linea, leido.columna, "simbolo '" + caracter + "'")

    def _procesar_identificador_o_reservada(self, lector):
        lexema, linea, columna = self._leer_identificador_candidato(lector)
        self.traza.lexema_generado(lexema, linea, columna)

        resultado_reservada = self.afd_reservadas.evaluar(lexema, traza=self.traza)
        if resultado_reservada.aceptado:
            self._agregar_simbolo(
                lexema,
                resultado_reservada.token,
                resultado_reservada.tipo,
                lexema,
                linea,
                columna,
            )
            return

        resultado_identificador = self.afd_identificador.evaluar(lexema, traza=self.traza)
        if resultado_identificador.aceptado:
            self._agregar_simbolo(
                lexema,
                resultado_identificador.token,
                resultado_identificador.tipo,
                lexema,
                linea,
                columna,
            )
            return

        self._registrar_error(101, linea, columna, "lexema '" + lexema + "'")

    def _procesar_numero(self, lector):
        lexema, linea, columna = self._leer_numero_candidato(lector)
        self.traza.lexema_generado(lexema, linea, columna)

        resultado = self.afd_numero.evaluar(lexema, traza=self.traza)
        if resultado.aceptado:
            self._agregar_simbolo(
                lexema,
                resultado.token,
                resultado.tipo,
                self._valor_numerico(lexema, resultado.tipo),
                linea,
                columna,
            )
            return

        self._registrar_error(103, linea, columna, "lexema '" + lexema + "'")

    def _procesar_cadena(self, lector):
        lexema, linea, columna, caracter_invalido = self._leer_cadena(lector)
        self.traza.lexema_generado(lexema, linea, columna)

        resultado = self.afd_cadena.evaluar(lexema, traza=self.traza)
        if resultado.aceptado and caracter_invalido is None:
            self._agregar_simbolo(
                lexema,
                resultado.token,
                resultado.tipo,
                lexema[1:-1],
                linea,
                columna,
            )
            return

        if caracter_invalido is not None:
            self._registrar_error(
                100,
                caracter_invalido.linea,
                caracter_invalido.columna,
                "simbolo '"
                + self.traza.representar_caracter(caracter_invalido.caracter)
                + "' dentro de cadena",
            )
            return

        self._registrar_error(102, linea, columna, "lexema '" + lexema + "'")

    def _procesar_operador(self, lector):
        lexema, linea, columna = self._leer_operador(lector)
        self.traza.lexema_generado(lexema, linea, columna)

        resultado = self.afd_operador.evaluar(lexema, traza=self.traza)
        if resultado.aceptado:
            self._agregar_simbolo(
                lexema,
                resultado.token,
                resultado.tipo,
                lexema,
                linea,
                columna,
            )
            return

        self._registrar_error(104, linea, columna, "lexema '" + lexema + "'")

    def _leer_identificador_candidato(self, lector):
        inicio = lector.mirar()
        lexema = ""
        while True:
            siguiente = lector.mirar()
            if siguiente is None:
                break
            caracter = siguiente.caracter
            if (
                self.alfabeto.es_letra(caracter)
                or self.alfabeto.es_digito(caracter)
                or self.alfabeto.es_guion_bajo(caracter)
            ):
                lexema += lector.leer().caracter
                continue
            break
        return lexema, inicio.linea, inicio.columna

    def _leer_numero_candidato(self, lector):
        inicio = lector.mirar()
        lexema = ""
        while True:
            siguiente = lector.mirar()
            if siguiente is None:
                break
            caracter = siguiente.caracter
            if (
                self.alfabeto.es_digito(caracter)
                or self.alfabeto.es_punto(caracter)
                or self.alfabeto.es_letra(caracter)
                or self.alfabeto.es_guion_bajo(caracter)
            ):
                lexema += lector.leer().caracter
                continue
            break
        return lexema, inicio.linea, inicio.columna

    def _leer_cadena(self, lector):
        inicio = lector.mirar()
        lexema = ""
        caracter_invalido = None

        apertura = lector.leer()
        lexema += apertura.caracter

        while True:
            siguiente = lector.mirar()
            if siguiente is None:
                break

            caracter = siguiente.caracter
            if self.alfabeto.es_salto_linea(caracter):
                break

            leido = lector.leer()
            lexema += leido.caracter

            if not self.alfabeto.pertenece(leido.caracter) and caracter_invalido is None:
                caracter_invalido = leido

            if self.alfabeto.es_comilla(leido.caracter):
                break

        return lexema, inicio.linea, inicio.columna, caracter_invalido

    def _leer_operador(self, lector):
        inicio = lector.mirar()
        primero = lector.leer()
        lexema = primero.caracter

        siguiente = lector.mirar()
        if siguiente is not None and siguiente.caracter == "=" and primero.caracter in "><!":
            lexema += lector.leer().caracter

        return lexema, inicio.linea, inicio.columna

    def _agregar_simbolo(self, lexema, token, tipo, valor, linea, columna):
        self.tabla_simbolos.agregar(lexema, token, tipo, valor, linea, columna)
        self.traza.token_aceptado(lexema, token, tipo)

    def _registrar_error(self, codigo, linea, columna, detalle):
        error = self.pila_errores.apilar(codigo, linea, columna, detalle)
        self.traza.error_detectado(error.codigo, error.descripcion, error.linea, error.columna)

    @staticmethod
    def _valor_numerico(lexema, tipo):
        if tipo == "ENTERO":
            return int(lexema)
        return float(lexema)
