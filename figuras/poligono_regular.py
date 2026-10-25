from typing import Tuple
from .base import BasePolygon
from math import sin, cos, radians

class PoligonoRegular(BasePolygon):
    """Polígono regular con generación optimizada y caché de vértices."""
    def __init__(self, 
                 pos: Tuple[float, float] = (0, 0), 
                 lados: int = 4, 
                 radio: float = 10, 
                 angle: float = 0):
        super().__init__(pos, radio, angle)
        self._lados = lados
        self._generate()
        self.__update_bounding_box()

    def _generate(self):
        """Generación optimizada"""
        step = 360 / self._lados
        self.__figure = [
            (
                self.__pos[0] + cos(radians(step * i + self.__angle)) * self.__radio,
                self.__pos[1] - sin(radians(step * i + self.__angle)) * self.__radio
            ) for i in range(self._lados)
        ]
        self.redraw += 1

    @property
    def lados(self) -> int:
        return self._lados
    @lados.setter
    def lados(self, value: int):
        if self._lados != value and value > 3:
            self._lados = value
            self._generate()
