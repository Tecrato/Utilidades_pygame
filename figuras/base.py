from pygame import Rect, draw
from typing import List, Tuple
from abc import abstractmethod

class BasePolygon:
	"""Clase base para polígonos con el protocolo de dibujado de la librería."""
	def __init__(self,
				 pos: Tuple[float, float],
				 radio: float,
				 angle: float,
				 color: Tuple[int,int,int]|str = 'white'):
		self.color = color
		self.__pos = pos
		self.__radio = radio
		self.__angle = angle
		self.__figure: List[Tuple[float, float]] = []
		self.__rect: Rect = Rect(0, 0, 0, 0)
		self.redraw = 2
		self.last_rect = Rect(0,0,0,0)
		self.use_mouse_wheel = False

	@abstractmethod
	def __generate(self): ...

	# ==================== PROPIEDADES OPTIMIZADAS ====================
	@property
	def pos(self) -> Tuple[float, float]:
		return self.__pos
	@pos.setter
	def pos(self, value: Tuple[float, float]):
		self.__pos = value
		self.__generate()
		self.__update_bounding_box()

	@property
	def radio(self) -> float:
		return self.__radio
	@radio.setter
	def radio(self, value: float):
		if self.__radio != value:
			self.__radio = value
			self.__generate()
			self.__update_bounding_box()

	@property
	def angle(self) -> float:
		return self.__angle
	@angle.setter
	def angle(self, value: float):
		if self.__angle != value:
			self.__angle = float(value)
			self.__generate()
	@property
	def height(self) -> float:
		return self.rect.height
	
	@property
	def width(self) -> float:
		return self.rect.width
	
	def update_hover(self,mouse_pos):
		return

	# ==================== CAJA DE COLISIÓN (AABB) ====================

	def __update_bounding_box(self):
		"""Actualiza el AABB (Axis-Aligned Bounding Box) del polígono"""
		if not self.__figure:
			self.__rect = Rect(0, 0, 0, 0)
			return
		self.__rect = Rect(0,0,self.radio*2,self.radio*2)
		self.__rect.center = self.pos
		self.redraw += 2

	# ==================== MÉTODOS DE INTERFAZ PÚBLICA ====================
	def draw(self, surface, diff_pos = None) -> list[Rect]:
		"""Renderizado optimizado"""
		if len(self.__figure) < 3 or self.redraw < 1:
			return []
		draw.polygon(surface, self.color, self.__figure)
		if self.redraw < 2:
			self.redraw = 0
			return (self.rect,)
		else:
			self.redraw = 0
			r = self.last_rect.union(self.rect.copy()).copy()
			self.last_rect = self.rect.copy()
			return (self.rect, r)
		
	def update(self, *args, **kwargs):
		pass
		
	@property
	def rect(self):
		"""Rectángulo de colisión actualizado dinámicamente"""
		return self.__rect
	@property
	def figura(self) -> List[Tuple[float, float]]:
		return self.__figure
		
	def collide(self, rect):
		return self.rect.colliderect(rect)

	def is_hover(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)
	
	def on_wheel(self, val):
		return False