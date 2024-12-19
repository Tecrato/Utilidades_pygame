from typing import Tuple, Literal
import pygame as pag

class Barra_de_progreso:
    def __init__(self, pos: Tuple[int,int], size: int|tuple[int,int], orientacion: Literal['vertical','horizontal'] = 'vertical',
                 border_color: tuple[int,int,int] = (0,255,0), fill_color: tuple[int,int,int] = (0,128,255), border_width: int = 2):
        self.__size = pag.Vector2(size)
        self.__pos = pag.Vector2(pos)
        self.orientacion = orientacion
        self.border_color = border_color
        self.fill_color = fill_color
        self.border_width = border_width
        self.rect = pag.rect.Rect(0, 0, *self.__size)
        self.rect2 = pag.rect.Rect(0, 0, *self.__size)
        self.__volumen = 1.0
        if orientacion == 'vertical':
            self.rect.bottomleft = self.__pos
            self.rect2.bottomleft = self.__pos
        elif orientacion == 'horizontal':
            self.rect.topleft = self.__pos
            self.rect2.topleft = self.__pos

    def pulsando(self) -> None:
        g,k = pag.mouse.get_pos()
        if self.orientacion == 'vertical':
            if self.rect2.bottom - k > self.__size.y:
                self.rect.height = self.__size.y
            elif self.rect2.bottom - k < 0:
                self.rect.height = 0
            else:
                self.rect.height = self.rect2.bottom - k
            self.rect.bottom = self.pos[1]
            self.volumen = float(self.rect.height / self.__size.y)
        elif self.orientacion == 'horizontal':
            if self.rect2.left + g > self.__size.x:
                self.rect.w = self.__size.x
            elif self.rect2.left + g < 0:
                self.rect.w = 0
            else:
                self.rect.w = self.rect2.bottom - g
            self.volumen = float(self.rect.w / self.__size.x)

    def draw(self,surface) -> None:
        pag.draw.rect(surface, self.border_color, self.rect)
        pag.draw.rect(surface, self.fill_color, self.rect2, width=self.border_width)
        return (self.rect2,)

    def update(self):
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
        if self.orientacion == 'vertical':
            self.rect.height = self.__size.y*volumen
            self.rect.bottom = self.pos[1]
        elif self.orientacion == 'horizontal':
            self.rect.w = self.__size.x*volumen

    @property
    def size(self):
        return self.__size
    @size.setter
    def size(self,size):
        self.__size = pag.Vector2(size)
        self.rect = pag.rect.Rect(0, 0, *self.__size)
        self.rect2 = pag.rect.Rect(0, 0, *self.__size)
        self.volumen = self.__volumen

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