import pygame as pag
import math

from pygame import Vector2
from ..texts import Button, Text

from .base import Base

class simple_popup(Base):
    def __init__(self, pos, dir = 'center', title= 'Titulo', text= 'Texto aqui', size= (200,80), border_radius=10, inside_limits=True) -> None:

        super().__init__(pos,dir, size, border_radius, inside_limits)

        Text(title, 16, None, (0,0), 'topleft', 'black').draw(self.surf)
        Text(text, 16, None, (10,40), 'left', 'black').draw(self.surf)

        self.botones.append({
            'btn':Button('Aceptar',16,None,self.rect.bottomright, (20,15), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'exit'
            })
        
class desicion_popup(Base):
    def __init__(self, pos, title= 'Titulo', text= 'Texto aqui', size= (200,80),accept_boton_text= 'aceptar', dir = 'center', border_radius=10, inside_limits=True) -> None:

        super().__init__(pos,dir, size, border_radius, inside_limits)

        Text(title, 16, None, (0,0), 'topleft', 'black').draw(self.surf)
        Text(text, 16, None, (10,40), 'left', 'black').draw(self.surf)

        
        self.botones.append({
            'btn':Button('Cancelar',16,None,self.rect.bottomright, (20,15), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'exit'
            })
        self.botones.append({
            'btn':Button(accept_boton_text,16,None,(self.botones[1]['btn'].rect.left - 10,self.rect.bottom), (20,15), 'bottomright','black',(240,240,240), border_radius=10, border_bottom_right_radius=0, border_width=-1),
            'result': 'aceptar'
            })

class select(Base):
    def __init__(self, pos, options:list, dir = 'topleft', captured = None,min_width =0, border_radius=10, inside_limits=True, volatile=True) -> None:
        super().__init__(pos,dir, border_radius=border_radius, inside_limits=inside_limits)
        self.texts = options
        self.captured = captured
        self.botones: list[Text] = []
        self.volatile = volatile

        self.txt_tama_h = Button(f'{max([f'{x}' for x in options])}',16,None,(0,280), 6, 'topleft','white', (20,20,20), 'darkgrey', 0, 0, border_width=1, border_color='white').rect.h
        self.txt_tama_w = min_width
        
        for i, op in enumerate(options):
            t = Text(f'{op}',16,None,(10,self.txt_tama_h*i +5), 'topleft','black', padding= (0,5))
            self.txt_tama_w = max(self.txt_tama_w,t.width + 20)
            self.botones.append(t.copy())

        self.size = (self.txt_tama_w,(self.txt_tama_h*len(options))+10)
        self.border_radius = 5

        self.surf = pag.Surface(self.size,pag.SRCALPHA)
        self.rect = self.surf.get_rect()

    def draw(self,surface,pos):
        pag.draw.rect(self.surf, (240,240,240), [0,0,*self.size], 0, self.border_radius)
        if self.rect.collidepoint(pos):
            new_pos = Vector2(pos)-self.rect.topleft
            new_pos_selection = self.txt_tama_h*math.floor((new_pos.y/self.size[1])*len(self.texts)) + 5
            pag.draw.rect(self.surf, 'darkgrey', [0,new_pos_selection,self.size[0],self.txt_tama_h], 0, self.border_radius)
        for btn in self.botones:
            btn.draw(self.surf)
        pag.draw.rect(self.surf, 'black', [0,0,*self.size], 1, self.border_radius)
        surface.blit(self.surf,self.rect)
        return self.rect

    def click(self, pos):
        if self.rect.collidepoint(pos):
            new_pos = Vector2(pos)-self.rect.topleft
            final_index = math.floor((new_pos.y/self.size[1])*len(self.texts))
            return {'index': final_index, 'text': self.botones[final_index].text, 'obj':self.captured}
        elif self.volatile:
            return 'exit'
        return False
