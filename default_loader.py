import pygame as pag
from .figuras.engranajes import Engranaje
from .obj_Base import Base as obj_base

class Loader:
    def __init__(self, pos) -> None:
        self.__pos = pos
        self.redraw = 1
        self.updates = []

        self.engranajes: list[Engranaje] = [
            Engranaje((0,0), 8, 5, 20, 20),
            Engranaje((0,0), 8, 5, 20, 0),
            Engranaje((0,0), 4, 5, 10, 75),
        ]
        self.posicionar_engranajes()
        self.engranajes[0].color = (140,30,160)
        self.engranajes[1].color = (200,80,220)
        self.engranajes[2].color = (150,120,200)
        self.rect = self.engranajes[0].rect.unionall([r.rect for r in self.engranajes[1:]])

    def update(self, dt=1) -> None:
        self.engranajes[0].angle += 1
        self.engranajes[1].angle -= 1
        self.engranajes[2].angle += 2

    def draw(self, surface) -> pag.Rect:
        self.updates.clear()
        for x in self.engranajes:
            x.draw(surface)
            self.updates.append(x.rect)
        return self.updates

    def posicionar_engranajes(self):
        self.engranajes[0].pos = self.pos[0] - 40, self.pos[1] - 50
        self.engranajes[1].pos = self.pos[0] - 70, self.pos[1] - 20
        self.engranajes[2].pos = self.pos[0] - 91, self.pos[1] - 46

    @property
    def pos(self):
        return self.__pos
    @pos.setter
    def pos(self,pos):
        self.__pos = pos
        self.posicionar_engranajes()

        self.rect = self.engranajes[0].rect.unionall([r for r in self.engranajes[1:]])

    @property
    def collide_rect(self):
        return self.rect
    def collide(self, rect: pag.Rect) -> bool:
        return self.collide_rect.colliderect(rect)
    def collide_all(self, lista) -> str:
        lista = []
        for i,x in enumerate(lista):
            if x.collide(self.collide_rect):
                lista.append(i)
        return lista
    def get_update_rects(self):
        return [self.collide_rect]
    

class Loader_Bar(obj_base):
    def __init__(self, pos, width=100, height=30):
        super().__init__(pos, 'center')
        self.x = 0
        self.pos = pos
        self.vel = 5
        self.max_vel = 5
        self.aceleration = 0.5
        self.ratio_width = 3
        self.width = width
        self.inside_r_width = self.width/self.ratio_width
        self.height = height
        self.rect.width = self.width
        self.rect.height = self.height
        self.direccion(self.rect)
        self.create_border(self.rect, 0)

    def update(self, **kwargs):
        if (self.aceleration > 0 and self.vel < 5) or (self.aceleration < 0 and self.vel > -5):
            self.vel += self.aceleration

        self.x += self.vel
        if (self.x > self.width and self.aceleration > 0) or (self.x < 0 and self.aceleration < 0):
            self.x -= self.vel
            self.aceleration = -self.aceleration
        
        return super().update(**kwargs)
    
    def draw(self,ventana: pag.Surface):
        if self.visible is False:
            return []

        diferencia = 0
        x = int(self.x-self.inside_r_width/2)
        if self.x+self.inside_r_width/2 > self.rect.width:
            diferencia = self.x+self.inside_r_width/2 - self.rect.width
        elif self.x-self.inside_r_width/2 < 0:
            diferencia = -(self.x-self.inside_r_width/2)
            x += diferencia
        w = self.inside_r_width - diferencia
        pag.draw.rect(ventana, 'green', pag.Rect(self.rect.x + x, self.rect.y, w, self.height))
        pag.draw.rect(ventana, 'white', self.rect, 2)

        return [self.rect]
    