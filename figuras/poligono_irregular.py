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
        self._generate()
        self._update_bounding_box()

    def _generate(self):
        """Generación vectorizada con transformaciones in situ"""
        pos, radio, angle = self.pos, self.radio, self.angle
        self._set_figura([
            (
                pos[0] + cos(radians(p[0] + angle)) * p[1] * radio,
                pos[1] - sin(radians(p[0] + angle)) * p[1] * radio
            ) for p in self.__puntos
        ])
        self.redraw += 2

    def actualizar_punto(self, index: int, **kwargs):
        """Actualización parcial de un punto con invalidación selectiva"""
        if 'angle' in kwargs or 'radio' in kwargs:
            self.__puntos[index].update(kwargs)
            self._generate()
        self._update_bounding_box()

    