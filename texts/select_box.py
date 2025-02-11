import pygame as pag
import math
from typing import Callable, Literal

from pygame import Vector2
from .boton import Text
from .boton import Button
from Utilidades_pygame.Animaciones import Curva_de_Bezier
        
class Select_box:
    def __init__(
            self, boton: Button, options: list[str], *, auto_open: bool=False, min_width = 10, min_height = 30, func: Callable=None, text_size: int = 16, position: Literal["top","bottom","right","left"] = 'bottom', animation_dir: Literal['vertical', 'horizontal']='vertical', font: str|None =None, padding_horizontal= 5, **kwargs):
        
        self.__options = options
        self.select_opened = False
        self.auto_open = auto_open
        self.func = func
        self.boton = boton
        self.in_animation = False
        self.botones = []
        self.selected_animation = animation_dir
        self.position = position
        self.redraw = 2
        self.padding_horizontal = padding_horizontal
        self.last_rect = pag.Rect(0,0,0,0)
        self.font = font
        self.border_radius = 5
        self.text_size = text_size
        self.min_width = min_width
        self.min_height = min_height
        self.hover_rect = pag.Rect(0,0,0,0)
        self.mouse_pos = pag.Vector2(0,0)
        self.use_mouse_motion = False

        self.animation_open = Curva_de_Bezier        

        self.dict_animations = {
            'open': "Curva_de_Bezier(20, [(self.rect.w,self.rect.h), (self.size[0]*1.5,self.size[1]*1.5),(self.size[0],self.size[1])])",
            'close': "Curva_de_Bezier(10, [\
                (self.rect.w,self.rect.h), \
                (self.rect.w,0) if self.selected_animation == 'vertical' else (0,self.rect.h)\
            ])"
        }

        self.__generate()
    
    def __generate(self):
        self.botones.clear()
        self.txt_tama_h = Button(f'{max([f'{x}' for x in self.options])}',self.text_size,self.font,(0,280), 6, 'topleft','white', (20,20,20), 'darkgrey', 0, 0, border_width=1, border_color='white').rect.h
        self.hover_rect.h = self.txt_tama_h

        t_max_l = [self.min_width]

        for i, op in enumerate(self.options):
            t = Text(f'{op}',self.text_size,None,(self.padding_horizontal,self.txt_tama_h*i +5), 'topleft','black', with_rect=False, padding=(0,5))
            t_max_l.append(t.width + self.padding_horizontal*2)
            self.botones.append(t.copy())

        self.size = (max(t_max_l),max(self.min_height,(self.txt_tama_h*len(self.options))+10))
        self.hover_rect.w = self.size[0]

        self.surf = pag.Surface(self.size,pag.SRCALPHA)
        self.rect = self.surf.get_rect()
        self.surf.fill((0,0,0,0))

        for x in self.botones:
            x.centerx = self.rect.w//2
        if self.selected_animation == 'vertical':
            self.rect.h = 0
        elif self.selected_animation == 'horizontal':
            self.rect.w = 0
        self.rect.topleft = self.boton.bottomleft

    def open_it(self) -> None:
        self.select_opened = True
        self.in_animation = True
        self.animation_open = eval(self.dict_animations['open'])
    
    def close_it(self) -> None:
        self.select_opened = False
        self.in_animation = True
        self.animation_open = eval(self.dict_animations['close'])

    def click(self, mouse_pos) -> bool:
        if self.boton.hover and not self.select_opened and not self.auto_open:
            self.open_it()
            return True
        if (self.boton.hover and self.select_opened and not self.auto_open) or (not self.rect.collidepoint(mouse_pos) and self.auto_open):
            self.close_it()
            return False
        if not self.rect.collidepoint(mouse_pos):
            self.close_it()
            return False
        new_pos = Vector2(mouse_pos)-self.rect.topleft
        final_index = math.floor((new_pos.y/self.size[1])*len(self.botones))

        self.func({'index': final_index, 'text': self.botones[final_index].text})
        self.close_it()
        return True

    def update(self, dt=1, **kwargs) -> None:
        if self.in_animation:
            self.redraw += 2
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

    def update_hover(self, mouse_pos=(-10000,-10000)):
        self.boton.update_hover(mouse_pos)
        if self.auto_open and self.boton.is_hover(mouse_pos) and not self.select_opened:
             self.open_it()
        elif self.auto_open and not self.boton.is_hover(mouse_pos) and not self.rect.collidepoint(mouse_pos) and self.select_opened:
             self.close_it()

        for btn in self.botones:
            btn.update()

        if self.mouse_pos != Vector2(mouse_pos)-self.rect.topleft:
            if self.rect.collidepoint(mouse_pos):
                self.mouse_pos = Vector2(mouse_pos)-self.rect.topleft
                self.hover_rect.top = self.txt_tama_h*math.floor((self.mouse_pos.y/self.size[1])*len(self.botones)) + 5
                self.redraw += 1
            else:
                if self.hover_rect != -1:
                    self.redraw += 1

                self.hover_rect.top = -1
                

    def draw(self, surface: pag.Surface, always_draw = False) -> None:
        pag.draw.rect(self.surf, (240,240,240), [0,0,*self.rect.size], 0)
        
        if always_draw:
            self.redraw += 1

        if self.redraw < 1:
            return []
        
        if self.hover_rect.top >= 0:
            pag.draw.rect(self.surf, 'darkgrey', self.hover_rect, 0, self.border_radius)
            if self.redraw < 1:
                self.redraw += 1
        for btn in self.botones:
            btn.redraw += 2
            btn.draw(self.surf)
        
        surface.blit(self.surf, self.rect.topleft,[0,0,self.rect.w,self.rect.h])
        
        if self.redraw < 2:
            self.redraw = 0
            return [self.rect]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect.copy()).copy()
            self.last_rect = self.rect.copy()
            return [self.rect, r]
    @property
    def collide_rect(self) -> str:
        return self.rect.union(self.last_rect)
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect.copy().union(self.last_rect.copy()).colliderect(rect)
    def collide_all(self, lista: list):
        lista = []
        for x in lista:
            if x.collide(self.collide_rect):
                lista.append(x.collide_rect)
        return lista
    
    def is_hover(self,pos) -> bool:
        return self.rect.collidepoint(pos)
    
    @property
    def options(self):
        return self.__options
    
    @options.setter
    def options(self, options):
        self.__options = options
        self.__generate()