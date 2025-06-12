import pygame as pag
from..bloque import Bloque

"""
Van a ser bloques, y se colocaran en la lista de dibujado principal
asi que tendran una variable active, que lo muestre, tambien servira para que no ejecute los updates, y el draw.
Tambien tendra una animacion de apertura, de abajo hacia arriba, ademas, se pondra en practica la maquina de estados finitos. 
"""

class Base_win(Bloque):
    def __init__(self, centro, size:tuple[int,int]=(500,300), **kwargs) -> None:
        super().__init__(pos=centro, size=size, **kwargs)

        self.active: bool = False
        self.pressed_click: bool = False
        self.__use_mouse_wheel = True
    
    def func_cerrar(self):
        self.active = False
        return True

    def click(self, mouse_pos):
        if not self.active:
            return False
        r = super().click(mouse_pos)
        if not r and self.rect.collidepoint(mouse_pos):
            return True
        return r

    def draw_before(self):
        ...

    def draw_after(self):
        ...

    def draw(self, surface):
        if not self.active:
            return []
        self.redraw += 1
        return super().draw(surface)

    def update(self, pos=None, dt=1, **kwargs):
        if not self.active:
            return False
        super().update(pos=pos, dt=dt, **kwargs)
    def update_hover(self, mouse_pos=...):
        if not self.active:
            self.hover = False
            self.cursor = pag.SYSTEM_CURSOR_ARROW
            return False
        r = super().update_hover(mouse_pos)
        if not r and self.rect.collidepoint(mouse_pos):
            self.hover = True
            self.cursor = pag.SYSTEM_CURSOR_ARROW
            return True
        return False
    def on_wheel(self, delta=None, **kwargs):
        if not self.active:
            return False
        super().on_wheel(delta, **kwargs)


    @property
    def use_mouse_wheel(self):
        return self.__use_mouse_wheel if self.active else False
    @use_mouse_wheel.setter
    def use_mouse_wheel(self,use_mouse_wheel):
        self.__use_mouse_wheel = use_mouse_wheel
