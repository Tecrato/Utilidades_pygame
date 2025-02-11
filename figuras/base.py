from pygame import Rect, draw
from typing import List, Tuple, Dict, Union
from math import hypot
import itertools

class BasePolygon:
	"""Clase base optimizada para polígonos con aceleración espacial."""
	def __init__(self, 
				 pos: Tuple[float, float], 
				 radio: float, 
				 angle: float, 
				 cell_size: float = 50.0,
				 color = 'white'):
		self.color = color
		self._pos = pos
		self._radio = radio
		self._angle = angle
		self.cell_size = cell_size
		self._figure: List[Tuple[float, float]] = []
		self._edges: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
		self._spatial_grid: Dict[Tuple[int, int], List[int]] = {}
		self._rect: Rect = Rect(0, 0, 0, 0)
		self.redraw = 2
		self.last_rect = Rect(0,0,0,0)

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
	
	def update_hover(self,mouse_pos):
		return

	# ==================== MÉTODOS DE CACHÉ Y ACELERACIÓN ====================

	def _build_spatial_grid(self):
		"""Construye una malla espacial para acelerar consultas de colisión"""
		self._spatial_grid.clear()
		for idx, ((x1, y1), (x2, y2)) in enumerate(self._edges):
			min_x, min_y = min(x1, x2), min(y1, y2)
			max_x, max_y = max(x1, x2), max(y1, y2)
			
			# Calcular celdas cubiertas por el borde
			start_cell = (int(min_x//self.cell_size), int(min_y//self.cell_size))
			end_cell = (int(max_x//self.cell_size), int(max_y//self.cell_size))
			
			for cx in range(start_cell[0], end_cell[0] + 1):
				for cy in range(start_cell[1], end_cell[1] + 1):
					cell = (cx, cy)
					if cell not in self._spatial_grid:
						self._spatial_grid[cell] = []
					self._spatial_grid[cell].append(idx)

	def _update_bounding_box(self):
		"""Actualiza el AABB (Axis-Aligned Bounding Box) del polígono"""
		if not self._figure:
			self._rect = Rect(0, 0, 0, 0)
			return
		self._rect = Rect(0,0,self.radio*2,self.radio*2)
		self._rect.center = self.pos
		self.redraw += 2

	# ==================== MÉTODOS DE INTERFAZ PÚBLICA ====================
	def get_edges_near(self, bbox: Tuple[float, float, float, float]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
		"""Obtiene bordes cercanos usando la malla espacial (versión corregida)"""
		# Eliminar la verificación de versión obsoleta
		return [self._edges[i] for i in self._get_edge_indices_near(bbox)]

	def _get_edge_indices_near(self, bbox: Tuple[float, float, float, float]) -> set:
		"""Obtiene índices de bordes en celdas cercanas"""
		min_x, min_y, max_x, max_y = bbox
		cells = set()
		
		for x in range(int(min_x//self.cell_size), int(max_x//self.cell_size) + 1):
			for y in range(int(min_y//self.cell_size), int(max_y//self.cell_size) + 1):
				cells.add((x, y))
		
		return set(itertools.chain.from_iterable(
			self._spatial_grid.get(cell, []) for cell in cells
		))

	def intersects_line(self, line_start: Tuple[float, float], line_end: Tuple[float, float]) -> List[Tuple[float, float]]:
		"""Versión ultra optimizada de intersección línea-polígono"""
		intersections = []
		
		# Consulta espacial
		line_bbox = (
			min(line_start[0], line_end[0]),
			min(line_start[1], line_end[1]),
			max(line_start[0], line_end[0]),
			max(line_start[1], line_end[1])
		)
		
		for edge in self.get_edges_near(line_bbox):
			# Detección temprana con AABB
			edge_bbox = (
				min(edge[0][0], edge[1][0]),
				min(edge[0][1], edge[1][1]),
				max(edge[0][0], edge[1][0]),
				max(edge[0][1], edge[1][1])
			)
			
			if not (line_bbox[2] < edge_bbox[0] or line_bbox[0] > edge_bbox[2] or
					line_bbox[3] < edge_bbox[1] or line_bbox[1] > edge_bbox[3]):
				# Cálculo preciso de intersección
				intersect = self._line_intersection(line_start, line_end, edge[0], edge[1])
				if intersect:
					intersections.append(intersect)
		
		# Ordenar por distancia al inicio de la línea
		intersections.sort(key=lambda p: hypot(p[0]-line_start[0], p[1]-line_start[1]))
		return intersections

	# ==================== MÉTODOS AUXILIARES ====================
	@staticmethod
	def _line_intersection(a1: Tuple[float, float], a2: Tuple[float, float], 
						 b1: Tuple[float, float], b2: Tuple[float, float]) -> Union[Tuple[float, float], None]:
		"""Algoritmo de intersección línea-línea con tolerancia numérica"""
		denom = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
		if abs(denom) < 1e-10:
			return None
		
		u = ((b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])) / denom
		t = ((a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])) / denom
		
		if 0 <= u <= 1 and 0 <= t <= 1:
			return (a1[0] + u * (a2[0] - a1[0]), a1[1] + u * (a2[1] - a1[1]))
		return None

	def draw(self, surface) -> list[Rect]:
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
	def figura(self) -> int:
		return self._figure
		
	def collide(self, rect):
		return self.rect.colliderect(rect)