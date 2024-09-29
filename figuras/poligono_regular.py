from .base import Base
from math import cos, sin, radians
from pygame import Vector2

class Poligono_regular(Base):
	def __init__(self, pos = Vector2(0,0), radio=20, lados=4, angle= 0,color='white') -> None:
		super().__init__(pos,radio,angle,color)
		self.__lados = lados
		self.type = type
		assert self.lados > 3
		self.generate()

	def generate(self) -> None:
		xs = [self.pos.x + cos(radians(360/self.__lados*a +self.angle)) * self.radio for a in range(self.__lados)]
		ys = [self.pos.y - sin(radians(360/self.__lados*a +self.angle)) * self.radio for a in range(self.__lados)]
		self.figure = [list((x,y)) for x,y in zip(xs,ys)]

	@property
	def lados(self) -> int:
		return self.__lados
	@lados.setter
	def lados(self,lados):
		self.__lados = lados
		self.generate()

