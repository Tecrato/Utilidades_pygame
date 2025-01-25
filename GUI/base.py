import pygame as pag

from ..texts import Button, Text, Input
from pygame.math import Vector2


class Base_win:
    def __init__(self, centro, title, size:tuple[int,int]=(500,300)) -> None:
        self.rect = pag.Rect(0,0,*size)
        self.rect.center = centro
        self.size = size


        self.surface: pag.Surface = pag.Surface(size)
        self.surface.fill((254,1,1))
        self.surface.set_colorkey((254,1,1))
        pag.draw.rect(self.surface,'white',[0,0,*size], border_radius=20)
        pag.draw.rect(self.surface,'lightgrey',[0,0,size[0],40], border_top_left_radius=20, border_top_right_radius=20)
        Text(title, 30, None, (0,0), 'topleft', 'black', False, padding=20).draw(self.surface)

        self.state: str = 'minimized' # minimized | maximized
        self.pressed_click: bool = False

        self.botones = [{
            'btn':Button('X',30,None,(size[0],0),20,'topright', 'black', color_rect='lightgrey', color_rect_active='darkgrey', border_radius=0, border_top_right_radius=20, border_width=-1),
            'return': 'destroy',
            'result': lambda:'',
            }]
        

    def draw(self, surface: pag.Surface) -> None|pag.Surface:
        [btn['btn'].draw(self.surface) for btn in self.botones]
        surface.blit(self.surface,self.rect)
        pag.draw.rect(surface,'black', self.rect,3, 20)
        return [self.rect]
        

    def click(self, pos):
        mx,my = Vector2(pos)-self.rect.topleft
        for btn in self.botones:
            if btn['btn'].rect.collidepoint((mx,my)):
                return btn
            
        if pag.Rect([0,0,500,40]).collidepoint((mx,my)):
            self.pressed_click = True

    def update(self,  **kwargs):
        [btn['btn'].update() for btn in self.botones]
    
    def update_hover(self, mouse_pos):
        mx,my = Vector2(mouse_pos)-self.rect.topleft
        for btn in self.botones:
            btn['btn'].update_hover((mx,my))

    def copy(self):
        return self