import random
import pygame as pag

from ..Animaciones import Second_Order_Dinamics
from ..obj_Base import Base


class Barra:
    def __init__(self, data_x, data_y, start_pos = (0,0), smothmove = True, color = (255,255,255)):
        self.data_x = data_x
        self.data_y = data_y
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.smothmove = smothmove
        self.color = color

        self.cambio_tamaño = Second_Order_Dinamics(60,2,1.0,1.1, (0,0))
        self.cambio_posicion = Second_Order_Dinamics(60,2,1.0,1.1, start_pos)

        self.rect = pag.Rect(*start_pos,0,0)


    def update(self,pos,size):
        if self.smothmove:
            self.x,self.y = self.cambio_posicion.update(pos)
            self.width, self.height = self.cambio_tamaño.update(size)
        else:
            self.x,self.y = pos
            self.width, self.height = size

        self.rect.width = self.width
        self.rect.height = self.height
        self.rect.bottomleft = (self.x, self.y)

    def draw(self,surface):
        pag.draw.rect(surface, self.color, self.rect)


    def __eq__(self, other):
        return self.data_x == other.data_x and self.data_y == other.data_y
    def __lt__(self, other):
        return self.data_x < other.data_x

class Grafico_Barras(Base):
    def __init__(self, pos: pag.Vector2, width: int, height: int, direccion = "center", random_color=True):
        super().__init__(pos,direccion)
        self.surface = pag.Surface((width, height))
        self.rect = self.surface.get_rect()

        self.random_color = random_color

        self.width = width
        self.height = height

        self.max_y = 0

        self.barras: list[Barra] = []

    def update(self, dt=1):
        super().update()
        for i,x in enumerate(self.barras):
            rect = pag.Rect(0,0,0,0)
            rect.width = self.width / len(self.barras) - 2
            rect.height = x.data_y/self.max_y * self.height
            rect.bottomleft = (i * (self.width / len(self.barras)) + 1, self.height)
            x.update(rect.bottomleft, rect.size)


    def draw(self, surf):
        self.surface.fill((0,0,0))
        for x in self.barras:
            x.draw(self.surface)

        surf.blit(self.surface, self.rect)

    def append(self, x, y):
        color = [random.randint(0,255) for _ in range(3)] if self.random_color else (255,255,255)
        self.barras.append(Barra(x, y, (0, self.height), color=color))
        self.barras.sort()
        if y > self.max_y:
            self.max_y = y

    def __len__(self):
        return len(self.barras)