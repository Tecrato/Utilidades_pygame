from typing import List, Tuple
from .base import BasePolygon
from math import sin, cos, radians

class PoligonoIrregular(BasePolygon):
    """Polígono irregular con soporte para formas complejas y actualización diferencial."""
    def __init__(self, 
                 puntos: List[Tuple[float, float]], 
                 pos: Tuple[float, float] = (0, 0), 
                 radio: float = 20, 
                 angle: float = 0, 
                 color='white'):
        super().__init__(pos, radio, angle, color=color)
        self.__puntos = puntos
        self.__generate()
        self.__update_bounding_box()

    def __generate(self):
        """Generación vectorizada con transformaciones in situ"""
        self.__figure = [
            (
                self.__pos[0] + cos(radians(p[0] + self.__angle)) * p[1] * self.__radio,
                self.__pos[1] - sin(radians(p[0] + self.__angle)) * p[1] * self.__radio
            ) for p in self.__puntos
        ]
        self.redraw += 2

    def actualizar_punto(self, index: int, **kwargs):
        """Actualización parcial de un punto con invalidación selectiva"""
        if 'angle' in kwargs or 'radio' in kwargs:
            self.__puntos[index].update(kwargs)
            self.__generate()
        self.__update_bounding_box()

    