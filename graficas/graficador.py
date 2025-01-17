# este modulo es para graficar funciones
# constara de una clase que genera una suface de pygame hecha para ser impresa en las ventanas de cualquier apliaccion
# la clase tendra un metodo que recibe una ecuacion y la grafica
import pygame as pag
import math
import random
from Utilidades import memosize, line_intersect

from ..obj_Base import Base
from ..texts import Text

@memosize
def numero(num,size) -> Text:
    return Text(num, size, None, (0, 0))

@memosize
def eval_func(ec,condition,x):
    try:
        if eval(condition):
            y = eval(ec)
            return (x, -y)
    except:
        return None


class Graficador(Base):
    def __init__(
            self, pos, ancho, alto, escala: int = 100,dire: str = 'center', background_color: tuple[int, int, int] = (0, 0, 0),
            scale_color: tuple[int, int, int] = (255, 255, 255), guide_lines_color: tuple[int, int, int] = (20, 20, 20),
            step: int = 15, grahpic_color: tuple[int, int, int] = (255, 255, 255), coords_size: int = 10, 
            coords_color: tuple[int, int, int]|None = None, border_width: int = -1, **kwargs
        ):
        super().__init__(pos,dire)
        
        self.ancho = ancho
        self.alto = alto
        self.escala = escala
        self.background_color = background_color
        self.limite = 1000
        self.__zoom = .5
        self.step: int = step
        self.coords_size = coords_size


        self.border_width = border_width
        self.border_color = kwargs.get('border_color', 'black')
        self.border_radius = kwargs.get('border_radius',0)
        self.border_top_left_radius = kwargs.get('border_top_left_radius',-1)
        self.border_bottom_left_radius = kwargs.get('border_bottom_left_radius',-1)
        self.border_top_right_radius = kwargs.get('border_top_right_radius',-1)
        self.border_bottom_right_radius = kwargs.get('border_bottom_right_radius',-1)

        
        self.coords_color = grahpic_color if coords_color is None else coords_color
        
        self.grahpic_color = grahpic_color
        
        self.scale_color = scale_color
        self.guide_lines_color = guide_lines_color
        
        self.ecuaciones = []
        self.puntos = []
        self.edge = pag.Vector2(ancho/2,alto/2)
        self.coords = []
        self.polygon = []

        self.surf = pag.Surface((self.ancho, self.alto))
        self.surf.fill(background_color)
        self.rect = self.surf.get_rect()
        self.direccion(self.rect)
        self.create_border(self.rect, self.border_width)
    
    def add_ecuacion(self,ec,condition):
        self.ecuaciones.append((str(ec),str(condition)))
        self.calcular_puntos()

    def calcular_puntos(self):
        self.puntos.clear()
        for i, (ec, condition) in enumerate(self.ecuaciones):
            self.puntos.append([])
            for x in range(0,self.ancho*2, self.step):
                x -= self.edge[0]
                x = x / (self.escala * self.zoom)
                
                point = eval_func(ec,condition,x)
                if not point:
                    continue
                point = (point[0] * self.escala * self.zoom) + self.edge[0], (point[1] * self.escala * self.zoom) + self.edge[1]
                self.puntos[i].append(point)
    
    def dibujar_escala(self):

        for x in range(-self.limite, self.limite):
            if x == 0: continue
            
            pos_x = x * self.escala * self.zoom + self.edge[0]
            pos_y = x * self.escala * self.zoom + self.edge[1]
            if pos_x > 0 and self.ancho > pos_x:
                pag.draw.line(self.surf, self.guide_lines_color, (pos_x, 0), (pos_x, self.alto),2)
            if pos_y > 0 and self.alto > pos_y:
                pag.draw.line(self.surf, self.guide_lines_color, (0, pos_y), (self.ancho, pos_y),2)
        for x in range(-self.limite, self.limite):
            if x == 0: continue
            pos_x = math.floor(x * self.escala * self.zoom + self.edge[0])
            pos_y = math.floor(x * self.escala * self.zoom + self.edge[1])
            
            if pos_x > 0 and self.ancho > pos_x:
                pag.draw.line(self.surf, self.scale_color, (pos_x, self.edge[1]), (pos_x, self.edge[1] + 10),2)
                num = numero(x,20 if self.zoom > .1 else 15)
                num.top = self.edge[1] + 15
                num.centerx = pos_x
                num.redraw = 2
                num.draw(self.surf)
            if pos_y > 0 and self.alto > pos_y:
                pag.draw.line(self.surf, self.scale_color, (self.edge[0], pos_y), (self.edge[0] + 10, pos_y),2)
                num = numero(x*-1,20 if self.zoom > .1 else 15)
                
                num.centery = pos_y
                num.left = self.edge[0]
                num.redraw = 2
                num.draw(self.surf)

    def add_coord(self,coord: tuple[int,int], color = None) -> None:
        self.coords.append({'coord': coord, 'color': color if color else self.coords_color})
    
    def crear_intercepciones(self):
        self.coords.clear()

        for i in range(len(self.ecuaciones)-1):
            for j in range(i+1,len(self.ecuaciones)):
                x = 0
                point1_1 = eval(self.ecuaciones[i][0])
                x = 100
                point2_1 = eval(self.ecuaciones[i][0])
                x= 0
                point1_2 = eval(self.ecuaciones[j][0])
                x = 100
                point2_2 = eval(self.ecuaciones[j][0])

            result = line_intersect((0,point1_1),(100,point2_1),(0,point1_2),(100,point2_2))
            if result:
                self.add_coord((result[0], result[1]),random.choice(pag.colordict.THECOLORS.keys()))
            
    def to_center(self):
        self.edge = pag.Vector2(self.ancho/2,self.alto/2)
    
    def draw(self, surface):
        self.surf.fill(self.background_color)
        pag.draw.line(self.surf, self.scale_color, (self.edge[0],self.edge[1] - 10000), (self.edge[0],self.edge[1] + 10000),2)
        pag.draw.line(self.surf, self.scale_color, (self.edge[0] - 10000,self.edge[1]), (self.edge[0] + 10000,self.edge[1]),2)
        self.dibujar_escala()
        for points_list in self.puntos:
            if len(points_list) < 2:
                continue
            pag.draw.lines(self.surf, self.grahpic_color, False, points_list)
        
        try:
            if len(self.polygon) > 2:
                l = [(x*self.escala*self.zoom+self.edge[0], -y*self.escala*self.zoom+self.edge[1]) for x,y in self.polygon]
                pag.draw.polygon(self.surf, self.grahpic_color, l)
        except Exception as e:
            print(e)
            print(self.polygon)
            raise e
        for coord in self.coords:
            x,y = coord['coord']
            pag.draw.circle(self.surf, coord['color'], (x*self.escala*self.zoom+self.edge[0], -y*self.escala*self.zoom+self.edge[1]), self.coords_size)
        surface.blit(self.surf, self.rect)
        pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius,
                      self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, 
                      self.border_bottom_right_radius)

    def resize(self, width, height):
        self.ancho = width
        self.alto = height

        self.surf = pag.Surface((self.ancho, self.alto))
        self.rect = self.surf.get_rect()
        self.direccion(self.rect)
        self.create_border(self.rect, self.border_width)

    @property
    def zoom(self):
        return self.__zoom

    @zoom.setter
    def zoom(self, value):
        self.__zoom = float(value)
        if self.__zoom >= 25:
            self.__zoom = 25
        elif self.__zoom <= .05:
            self.__zoom = .05
        self.calcular_puntos()

    @property
    def edge(self):
        return self.__edge

    @edge.setter
    def edge(self, value):
        self.__edge = pag.Vector2(value)
        self.calcular_puntos()
