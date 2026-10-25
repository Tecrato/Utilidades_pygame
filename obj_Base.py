from typing import Literal, Self
from copy import deepcopy
import pygame as pag

from .Animaciones import Curva_de_Bezier, Second_Order_Dynamics, Simple_acceleration
from Utilidades.maths import Hipotenusa

from pygame import Vector2

from .constants import ALIGN_DIRECTION

class Base:
    def __init__(self,pos: tuple|Vector2, dire: ALIGN_DIRECTION = 'center'):
        self.rect = pag.Rect(0,0,50,50)
        self.smoothmove_bool = False

        self.__dire: str = dire
        self.__pos = Vector2(pos)
        self.smoothmove_pos = Vector2(0)
        self.rect_border = pag.rect.Rect(0,0,0,0)
        self.redraw: int = 2
        self.last_rect = pag.Rect(0,0,0,0)
        self.mouse_pos = Vector2(0,0)
        self.hover = False
        self.use_mouse_motion = False
        self.smoothmove_type = None
        self.use_mouse_wheel = False
        self.cursor: int|None = pag.SYSTEM_CURSOR_ARROW
        self.__visible = True
        self.keys_using = tuple()

    def create_border(self, rect: pag.Rect, border_width: int) -> None:
        if border_width == -1:
            border_width = 0
        self.rect_border = pag.rect.Rect(0,0,rect.size[0] + border_width,rect.size[1] + border_width)
        self.rect_border.center = rect.center

    def direccion(self, rect) -> None:
        rect.center = self.__pos
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
            
    def smoothmove(self,f, z, r) -> Self:
        self.smoothmove_pos = self.pos
        self.movimiento = Second_Order_Dynamics(f, z, r, self.__pos)
        self.smoothmove_bool = True
        self.smoothmove_type = 'Second order dinamics'
        return self
    def Cubic_bezier_move(self, puntos, multiplicador:float = 1) -> Self:
        self.smoothmove_pos = self.pos
        self.smoothmove_bool = True
        self.smoothmove_type = 'Cubic Bezier'
        self.movimiento = Curva_de_Bezier(multiplicador,puntos)
        return self
    def simple_acceleration_move(self, vel,dir=[1,0],tipo: Literal['follow','forward']='follow') -> Self:
        self.smoothmove_pos = self.pos
        self.movimiento = Simple_acceleration(vel, dir, self.pos)
        self.smoothmove_bool = True
        self.smoothmove_type = 'Simple Acceleration'
        self.simplemove_type = tipo

        self.vel = float(vel)

        self.direccion(self.rect)
        return self

    def update(self,pos=None,dt=1, **kwargs) -> bool:
        if not self.smoothmove_bool and not pos:
            return False
        elif pos:
            self.pos = pos
            return True
        if self.__pos == self.smoothmove_pos:
            return False
        
        if self.smoothmove_type == 'Second order dinamics' and isinstance(self.movimiento, Second_Order_Dynamics):
            nueva = self.movimiento.update(self.smoothmove_pos, dt)
            # Si ya casi no se mueve, clávalo en el objetivo para que la animación acabe.
            if abs(sum(self.movimiento.yd)) < 0.01 and Hipotenusa(nueva, self.smoothmove_pos) < 0.5:
                nueva = Vector2(self.smoothmove_pos)
            self.__pos = Vector2(nueva)
        elif self.smoothmove_type == 'Simple Acceleration' and isinstance(self.movimiento, Simple_acceleration):
            if self.simplemove_type == 'follow':
                self.__pos = self.movimiento.follow(self.smoothmove_pos,dt=dt)
                self.redraw += 2
                if Hipotenusa(self.__pos,self.smoothmove_pos) < self.vel+1:
                    self.__pos = self.smoothmove_pos
            else:
                self.__pos = self.movimiento.update(dt)
        elif self.smoothmove_type == 'Cubic Bezier':
            r = self.movimiento.update(dt)

            if (r == True):
                self.smoothmove_bool = False
                self.smoothmove_type = None
            else:
                self.__pos = Vector2(r)
        
        self.direccion(self.rect)
        return True

    def update_hover(self, mouse_pos) -> bool:
        if self.rect.collidepoint(mouse_pos) and not self.hover:
            self.hover = True
        elif not self.rect.collidepoint(mouse_pos) and self.hover:
            self.hover = False
        return self.hover

    def move(self, pos) -> None:
        self.pos = pos

    def on_mouse_motion(self):
        return False
    def on_key_down(self, key: int) -> bool:
        return False
    def on_key_up(self, key: int) -> bool:
        return False
    def on_wheel(self, delta):
        return False

    @property
    def pos(self) -> Vector2:
        return self.__pos if not self.smoothmove_bool else self.smoothmove_pos
    @property
    def raw_pos(self) -> Vector2:
        return self.__pos
    @pos.setter
    def pos(self,pos:tuple[int|float,int|float]|Vector2):
        self.redraw += 1
        if self.smoothmove_bool:
            self.smoothmove_pos = Vector2(pos)
        else:
            self.last_rect = self.last_rect.copy().union(self.rect.copy())
            self.__pos: Vector2 = Vector2(pos)
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
        return self.rect.left
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
    def visible(self) -> bool:
        return self.__visible
    @visible.setter
    def visible(self,visible: bool):
        if self.__visible == visible:
            return
        self.__visible = visible
        self.redraw += 1

    @property
    def collide_rect(self) -> pag.Rect:
        return self.rect
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect.colliderect(rect) or self.last_rect.colliderect(rect)
    def collide_all(self, lista: list[Self]) -> list[pag.Rect]:
        lista_collide = []
        for i,x in enumerate(lista):
            if x.collide(self.collide_rect):
                lista_collide.append(i)
        return lista_collide
    def get_update_rects(self):
        if self.redraw < 1:
            return []
        elif self.redraw < 2:
            return [self.rect]
        else:
            return [self.rect,self.last_rect]
    
    def is_hover(self,pos) -> bool:
        return self.rect.collidepoint(pos)

    def copy(self) -> Self:
        """Copia independiente: rects, posiciones y animación no se comparten."""
        new_instance = self.__class__.__new__(self.__class__)
        new_instance.__dict__.update(self.__dict__)
        for attr in ('rect', 'rect_border', 'last_rect'):
            new_instance.__dict__[attr] = getattr(self, attr).copy()
        new_instance.__dict__['_Base__pos'] = Vector2(self._Base__pos)
        new_instance.__dict__['smoothmove_pos'] = Vector2(self.smoothmove_pos)
        movimiento = new_instance.__dict__.get('movimiento')
        if movimiento is not None:
            new_instance.__dict__['movimiento'] = deepcopy(movimiento)
        return new_instance
