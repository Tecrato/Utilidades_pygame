import pygame as pag
from typing import Literal, Callable
from .text import Text
from .input import Input
from ..constants import ALING_DIRECTION


class Button(Text):
    '''
    ### More options
     - sound_to_hover: pag.Sound
     - sound_to_click: pag.Sound
     - toggle_rect: bool
     - color_active: pygame.Color
     - color_rect_active: pygame.Color
     - color_border_active: pygame.Color
     - func_to_hover: Callable
     - func_out_hover: Callable

    '''
    def __init__(self, text, size: int, font: str|None, pos: tuple|pag.Vector2 = (0,0), padding: int|list|tuple = 20,
        dire: ALING_DIRECTION = 'center', color = 'black', color_rect = 'darkgrey',
        color_rect_active='lightgrey',rect_width=0,border_radius:int=15,border_top_left_radius:int=-1,
        border_top_right_radius: int = -1, border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1, border_width = 2, border_color = 'black', with_rect = True,
        func:None|Callable = None, max_width = 0, min_width = 0, min_height = 0, wrap=True,
        cursor: int|None = None, text_align: ALING_DIRECTION = 'center', func_to_hover= None, func_out_hover= None,
        **kwargs) -> None:

        self.__hover = False
        self.color_rect_active = color_rect_active if color_rect_active != None else color_rect
        self.color_rect_inactive = color_rect
        self.color_inactive = color
        self.with_rect2 = with_rect
        self.scroll = False

        self.toggle_rect = kwargs.get('toggle_rect',False)
        self.border_color_inactive = border_color
        self.color_border_active = kwargs.get('color_border_active',border_color)

        self.color_active = kwargs.get('color_active',None)
        self.func = func
        self.func_to_hover = func_to_hover
        self.func_out_hover = func_out_hover
    
        self.sound_to_hover = kwargs.get('sound_to_hover',False)
        self.sound_to_click = kwargs.get('sound_to_click',False)

        self.controles_adyacentes: dict[Literal['up','right','down','left'], Button|Input|None] = {}

        Text.__init__(self,text, size, font, pos, dire, color, with_rect, color_rect, padding=padding, 
                             rect_width=rect_width, border_radius=border_radius,border_top_left_radius=border_top_left_radius, 
                             border_top_right_radius=border_top_right_radius, border_bottom_left_radius=border_bottom_left_radius, 
                             border_bottom_right_radius=border_bottom_right_radius, border_width=border_width,border_color=border_color,
                             max_width = max_width, min_width = min_width, min_height = min_height, wrap=wrap, **kwargs)
        if self.toggle_rect:
            self.with_rect = False
        self.cursor = cursor if cursor != None else pag.SYSTEM_CURSOR_HAND

    def update_hover(self,mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.hover = True
        else:
            self.hover = False
        return self.hover

    @property
    def hover(self):
        return self.__hover
    
    @hover.setter
    def hover(self, value: bool):
        if self.__hover and not bool(value):
            if self.func_out_hover:
                self.func_out_hover()
            self.__hover = False
            self.color_rect = self.color_rect_inactive
            self.color = self.color_inactive
            self.border_color = self.border_color_inactive
            if self.toggle_rect and self.with_rect2:
                self.with_rect = False
            if self.redraw < 1:
                self.redraw = 1
        elif not self.__hover and bool(value):
            if self.sound_to_hover:
                self.sound_to_hover.play()
            if self.func_to_hover:
                self.func_to_hover()
            self.__hover = True
            self.color_rect = self.color_rect_active
            self.color = self.color_active if self.color_active else self.color_inactive
            self.border_color = self.color_border_active
            if self.toggle_rect and self.with_rect2:
                self.with_rect = True
            if self.redraw < 1:
                self.redraw = 1

    def click(self, *args, **kwargs) -> bool:
        if not self.hover:
            return False
        if self.sound_to_click:
            self.sound_to_click.play()
        if self.func:
            return self.func()
        return True
    def change_color_ad(self,color,color_active = None) -> None:
        self.color_inactive = color
        self.color_active = color_active if color_active != None else self.color_active
        if self.hover and self.color_active:
            self.color = self.color_active
        else:
            self.color = self.color_inactive
        if self.redraw < 1:
            self.redraw += 1
    def change_color_rect_ad(self,color_inactive,color_active = None) -> None:
        self.color_rect_inactive = color_inactive if color_inactive != None else self.color_rect_inactive
        self.color_rect_active = color_active if color_active != None else self.color_rect_active
        if self.hover:
            self.color_rect = self.color_rect_active
        else:
            self.color_rect = self.color_rect_inactive
        if self.redraw < 1:
            self.redraw += 1


    def __str__(self) -> str:
        return 'Button: {} - pos: {}'.format(self.raw_text,self.pos)
    def __repr__(self) -> str:
        return self.__str__()