import pygame as pag
import math
from typing import Callable, Literal

from .boton import Text
from .boton import Button
from Utilidades_pygame.Animaciones import Curva_de_Bezier, Vector2
        
class Select_box:
    def __init__(
            self, boton: Button, options: list, *, auto_open: bool=False, min_width = 30, func: Callable=None, position: Literal["top","bottom","right","left"] = 'bottom', animation_dir: Literal['vertical', 'horizontal']='vertical', **kwargs):
        
        self.options = options
        self.select_opened = False
        self.auto_open = auto_open
        self.func = func
        self.boton = boton
        self.in_animation = False
        self.botones = []
        self.selected_animation = animation_dir
        self.position = position
        self.redraw = 2
        self.last_rect = pag.Rect(0,0,0,0)

        
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
        if self.selected_animation == 'vertical':
            self.rect.h = 0
        elif self.selected_animation == 'horizontal':
            self.rect.w = 0
        self.rect.topleft = self.boton.bottomleft
        self.animation_open = Curva_de_Bezier

        self.dict_animations = {
            'open': "Curva_de_Bezier(20, [(self.rect.w,self.rect.h), (self.size[0]*1.5,self.size[1]*1.5),(self.size[0],self.size[1])])",
            'close': "Curva_de_Bezier(20, [(self.rect.w,self.rect.h), (self.rect.w,self.rect.h*-.5) if self.selected_animation == 'vertical' else (self.rect.w*-.5,self.rect.h), (self.rect.w,0) if self.selected_animation == 'vertical' else (0,self.rect.h)])"
        }

    def open_it(self) -> None:
        self.select_opened = True
        self.in_animation = True
        self.animation_open = eval(self.dict_animations['open'])
    
    def close_it(self) -> None:
        self.select_opened = False
        self.in_animation = True
        self.animation_open = eval(self.dict_animations['close'])

    def click(self, mouse_pos) -> bool:
        if self.boton.click(mouse_pos) and not self.select_opened and not self.auto_open:
            self.open_it()
            return True
        if (self.boton.click(mouse_pos) and self.select_opened and not self.auto_open) or (not self.rect.collidepoint(mouse_pos) and self.auto_open):
            self.close_it()
            return True
        if not self.rect.collidepoint(mouse_pos):
            self.close_it()
            return False
        new_pos = Vector2(mouse_pos)-self.rect.topleft
        final_index = math.floor((new_pos.y/self.size[1])*len(self.botones))

        self.func({'index': final_index, 'text': self.botones[final_index].text})
        self.close_it()
        return True

    def update(self, dt=1, mouse_pos=(-10000,-10000)) -> None:
        self.boton.update(dt)

        if self.auto_open and self.boton.is_hover(mouse_pos) and not self.select_opened:
             self.open_it()
        elif self.auto_open and not self.boton.is_hover(mouse_pos) and not self.rect.collidepoint(mouse_pos) and self.select_opened:
             self.close_it()
        
        if self.in_animation:
            self.redraw = 2
            self.last_rect = self.last_rect.union(self.rect.copy())
            r = self.animation_open.update()
            if r == True:
                self.in_animation = False
                if self.selected_animation == 'vertical' and not self.select_opened:
                    self.rect.size = (self.size[0],0)
                elif self.selected_animation == 'horizontal' and not self.select_opened:
                    self.rect.size = (0,self.size[1])
                return
            if r[0] > self.size[0]:
                r[0] = self.size[0]
            if r[1] > self.size[1]:
                r[1] = self.size[1]
            self.rect.size = r
            if self.position == 'top':
                self.rect.bottomleft = self.boton.rect_border.topleft
            elif self.position == 'bottom':
                self.rect.topleft = self.boton.rect_border.bottomleft
            elif self.position == 'right':
                self.rect.topleft = self.boton.rect_border.topright
            elif self.position == 'left':
                self.rect.topleft = self.boton.rect_border.bottomright

    def draw(self, surface: pag.Surface, mouse_pos) -> None:
        pag.draw.rect(self.surf, (240,240,240), [0,0,*self.rect.size], 0)
        if self.rect.collidepoint(mouse_pos):
            new_pos = Vector2(mouse_pos)-self.rect.topleft
            new_pos_selection = self.txt_tama_h*math.floor((new_pos.y/self.size[1])*len(self.botones)) + 5
            pag.draw.rect(self.surf, 'darkgrey', [0,new_pos_selection,self.size[0],self.txt_tama_h], 0, self.border_radius)
            if self.redraw < 1:
                self.redraw = 1
        for btn in self.botones:
            btn.redraw = 1
            btn.draw(self.surf)
        surface.blit(self.surf, self.rect.topleft,[0,0,self.rect.w,self.rect.h])
        
        if self.redraw < 1:
            return []
        if self.redraw < 2:
            self.redraw = 0
            return [self.rect]
        elif self.redraw < 3:
            self.redraw = 0
            r = self.last_rect.union(self.rect.copy()).copy()
            self.last_rect = self.rect.copy()
            return [self.rect, r]
    @property
    def collide_rect(self) -> str:
        return self.rect
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect.collidepoint(rect)
    def collide_all(self, lista: list):
        lista = []
        for x in lista:
            if x.collide(self.collide_rect):
                lista.append(x.collide_rect)
        return lista
    
    def is_hover(self,pos) -> bool:
        return self.rect_border.collidepoint(pos)