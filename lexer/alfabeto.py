"""Definicion formal del alfabeto de DataCheck DSL.

Este modulo concentra los simbolos terminales basicos que el analizador
lexico puede leer. Cada clase de caracter se determina por pertenencia
explicita al alfabeto definido para el lenguaje.
"""


class CategoriaCaracter:
    """Etiquetas de clasificacion usadas por los AFD del lexer."""

    LETRA = "LETRA"
    DIGITO = "DIGITO"
    GUION_BAJO = "GUION_BAJO"
    PUNTO = "PUNTO"
    COMILLA = "COMILLA"
    OPERADOR = "OPERADOR"
    ESPACIO = "ESPACIO"
    SALTO_LINEA = "SALTO_LINEA"
    FIN_ARCHIVO = "FIN_ARCHIVO"
    DESCONOCIDO = "DESCONOCIDO"


class AlfabetoDataCheck:
    """Representa Sigma, el alfabeto permitido por el lenguaje.

    Recibe caracteres individuales y retorna su categoria formal. El lexer
    consulta este modulo antes de construir lexemas para detectar caracteres
    que no pertenecen al lenguaje.
    """

    LETRAS_MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    LETRAS_MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
    DIGITOS = "0123456789"
    OPERADORES = "><=!"
    ESPACIOS = " \t"
    SALTOS_LINEA = "\n\r"
    COMILLA = '"'
    GUION_BAJO = "_"
    PUNTO = "."

    def __init__(self):
        self._letras = set(self.LETRAS_MAYUSCULAS + self.LETRAS_MINUSCULAS)
        self._digitos = set(self.DIGITOS)
        self._operadores = set(self.OPERADORES)
        self._espacios = set(self.ESPACIOS)
        self._saltos_linea = set(self.SALTOS_LINEA)
        self._permitidos = set(
            self.LETRAS_MAYUSCULAS
            + self.LETRAS_MINUSCULAS
            + self.DIGITOS
            + self.OPERADORES
            + self.ESPACIOS
            + self.SALTOS_LINEA
            + self.COMILLA
            + self.GUION_BAJO
            + self.PUNTO
        )

    def pertenece(self, caracter):
        """Retorna True si el caracter pertenece al alfabeto Sigma."""
        return caracter in self._permitidos

    def es_letra(self, caracter):
        """Retorna True si el caracter pertenece a la clase LETRA."""
        return caracter in self._letras

    def es_digito(self, caracter):
        """Retorna True si el caracter pertenece a la clase DIGITO."""
        return caracter in self._digitos

    def es_guion_bajo(self, caracter):
        """Retorna True si el caracter es '_'."""
        return caracter == self.GUION_BAJO

    def es_punto(self, caracter):
        """Retorna True si el caracter es el punto decimal."""
        return caracter == self.PUNTO

    def es_comilla(self, caracter):
        """Retorna True si el caracter abre o cierra una cadena."""
        return caracter == self.COMILLA

    def es_operador(self, caracter):
        """Retorna True si el caracter puede iniciar un operador."""
        return caracter in self._operadores

    def es_espacio(self, caracter):
        """Retorna True para blancos horizontales."""
        return caracter in self._espacios

    def es_salto_linea(self, caracter):
        """Retorna True para saltos de linea reconocidos."""
        return caracter in self._saltos_linea

    def es_caracter_cadena(self, caracter):
        """Retorna True si el caracter puede aparecer dentro de una cadena.

        Las comillas y los saltos de linea tienen transiciones propias en el
        AFD de cadenas, por eso se excluyen de esta clase.
        """
        return (
            self.pertenece(caracter)
            and not self.es_comilla(caracter)
            and not self.es_salto_linea(caracter)
        )

    def categoria(self, caracter):
        """Clasifica un caracter individual en una categoria formal."""
        if caracter is None:
            return CategoriaCaracter.FIN_ARCHIVO
        if self.es_letra(caracter):
            return CategoriaCaracter.LETRA
        if self.es_digito(caracter):
            return CategoriaCaracter.DIGITO
        if self.es_guion_bajo(caracter):
            return CategoriaCaracter.GUION_BAJO
        if self.es_punto(caracter):
            return CategoriaCaracter.PUNTO
        if self.es_comilla(caracter):
            return CategoriaCaracter.COMILLA
        if self.es_operador(caracter):
            return CategoriaCaracter.OPERADOR
        if self.es_espacio(caracter):
            return CategoriaCaracter.ESPACIO
        if self.es_salto_linea(caracter):
            return CategoriaCaracter.SALTO_LINEA
        return CategoriaCaracter.DESCONOCIDO
