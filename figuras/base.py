from pygame import Rect, draw
from typing import List, Tuple

class BasePolygon:
	"""Clase base para polígonos con el protocolo de dibujado de la librería."""
	def __init__(self,
				 pos: Tuple[float, float],
				 radio: float,
				 angle: float,
				 color = 'white'):
		self.color = color
		self._pos = pos
		self._radio = radio
		self._angle = angle
		self._figure: List[Tuple[float, float]] = []
		self._rect: Rect = Rect(0, 0, 0, 0)
		self.redraw = 2
		self.last_rect = Rect(0,0,0,0)
		self.use_mouse_wheel = False

	# ==================== PROPIEDADES OPTIMIZADAS ====================
	@property
	def pos(self) -> Tuple[float, float]:
		return self._pos
	@pos.setter
	def pos(self, value: Tuple[float, float]):
		self._pos = value
		self._generate()
		self._update_bounding_box()

	@property
	def radio(self) -> float:
		return self._radio
	@radio.setter
	def radio(self, value: float):
		if self._radio != value:
			self._radio = value
			self._generate()
			self._update_bounding_box()

	@property
	def angle(self) -> float:
		return self._angle
	@angle.setter
	def angle(self, value: float):
		if self._angle != value:
			self._angle = float(value)
			self._generate()
	@property
	def height(self) -> float:
		return self.rect.height
	
	@property
	def width(self) -> float:
		return self.rect.width
	
	def update_hover(self,mouse_pos):
		return

	# ==================== CAJA DE COLISIÓN (AABB) ====================

	def _update_bounding_box(self):
		"""Actualiza el AABB (Axis-Aligned Bounding Box) del polígono"""
		if not self._figure:
			self._rect = Rect(0, 0, 0, 0)
			return
		self._rect = Rect(0,0,self.radio*2,self.radio*2)
		self._rect.center = self.pos
		self.redraw += 2

	# ==================== MÉTODOS DE INTERFAZ PÚBLICA ====================
	def draw(self, surface, diff_pos = None) -> list[Rect]:
		"""Renderizado optimizado"""
		if len(self._figure) < 3 or self.redraw < 1:
			return []
		draw.polygon(surface, self.color, self._figure)
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
		return self._rect
	@property
	def figura(self) -> List[Tuple[float, float]]:
		return self._figure
		
	def collide(self, rect):
		return self.rect.colliderect(rect)

	def is_hover(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)
	
	def on_wheel(self, val):
		return False