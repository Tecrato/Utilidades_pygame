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
		self.__generate()
		self.__update_bounding_box()

	def __generate(self):
		"""Generación precisa de dientes cuadrados radiales"""
		vertices = []
		paso_angular = 360 / self.n_dientes
		radio_total = self.__radio + self.__size_diente
		
		for i in range(self.n_dientes):
			angulo_central = radians(paso_angular * i + self.__angle)
			
			# Base inicio
			vertices.append(
				(
					self.__pos[0] + cos(angulo_central - radians(paso_angular/4)) * self.__radio,
					self.__pos[1] - sin(angulo_central - radians(paso_angular/4)) * self.__radio
				)
			)
			# Punta inicio
			vertices.append(
				(
					self.__pos[0] + cos(angulo_central - radians(paso_angular/8)) * radio_total,
					self.__pos[1] - sin(angulo_central - radians(paso_angular/8)) * radio_total
				)
			)

			# Base fin
			vertices.append(
				(
					self.__pos[0] + cos(angulo_central + radians(paso_angular/8)) * radio_total,
					self.__pos[1] - sin(angulo_central + radians(paso_angular/8)) * radio_total
				)
			)
			# Punta fin
			vertices.append(
				(
					self.__pos[0] + cos(angulo_central + radians(paso_angular/4)) * self.__radio,
					self.__pos[1] - sin(angulo_central + radians(paso_angular/4)) * self.__radio
				)
			)
			
		# Suavizar transiciones entre dientes
		self.__figure = vertices
		self.redraw += 2

	def __update_bounding_box(self):
		"""Actualiza el AABB (Axis-Aligned Bounding Box) del polígono"""
		if not self.__figure:
			self.__rect = Rect(0, 0, 0, 0)
			return
		self.__rect = Rect(0,0,self.radio*2 + self.__size_diente*2,self.radio*2 + self.__size_diente*2)
		self.__rect.center = self.pos
		self.redraw += 2
		
	def collide(self, rect):
		return self.rect.colliderect(rect)
		
	def draw(self, surface) -> list[Rect]:
		"""Renderizado optimizado"""
		a = super().draw(surface)
		if a and self.__circle:
			draw.circle(surface, self.color, self.__pos, self.__radio)
		return a
	
	# Setters actualizados para regeneración automática
	@property
	def n_dientes(self) -> int:
		return self.__n_dientes
	@n_dientes.setter
	def n_dientes(self, value: int):
		if value != self.__n_dientes and value > 3:
			self.__n_dientes = value
			self.__generate()

	@property
	def size_diente(self) -> float:
		return self.__size_diente
	@size_diente.setter
	def size_diente(self, value: float):
		if value != self.__size_diente:
			self.__size_diente = value
			self.__generate()
			self.__update_bounding_box()