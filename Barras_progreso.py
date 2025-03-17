from typing import Tuple, Literal
from .Animaciones import Second_Order_Dinamics
import pygame as pag

class Barra_de_progreso:
    def __init__(
            self, pos: Tuple[int,int], size: int|tuple[int,int], orientacion: Literal['vertical','horizontal'] = 'vertical',
            border_color: tuple[int,int,int] = (0,128,255), fill_color: tuple[int,int,int] = (0,255,0), border_width: int = 2,
            smoth = False
            ):
        self.__size = pag.Vector2(size)
        self.__pos = pag.Vector2(pos)
        self.orientacion = orientacion
        self.border_color = border_color
        self.fill_color = fill_color
        self.border_width = border_width
        self.rect = pag.rect.Rect(0, 0, *self.__size)
        self.rect2 = pag.rect.Rect(0, 0, *self.__size)
        self.__volumen = 1.0
        self.redraw = 2
        self.smoth = smoth
        self.smoth_movent = Second_Order_Dinamics(60, 1.5, 1, 1.5, 0)
        if self.orientacion == 'vertical':
            self.rect.bottomleft = self.__pos
            self.rect2.bottomleft = self.__pos
        elif self.orientacion == 'horizontal':
            self.rect.topleft = self.__pos
            self.rect2.topleft = self.__pos

    def pulsando(self) -> None:
        m_x, m_y = pag.mouse.get_pos()
        if self.orientacion == 'vertical':
            if self.rect2.bottom - m_y > self.__size.y:
                self.rect.height = self.__size.y
            elif self.rect2.bottom - m_y < 0:
                self.rect.height = 0
            else:
                self.rect.height = self.rect2.bottom - m_y
            self.rect.bottom = self.pos[1]
            self.volumen = float(self.rect.height / self.__size.y)
        elif self.orientacion == 'horizontal':
            if self.rect2.left + m_x > self.__size.x:
                self.rect.w = self.__size.x
            elif self.rect2.left + m_x < 0:
                self.rect.w = 0
            else:
                self.rect.w = self.rect2.left + m_x
            self.volumen = float(self.rect.w / self.__size.x)
        

    def draw(self,surface, *, always_draw=False, **kwargs) -> None:
        if always_draw:
            self.redraw = 2
        pag.draw.rect(surface, self.fill_color, self.rect)
        pag.draw.rect(surface, self.border_color, self.rect2, width=self.border_width)
        return (self.rect2,)

    def update(self, dt=1, **kwargs):
        self.redraw = 2
        if self.smoth:
            v = self.smoth_movent.update(self.__volumen)[0]
        else:
            v = self.__volumen
        if self.orientacion == 'vertical':
            self.rect.height = self.__size.y*v
            self.rect.bottom = self.pos[1]
        elif self.orientacion == 'horizontal':
            self.rect.w = self.__size.x*v
        pass

    @property
    def volumen(self):
        return self.__volumen
    @volumen.setter
    def volumen(self,volumen):
        if volumen > 1:
            volumen = 1
        elif volumen < 0:
            volumen = 0

        self.__volumen = float(volumen)

    @property
    def size(self):
        return self.__size
    @size.setter
    def size(self,size):
        self.__size = pag.Vector2(size)
        self.rect = pag.rect.Rect(0, 0, *self.__size)
        self.rect2 = pag.rect.Rect(0, 0, *self.__size)

    @property
    def pos(self):
        return self.__pos
    @pos.setter
    def pos(self,pos):
        self.__pos = pag.Vector2(pos)
        if self.orientacion == 'vertical':
            self.rect.bottomleft = self.__pos
            self.rect2.bottomleft = self.__pos
        elif self.orientacion == 'horizontal':
            self.rect.topleft = self.__pos
            self.rect2.topleft = self.__pos

    @property
    def collide_rect(self) -> str:
        return self.rect2
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect2.colliderect(rect)
    def collide_all(self, lista: list) -> str:
        lista = []
        for i,x in enumerate(lista):
            if x.collide(self.collide_rect):
                lista.append(i)
        return lista