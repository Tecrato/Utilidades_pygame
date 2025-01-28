from typing import Self
import pygame as pag
from pygame import draw, Vector2, Rect
from Utilidades.optimize import memosize

@memosize
def to_surf(points, radio, color) -> pag.Surface:
	surf = pag.Surface((radio*2,radio*2))
	surf.fill((0,0,0,0))
	pag.draw.polygon(surf, color, points)
	return surf

class Base:
	def __init__(self,pos,radio,angle,color) -> None:
		self.__pos = Vector2(pos)
		self.x = self.__pos.x
		self.y = self.__pos.y
		self.__angle = angle
		self.__radio = radio
		self.__color = color
		self.max_radio = 0
		self.figure: list[dict] = []
		self.redraw = True

	def draw(self,surface) -> Rect:
		draw.polygon(surface,self.color,self.figure)
		return Rect(0,0,self.radio*2,self.radio*2).move(self.pos.x-self.radio,self.pos.y-self.radio)

	def get_surface(self) -> pag.Surface:
		return to_surf(self.figure, int(self.radio), self.color)
	
	@property
	def pos(self) -> Vector2:
		return self.__pos
	@pos.setter
	def pos(self,pos):
		self.x = pos[0]
		self.y = pos[1]
		diferencia = Vector2(pos) - self.__pos
		self.__pos = Vector2(pos)
		for i,x in enumerate(self.figure):
			self.figure[i] = (x[0]+diferencia[0],x[1]+diferencia[1])
		# self.generate()
	@property
	def angle(self) -> float:
		return float(self.__angle)
	@angle.setter
	def angle(self,angle):
		self.__angle = float(angle)
		self.generate()
	@property
	def radio(self) -> int:
		return self.__radio
	@radio.setter
	def radio(self,radio):
		self.__radio = int(radio)
		self.generate()
	@property
	def color(self):
		return self.__color
	@color.setter
	def color(self,color):
		self.__color = color

	def copy(self) -> Self:
		return self
	@property
	def edges(self) -> list:
		return self.figure

