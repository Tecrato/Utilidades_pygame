import pygame as pag
import math

from pygame import Vector2
from ..texts import Button, Text

from .base import Base

class simple_popup(Base):
    def __init__(self, pos, dir = 'center', title= 'Titulo', text= 'Texto aqui', size= (200,80), border_radius=10, inside_limits=True) -> None:

        super().__init__(pos,dir, size, border_radius, inside_limits)

        Text(title, 16, None, (0,0), 'topleft', 'black', padding=10).draw(self.surf)
        Text(text, 16, None, (10,30), 'topleft', 'black', padding=1).draw(self.surf)

        self.botones.append({
            'btn':Button('Aceptar',16,None,self.rect.bottomright, (10,5), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'exit'
            })
        
class desicion_popup(Base):
    def __init__(self, pos, title= 'Titulo', text= 'Texto aqui', size= (200,80),accept_boton_text= 'aceptar', dir = 'center', border_radius=10, inside_limits=True) -> None:

        super().__init__(pos,dir, size, border_radius, inside_limits)

        Text(title, 16, None, (0,0), 'topleft', 'black', padding=10).draw(self.surf)
        Text(text, 16, None, (10,30), 'topleft', 'black', padding=1).draw(self.surf)

        
        self.botones.append({
            'btn':Button('Cancelar',16,None,self.rect.bottomright, (10,5), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'exit'
            })
        self.botones.append({
            'btn':Button(accept_boton_text,16,None,(self.botones[1]['btn'].rect.left - 10,self.rect.bottom), (10,5), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'aceptar'
            })

class select(Base):
    """
    La clase select que sirve esencialmente para cuando se quiere tener opciones al hacer click derecho,
    las funcion asignada constara de los siguientes parametros:
     - En caso de obtener un resultado de click:
        - index: int
        - text: str
        - obj: objeto
     - En caso de que el usuario no haga click o no haya seleccionado ninguna opcion:
        - exit
    """
    def __init__(self, pos, options:list, dir = 'topleft', captured = None,min_width =0, border_radius=10, inside_limits=True, volatile=True) -> None:
        super().__init__(pos,dir, border_radius=border_radius, inside_limits=inside_limits)
        self.texts = options
        self.captured = captured
        self.opciones: list[Text] = []
        self.volatile = volatile
        self.new_pos_selection = -1

        self.txt_tama_h = Button(f'{max([f'{x}' for x in options])}',16,None,(0,280), 5, 'topleft','white', (20,20,20), 'darkgrey', 0, 0, border_width=-1, border_color='white').rect_border.h
        self.txt_tama_w = min_width
        
        for i, op in enumerate(options):
            t = Text(f'{op}',16,None,(10,self.txt_tama_h*i +5), 'topleft','black', padding= (0,5))
            self.txt_tama_w = max(self.txt_tama_w,t.width + 20)
            self.opciones.append(t.copy())

        self.size = (self.txt_tama_w,(self.txt_tama_h*len(options))+10)
        self.border_radius = 5

        self.surf = pag.Surface(self.size,pag.SRCALPHA)
        self.rect = self.surf.get_rect()

    def draw(self,surface):
        if self.redraw < 1:
            return []
        self.redraw = 0
        pag.draw.rect(self.surf, (240,240,240), [0,0,*self.size], 0, self.border_radius)
        if self.new_pos_selection > -1 and self.new_pos_selection < len(self.texts):
            pag.draw.rect(self.surf, 'darkgrey', [0,self.txt_tama_h*self.new_pos_selection + 5,self.size[0],self.txt_tama_h], 0, self.border_radius)
        for btn in self.opciones:
            btn.redraw = 1
            btn.draw(self.surf)
        pag.draw.rect(self.surf, 'black', [0,0,*self.size], 1, self.border_radius)
        surface.blit(self.surf,self.rect)
        return self.rect

    def click(self, pos = (-10000,-10000), *args, **kwargs):
        if self.new_pos_selection > -1 and self.new_pos_selection < len(self.texts):
            return {'index': self.new_pos_selection, 'text': self.opciones[self.new_pos_selection].text, 'obj':self.captured}
        elif self.volatile:
            return 'exit'
        return False
    
    def set_new_pos_selection(self, mouse_pos):
        new_pos = Vector2(mouse_pos)-self.rect.topleft-(0,5)
        self.new_pos_selection = math.floor((new_pos.y/(self.size[1]-10))*len(self.texts))

    def update(self, dt=1, mouse_pos=(-10000,-10000), **kwargs) -> None:
        if self.rect.collidepoint(mouse_pos):
            self.set_new_pos_selection(mouse_pos)
            self.redraw += 2
        else:
            self.new_pos_selection = -100000
            self.redraw += 2
        super().update(dt=dt, mouse_pos=mouse_pos)

