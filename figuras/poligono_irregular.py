from typing import Literal
from pathlib import Path
from .base import Base
from math import cos, sin, radians


class Poligono_irregular(Base):
	'''
	# Contiene las siguientes figuras pre-establecidas:
	- "flecha"
	- "estrella"
	- "rectangulo"
	- "x"
	## O tambien puede personalizar su figura:
	- coordenadas en una lista mediante la variable type
	- nombre del archivo con un formato valido.
	'''
	def __init__(self, type: list[dict[Literal["angle"],Literal["radio"]]]|Literal['flecha','x','rectangulo','estrella']|Path|str, pos = (0,0), radio=20, angle=0,color='white') -> None:
		super().__init__(pos,radio,angle,color)
		self.type = type
		if self.type in ['flecha','x','rectangulo','estrella']:
			self.import_file(f'{self.type}.txt')
			self.figure = self.generate_irregular_polygon(self.type)
		self.generate()

	def generate(self) -> None:
		self.figure = self.generate_irregular_polygon(self.type)

	def generate_irregular_polygon(self,l) -> list:#
		nose = []
		xs = [self.x + cos(radians(a['angle']+self.angle)) * a['radio'] * self.radio for a in l]
		ys = [self.y - sin(radians(a['angle']+self.angle)) * a['radio'] * self.radio for a in l]
		for x,y in zip(xs,ys):
			nose.append((x,y))
		return nose

	def import_file(self, path):
		self.type = [{'angle':float(a), 'radio':float(s)} for a,s in [x.split(',') for x in open(Path(__file__).parent.joinpath(f'./{path}'),'r').readline().split('|')]]
		# self.figure = [(self.pos.x + cos(radians(l['angle'] + self.angle))*self.radio*l['radio'],self.pos.y - sin(radians(l['angle'] + self.angle)) * self.radio*l['radio']) for l in string]

	def __str__(self):
		return f'Poligono irregular tipo={self.type} en={self.pos} angulo={self.angle}'
	
