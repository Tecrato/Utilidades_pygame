from pygame import draw, Rect
from typing import Tuple
from math import cos, sin, radians
from .base import BasePolygon

class Engranaje(BasePolygon):
	def __init__(
			self, pos: Tuple[float, float], 
			dientes: int, 
			size_diente: float, 
			radio: float, 
			angle: float = 0, 
			color: Tuple[int, int, int] = (255, 255, 255),
			cell_size: float = 100.0,
			circle = True
		):
		
		super().__init__(pos, radio, angle, cell_size, color)
		self._n_dientes = dientes
		self._size_diente = size_diente
		self._circle = circle
		self._generate()
		self._update_bounding_box()

	def _generate(self):
		"""Generación precisa de dientes cuadrados radiales"""
		vertices = []
		paso_angular = 360 / self.n_dientes
		radio_total = self._radio + self._size_diente
		
		for i in range(self.n_dientes):
			angulo_central = radians(paso_angular * i + self._angle)
			
			# Base inicio
			vertices.append(
				(
					self._pos[0] + cos(angulo_central - radians(paso_angular/4)) * self._radio,
					self._pos[1] - sin(angulo_central - radians(paso_angular/4)) * self._radio
				)
			)
			# Punta inicio
			vertices.append(
				(
					self._pos[0] + cos(angulo_central - radians(paso_angular/8)) * radio_total,
					self._pos[1] - sin(angulo_central - radians(paso_angular/8)) * radio_total
				)
			)

			# Base fin
			vertices.append(
				(
					self._pos[0] + cos(angulo_central + radians(paso_angular/8)) * radio_total,
					self._pos[1] - sin(angulo_central + radians(paso_angular/8)) * radio_total
				)
			)
			# Punta fin
			vertices.append(
				(
					self._pos[0] + cos(angulo_central + radians(paso_angular/4)) * self._radio,
					self._pos[1] - sin(angulo_central + radians(paso_angular/4)) * self._radio
				)
			)
			
		# Suavizar transiciones entre dientes
		self._figure = vertices
		self._edges = list(zip(self._figure, self._figure[1:] + self._figure[:1]))
		self._build_spatial_grid()
		self.redraw += 2

	def _update_bounding_box(self):
		"""Actualiza el AABB (Axis-Aligned Bounding Box) del polígono"""
		if not self._figure:
			self._rect = Rect(0, 0, 0, 0)
			return
		self._rect = Rect(0,0,self.radio*2 + self._size_diente*2,self.radio*2 + self._size_diente*2)
		self._rect.center = self.pos
		self.redraw += 2
		
	def collide(self, rect):
		return self.rect.colliderect(rect)
		
	def draw(self, surface) -> Rect:
		"""Renderizado optimizado"""
		a = super().draw(surface)
		if a and self._circle:
			draw.circle(surface, self.color, self._pos, self._radio)
		return a
	
	# Setters actualizados para regeneración automática
	@property
	def n_dientes(self) -> int:
		return self._n_dientes
	@n_dientes.setter
	def n_dientes(self, value: int):
		if value != self._n_dientes and value > 3:
			self._n_dientes = value
			self._generate()

	@property
	def size_diente(self) -> float:
		return self._size_diente
	@size_diente.setter
	def size_diente(self, value: float):
		if value != self._size_diente:
			self._size_diente = value
			self._generate()
			self._update_bounding_box()