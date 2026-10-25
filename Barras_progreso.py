from typing import Tuple, Literal
from .Animaciones import Second_Order_Dynamics
import pygame as pag
import time
from .constants import DELAY_PRESSING, VERTICAL, HORIZONTAL

class Barra_de_progreso:
    def __init__(
            self, pos: Tuple[int,int], size: int|tuple[int,int], orientacion: VERTICAL|HORIZONTAL = 'vertical',
            border_color: tuple[int,int,int] = (0,128,255), fill_color: tuple[int,int,int] = (0,255,0), border_width: int = 2,
            smooth = False, func_on_change = None, highlight_color = "cyan"
            ):
        self.__size = pag.Vector2(size)
        self.__pos = pag.Vector2(pos)
        self.__orientacion = orientacion
        self.border_color = border_color
        self.default_border_color = border_color
        self.highlight_color = highlight_color
        self.fill_color = fill_color
        self.border_width = border_width
        self.rect = pag.rect.Rect(0, 0, *self.__size)
        self.rect2 = pag.rect.Rect(0, 0, *self.__size)
        self.__volumen = 1.0
        self.redraw = 2
        self.smooth = smooth
        self.smooth_movent = Second_Order_Dynamics(1.5, 1, 1.5, (0,0))
        self.use_mouse_motion = False
        self.keys_to_use = (pag.K_UP, pag.K_DOWN)  if self.__orientacion == "vertical" else (pag.K_RIGHT, pag.K_LEFT)
        self.keys_using: Tuple = tuple()
        self.last_press = 0
        self.volumen_change_direction = 1 
        self.pressing = False

        self.default_controles_adyacentes = {'up': None, 'right': None, 'down': None, 'left': None}
        self.controles_adyacentes = {'up': None, 'right': None, 'down': None, 'left': None}

        self.visible = True
        self.__hover = False
        self.func = func_on_change

        if self.__orientacion == 'vertical':
            self.rect.bottomleft = self.__pos
            self.rect2.bottomleft = self.__pos
        elif self.__orientacion == 'horizontal':
            self.rect.topleft = self.__pos
            self.rect2.topleft = self.__pos

    def pulsando(self) -> None:
        m_x, m_y = pag.mouse.get_pos()
        if self.__orientacion == 'vertical':
            if self.rect2.bottom - m_y > self.__size.y:
                self.rect.height = self.__size.y
            elif self.rect2.bottom - m_y < 0:
                self.rect.height = 0
            else:
                self.rect.height = self.rect2.bottom - m_y
            self.rect.bottom = self.pos[1]
            new_vol = float(self.rect.height / self.__size.y)
        elif self.__orientacion == 'horizontal':
            if self.rect2.left + m_x > self.__size.x:
                self.rect.w = self.__size.x
            elif self.rect2.left + m_x < 0:
                self.rect.w = 0
            else:
                self.rect.w = self.rect2.left + m_x
            new_vol = float(self.rect.w / self.__size.x)
        if new_vol != self.volumen:
            self.volumen = new_vol
            self.func_on_change()
        

    def draw(self,surface, *, always_draw=False, **kwargs) -> None:
        if not self.visible:
            return ()
        if always_draw:
            self.redraw = 2
        pag.draw.rect(surface, self.fill_color, self.rect)
        pag.draw.rect(surface, self.border_color, self.rect2, width=self.border_width)
        return (self.rect2,)

    def update(self, dt=1, **kwargs):
        self.redraw = 2
        if self.pressing and time.time() - self.last_press >  DELAY_PRESSING:
            self.volumen += dt * self.volumen_change_direction
        if self.smooth:
            v = self.smooth_movent.update(self.__volumen, dt=dt)[0]
        else:
            v = self.__volumen
        if self.__orientacion == 'vertical':
            self.rect.height = self.__size.y*v
            self.rect.bottom = self.pos[1]
        elif self.__orientacion == 'horizontal':
            self.rect.w = self.__size.x*v
        pass

    def click(self, mouse_pos) -> None:
        if not self.visible:
            return False
        if self.rect2.collidepoint(mouse_pos):
            self.use_mouse_motion = True
            self.pulsando()
            return True
    def on_mouse_motion(self, event: pag.event.Event) -> None:
        self.pulsando()

    def func_on_change(self) -> None:
        if self.func:
            self.func(self.volumen)

    def update_hover(self, mouse_pos) -> bool:
        if self.rect2.collidepoint(mouse_pos):
            self.hover = True
            return True
        else:
            self.hover = False
            return False

    @property
    def hover(self):
        return self.__hover
    @hover.setter
    def hover(self, val: bool):
        self.__hover:bool = bool(val)

        if self.__hover:
            self.keys_using = self.keys_to_use
            self.border_color = self.highlight_color
        else:
            self.keys_using = tuple()
            self.border_color = self.default_border_color

    def is_hover(self, pos) -> bool:
        return self.rect2.collidepoint(pos)

    def on_key_down(self, key):
        if key == self.keys_to_use[0]:
            self.volumen += .05
            self.volumen_change_direction = 1
        elif key == self.keys_to_use[1]:
            self.volumen -= .05
            self.volumen_change_direction = -1
        self.last_press = time.time()
        self.pressing = True
        self.func_on_change()
        return True
    def on_key_up(self, key):
        if key == self.keys_to_use[0] and self.volumen_change_direction == 1:
            self.pressing = False
        elif key == self.keys_to_use[1] and self.volumen_change_direction == -1:
            self.pressing = False
        else:
            return False
        return True


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
        if self.__orientacion == 'vertical':
            self.rect.bottomleft = self.__pos
            self.rect2.bottomleft = self.__pos
        elif self.__orientacion == 'horizontal':
            self.rect.topleft = self.__pos
            self.rect2.topleft = self.__pos

    @property
    def center(self):
        return self.rect.center
    @property
    def orientacion(self):
        return  self.__orientacion

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
    
    def __str__(self) -> str:
        return f"Barra de progreso({id(self)}):  {self.pos=}, {self.volumen}"