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
			color: Tuple[int, int, int]|str = (255, 255, 255),
			circle = True
		):
		
		super().__init__(pos, radio, angle, color)
		self.__n_dientes = dientes
		self.__size_diente = size_diente
		self.__circle = circle
		self._generate()
		self._update_bounding_box()

	def _generate(self):
		"""Generación precisa de dientes cuadrados radiales"""
		vertices = []
		paso_angular = 360 / self.n_dientes
		pos, radio, angle = self.pos, self.radio, self.angle
		radio_total = radio + self.__size_diente
		
		for i in range(self.n_dientes):
			angulo_central = radians(paso_angular * i + angle)
			
			# Base inicio
			vertices.append(
				(
					pos[0] + cos(angulo_central - radians(paso_angular/4)) * radio,
					pos[1] - sin(angulo_central - radians(paso_angular/4)) * radio
				)
			)
			# Punta inicio
			vertices.append(
				(
					pos[0] + cos(angulo_central - radians(paso_angular/8)) * radio_total,
					pos[1] - sin(angulo_central - radians(paso_angular/8)) * radio_total
				)
			)

			# Base fin
			vertices.append(
				(
					pos[0] + cos(angulo_central + radians(paso_angular/8)) * radio_total,
					pos[1] - sin(angulo_central + radians(paso_angular/8)) * radio_total
				)
			)
			# Punta fin
			vertices.append(
				(
					pos[0] + cos(angulo_central + radians(paso_angular/4)) * radio,
					pos[1] - sin(angulo_central + radians(paso_angular/4)) * radio
				)
			)
			
		# Suavizar transiciones entre dientes
		self._set_figura(vertices)
		self.redraw += 2

	def _update_bounding_box(self, size: float | None = None):
		"""El AABB del engranaje suma los dientes al radio."""
		super()._update_bounding_box((self.radio + self.__size_diente) * 2)
		
	def collide(self, rect):
		return self.rect.colliderect(rect)
		
	def draw(self, surface) -> list[Rect]:
		"""Renderizado optimizado"""
		a = super().draw(surface)
		if a and self.__circle:
			draw.circle(surface, self.color, self.pos, self.radio)
		return a
	
	# Setters actualizados para regeneración automática
	@property
	def n_dientes(self) -> int:
		return self.__n_dientes
	@n_dientes.setter
	def n_dientes(self, value: int):
		if value != self.__n_dientes and value > 3:
			self.__n_dientes = value
			self._generate()

	@property
	def size_diente(self) -> float:
		return self.__size_diente
	@size_diente.setter
	def size_diente(self, value: float):
		if value != self.__size_diente:
			self.__size_diente = value
			self._generate()
			self._update_bounding_box()