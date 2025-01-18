from typing import Literal, Self
import pygame as pag
from pygame import Vector2

from .Animaciones import Curva_de_Bezier, Second_Order_Dinamics, Simple_acceleration
from Utilidades import Hipotenuza

class Base:
    def __init__(self,pos,dire: Literal["left","right","top","bottom","center","topleft","topright","bottomleft","bottomright"]) -> None:
        self.rect = pag.Rect(0,0,50,50)
        self.smothmove_bool = False

        self.__dire: str = dire
        self.__pos = Vector2(pos)
        self.smothmove_pos = Vector2(0)
        self.rect_border = pag.rect.Rect(0,0,0,0)
        self.redraw: int = 2
        self.last_rect = pag.Rect(0,0,0,0)

    def create_border(self, rect, border_width) -> None:
        if border_width == -1:
            border_width = 0
        self.rect_border = pag.rect.Rect(0,0,rect.size[0] + border_width,rect.size[1] + border_width)
        self.rect_border.center = rect.center

    def direccion(self, rect) -> None:
        rect.center = self.__pos
        if self.redraw < 2:
            self.redraw += 2
        if self.dire == 'center':
            self.rect_border.center = rect.center
            return
        if self. dire in ['left','topleft','bottomleft']:
            rect.left = self.__pos.x
        elif self.dire in ['right','topright','bottomright']:
            rect.right = self.__pos.x

        if self.dire in ['top','topleft','topright']:
            rect.top = self.__pos.y
        elif self.dire in ['bottom','bottomleft','bottomright']:
            rect.bottom = self.__pos.y
        self.rect_border.center = rect.center
            
    def smothmove(self, T, f, z, r) -> None:
        self.smothmove_pos = self.pos
        self.movimiento = Second_Order_Dinamics(T, f, z, r, self.pos)
        self.smothmove_bool = True
        self.smothmove_type = 'Second order dinamics'
    def Cubic_bezier_move(self, fps, puntos, multiplicador:float = 1):
        self.smothmove_pos = self.pos
        self.smothmove_bool = True
        self.smothmove_type = 'Cubic Bezier'
        self.movimiento = Curva_de_Bezier(fps,puntos,multiplicador)
    def simple_acceleration_move(self, vel,dir=[1,0],tipo: Literal['follow','forward']='follow') -> None:
        self.smothmove_pos = self.pos
        self.movimiento = Simple_acceleration(vel, dir, self.pos)
        self.smothmove_bool = True
        self.smothmove_type = 'Simple Acceleration'
        self.simple_acceleration_type = tipo

        self.vel = float(vel)

        self.direccion(self.rect)

      
    def update(self,pos=None,dt=1, **kwargs) -> bool:
        if self.smothmove_bool is False or pos is None or not pos:
            return False
        elif pos:
            self.pos = pos
        elif self.__pos == self.smothmove_pos:
            return False
        
        if self.smothmove_type == 'Second order dinamics':
            if abs(sum(self.movimiento.yd.xy)) < 0.01:
                self.__pos = self.smothmove_pos
            self.__pos = Vector2(self.movimiento.update(self.smothmove_pos,dt=dt))
        elif self.smothmove_type == 'Simple Acceleration':
            if self.simple_acceleration_type == 'follow':
                self.__pos = self.movimiento.follow(self.smothmove_pos,dt=dt)
                self.redraw += 2
                if Hipotenuza(self.__pos,self.smothmove_pos) < self.vel+1:
                    self.__pos = self.smothmove_pos
            else:
                self.__pos = self.movimiento.update()
        elif self.smothmove_type == 'Cubic Bezier':
            r = self.movimiento.update(dt)

            if (r == True):
                self.smothmove_bool = False
                self.smothmove_type = None
            else:
                self.__pos = Vector2(r)
        
        self.direccion(self.rect)
        return True

    def move(self, pos):
        self.pos = pos

    @property
    def pos(self):
        return self.__pos if not self.smothmove_bool else self.smothmove_pos
    @property
    def raw_pos(self):
        return self.__pos
    @pos.setter
    def pos(self,pos:tuple[int,int]|Vector2):
        if self.smothmove_bool:
            self.smothmove_pos = Vector2(pos)
        else:
            self.__pos = Vector2(pos)
            self.direccion(self.rect)
    @property
    def dire(self) -> str:
        return self.__dire
    @dire.setter
    def dire(self,dire) -> None:
        self.__dire = dire
        self.direccion(self.rect)

    @property
    def left(self) -> int:
        return self.rect_border.left
    @left.setter
    def left(self,left) -> None:
        self.pos = (self.pos.x + (left - self.rect.left),self.pos.y)
    @property
    def right(self) -> int:
        return self.rect.right
    @right.setter
    def right(self,right) -> None:
        self.pos = (self.pos.x + (right - self.rect.right),self.pos.y)
    @property
    def top(self) -> int:
        return self.rect.top
    @top.setter
    def top(self,top) -> None:
        self.pos = (self.pos.x,self.pos.y + (top - self.rect.top))
    @property
    def bottom(self) -> int:
        return self.rect.bottom
    @bottom.setter
    def bottom(self,bottom) -> None:
        self.pos = (self.pos.x,self.pos.y + (bottom - self.rect.bottom))
    @property
    def topleft(self) -> Vector2:
        return Vector2(self.rect.topleft)
    @topleft.setter
    def topleft(self,topleft) -> None:
        self.pos = self.pos + (Vector2(topleft) - self.rect.topleft)
    @property
    def topright(self) -> Vector2:
        return Vector2(self.rect.topright)
    @topright.setter
    def topright(self,topright) -> None:
        self.pos = self.pos + (Vector2(topright) - self.rect.topright)
    @property
    def bottomleft(self) -> Vector2:
        return Vector2(self.rect.bottomleft)
    @bottomleft.setter
    def bottomleft(self,bottomleft) -> None:
        self.pos = self.pos + (Vector2(bottomleft) - self.rect.bottomleft)
    @property
    def bottomright(self) -> Vector2:
        return Vector2(self.rect.bottomright)
    @bottomright.setter
    def bottomright(self,bottomright) -> None:
        self.pos = self.pos + (Vector2(bottomright) - self.rect.bottomright)

    @property
    def center(self) -> Vector2:
        return Vector2(self.rect.center)
    @center.setter
    def center(self,center) -> None:
        self.pos = self.pos + (Vector2(center) - self.rect.center)
    @property
    def centerx(self) -> int:
        return self.rect.centerx
    @centerx.setter
    def centerx(self,centerx) -> None:
        self.pos = (self.pos.x + (centerx - self.rect.centerx),self.pos.y)
    @property
    def centery(self) -> int:
        return self.rect.centery
    @centery.setter
    def centery(self,centery) -> None:
        self.pos = (self.pos.x, self.pos.y + (centery - self.rect.centery))

    @property
    def collide_rect(self) -> str:
        return self.rect_border
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect_border.colliderect(rect)
    def collide_all(self, lista: list[Self]) -> str:
        lista = []
        for i,x in enumerate(lista):
            if x.collide(self.collide_rect):
                lista.append(i)
        return lista
    def get_update_rects(self):
        if self.redraw < 1:
            return []
        elif self.redraw < 2:
            return [self.rect_border]
        else:
            return [self.rect_border,self.last_rect]
    
    def is_hover(self,pos) -> bool:
        return self.rect_border.collidepoint(pos)

    def copy(self):
        return self
