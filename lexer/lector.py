"""Lectura de archivos fuente para DataCheck DSL.

El lector consume el archivo con read(1), es decir, caracter por caracter. La
clase tambien ofrece mirar() para consultar el siguiente caracter sin
consumirlo, lo cual permite construir lexemas mediante exploracion secuencial.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CaracterLeido:
    """Caracter individual con su posicion exacta en el archivo fuente."""

    caracter: str
    linea: int
    columna: int
    indice: int


class LectorArchivo:
    """Lector secuencial con un unico caracter de anticipacion."""

    def __init__(self, ruta, traza=None, codificacion="utf-8-sig"):
        self.ruta = ruta
        self.traza = traza
        self.codificacion = codificacion
        self._archivo = None
        self._buffer = None
        self._linea_siguiente = 1
        self._columna_siguiente = 1
        self._indice_siguiente = 0

    def __enter__(self):
        self.abrir()
        return self

    def __exit__(self, tipo_excepcion, excepcion, traza_excepcion):
        self.cerrar()

    def abrir(self):
        """Abre el archivo fuente en modo texto."""
        self._archivo = open(self.ruta, "r", encoding=self.codificacion)

    def cerrar(self):
        """Cierra el archivo fuente si esta abierto."""
        if self._archivo is not None:
            self._archivo.close()
            self._archivo = None

    def mirar(self):
        """Retorna el siguiente caracter sin consumirlo."""
        if self._buffer is None:
            self._buffer = self._leer_fisico()
        return self._buffer

    def leer(self):
        """Consume y retorna un caracter del archivo fuente."""
        if self._buffer is not None:
            caracter = self._buffer
            self._buffer = None
        else:
            caracter = self._leer_fisico()

        if caracter is None:
            return None

        self._avanzar_posicion(caracter)
        if self.traza is not None:
            self.traza.caracter_leido(caracter)
        return caracter

    def _leer_fisico(self):
        if self._archivo is None:
            raise RuntimeError("El archivo fuente no esta abierto.")

        caracter = self._archivo.read(1)
        if caracter == "":
            return None

        return CaracterLeido(
            caracter=caracter,
            linea=self._linea_siguiente,
            columna=self._columna_siguiente,
            indice=self._indice_siguiente,
        )

    def _avanzar_posicion(self, caracter):
        if caracter.caracter == "\n":
            self._linea_siguiente += 1
            self._columna_siguiente = 1
        else:
            self._columna_siguiente += 1
        self._indice_siguiente += 1


class LectorTexto:
    """Lector secuencial para codigo fuente recibido como cadena.

    Expone la misma interfaz que LectorArchivo para que el lexer pueda operar
    sobre archivos locales o sobre texto enviado por la API sin duplicar reglas
    de tokenizacion.
    """

    def __init__(self, texto, traza=None):
        self.texto = texto
        self.traza = traza
        self._buffer = None
        self._linea_siguiente = 1
        self._columna_siguiente = 1
        self._indice_siguiente = 0

    def __enter__(self):
        return self

    def __exit__(self, tipo_excepcion, excepcion, traza_excepcion):
        return None

    def mirar(self):
        """Retorna el siguiente caracter sin consumirlo."""
        if self._buffer is None:
            self._buffer = self._leer_fisico()
        return self._buffer

    def leer(self):
        """Consume y retorna un caracter del texto fuente."""
        if self._buffer is not None:
            caracter = self._buffer
            self._buffer = None
        else:
            caracter = self._leer_fisico()

        if caracter is None:
            return None

        self._avanzar_posicion(caracter)
        if self.traza is not None:
            self.traza.caracter_leido(caracter)
        return caracter

    def _leer_fisico(self):
        if self._indice_siguiente >= len(self.texto):
            return None

        caracter = self.texto[self._indice_siguiente]
        return CaracterLeido(
            caracter=caracter,
            linea=self._linea_siguiente,
            columna=self._columna_siguiente,
            indice=self._indice_siguiente,
        )

    def _avanzar_posicion(self, caracter):
        if caracter.caracter == "\n":
            self._linea_siguiente += 1
            self._columna_siguiente = 1
        else:
            self._columna_siguiente += 1
        self._indice_siguiente += 1
