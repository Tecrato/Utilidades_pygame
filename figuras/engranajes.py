from pygame import draw, Rect
from .base import Base
from math import cos, sin, radians
from .poligono_regular import Poligono_regular

class Engranaje(Base):
	def __init__(self,pos, dientes, size_diente, radio,angle=0,color='white') -> None:
		super().__init__(pos,radio,angle,color)
		self.n_dientes = dientes
		self.size_diente = size_diente
		self.dientes = []

	def generate(self):
		self.dientes = [Poligono_regular((self.pos.x + cos(radians(360/self.n_dientes*a +self.angle+45)) * self.radio,self.pos.y - sin(radians(360/self.n_dientes*a +self.angle+45)) * self.radio), self.size_diente,4,360/self.n_dientes*a +self.angle) for a in range(self.n_dientes)]
		
	def draw(self,surface) -> Rect:
		for x in self.dientes:
			draw.polygon(surface,self.color,x.figure)
		draw.circle(surface, self.color, self.pos,self.radio)
		
		s = (self.radio + self.size_diente)
		return Rect(0,0,s*2,s*2).move(self.pos.x-s,self.pos.y-s)
