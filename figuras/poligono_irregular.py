from typing import List, Dict, Tuple
from .base import BasePolygon
from math import sin, cos, radians

class PoligonoIrregular(BasePolygon):
    """Polígono irregular con soporte para formas complejas y actualización diferencial."""
    def __init__(self, 
                 puntos: List[Dict[str, float]], 
                 pos: Tuple[float, float] = (0, 0), 
                 radio: float = 20, 
                 angle: float = 0, 
                 cell_size: float = 50.0,
                 color='white'):
        super().__init__(pos, radio, angle, cell_size, color=color)
        self._puntos = puntos
        self._generate()
        self._update_bounding_box()

    def _generate(self):
        """Generación vectorizada con transformaciones in situ"""
        self._figure = [
            (
                self._pos[0] + cos(radians(p[0] + self._angle)) * p[1] * self._radio,
                self._pos[1] - sin(radians(p[0] + self._angle)) * p[1] * self._radio
            ) for p in self._puntos
        ]
        self._edges = list(zip(self._figure, self._figure[1:] + self._figure[:1]))
        self._build_spatial_grid()
        self.redraw += 2

    def actualizar_punto(self, index: int, **kwargs):
        """Actualización parcial de un punto con invalidación selectiva"""
        if 'angle' in kwargs or 'radio' in kwargs:
            self._puntos[index].update(kwargs)
            self._generate()
        self._update_bounding_box()

    