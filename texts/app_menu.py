import pygame as pag
from .text import Text
from .boton import Button
from .select_box import Select_box

class App_menu:
    def __init__(self, width: int, *, height: int = 20, background='black', color_hover= 'darkgrey', botons_height=None, text_color = 'white', text_size = 16):
        self.width = width
        self.background = background
        self.botons_height = botons_height
        self.text_color = text_color
        self.text_size = text_size
        self.color_hover = color_hover

        self.option_height = Text('.|asd]¿!',16,None,padding=0).height
        self.height = max(height,self.option_height)

        self.rect = pag.Rect(0,0,width,self.height)

        self.options: list[Select_box] = []

    def add(self, text: str, options: list[str], func=None) -> None:
        if len(self.options) > 0:
            pos = (self.options[-1].boton.right,self.height/2)
        else:
            pos = (0,self.height/2)
        self.options.append(
            Select_box(
                Button(
                    text, 16, None, pos, self.text_size, 'left', self.text_color, color_rect=self.background, 
                    color_rect_active=self.color_hover,height=self.height if not self.botons_height else self.botons_height,
                    border_radius=0, border_width=-1
                ),
                options, auto_open=True, func=func
            )
        )
        
    def draw(self, surface, mouse_pos) -> None:
        pag.draw.rect(surface, self.background, self.rect)
        for i,x in sorted(enumerate(self.options),reverse=False):
            x.draw(surface, mouse_pos)
    
    def click(self, pos) -> bool:
        for i,x in sorted(enumerate(self.options),reverse=False):
            if x.click(pos):
                return True
        return False
    
    def update(self, dt=1, mouse_pos=(-10000,-10000)) -> None:
        for i,x in sorted(enumerate(self.options),reverse=False):
            x.update(dt, mouse_pos)