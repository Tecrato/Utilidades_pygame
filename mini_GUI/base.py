import pygame as pag
from pygame import Vector2

from ..obj_Base import Base as primary_base
from ..texts import Button


class Base(primary_base):
    def __init__(self,pos,dir = 'center', size = (200,125), border_radius = 10, inside_limits=True,border_width = 3) -> None:
        self.limits = pag.Rect(0,0,600,550)
        self.inside_limits = inside_limits
        self.size = size
        super().__init__(pos,dir)

        self.border_width = border_width
        self.border_radius = border_radius

        self.botones = [{
            'btn':Button('X',24,None,(size[0],0),10,'topright', 'black', color_rect='lightgrey', color_rect_active='darkgrey', border_radius=0, border_top_right_radius=border_radius, border_width=-1),
            'result': 'exit',
            }]


        self.surf = pag.Surface(size,pag.SRCALPHA)
        self.rect = self.surf.get_rect()

        pag.draw.rect(self.surf, (240,240,240), [0,0,*size], 0, border_radius)
        pag.draw.rect(self.surf, 'lightgrey', [0,0,size[0],26], 0, border_top_left_radius=border_radius, border_top_right_radius=border_radius)


    def direccion(self, rect) -> None:
        rect.center = self.pos
        primary_base.direccion(self,rect)
        if not self.inside_limits:
            return
        if rect.right > self.limits.right:
            rect.right = self.limits.right
        elif rect.left < self.limits.left:
            rect.left = self.limits.left
        if rect.bottom > self.limits.bottom:
            rect.bottom = self.limits.bottom
        elif rect.top < self.limits.top:
            rect.top = self.limits.top
        self.create_border(self.rect, self.border_width)

    def click(self,pos):
        for btn in self.botones:
            if btn['btn'].rect.collidepoint(Vector2(pos)-self.rect.topleft):
                return btn['result']

    def draw(self, surface) -> pag.Rect:
        pag.draw.rect(surface, (0,0,0), self.rect_border, self.border_width, self.border_radius)
        for x in self.botones:
            x['btn'].draw(self.surf)
        surface.blit(self.surf,self.rect)
        return self.rect_border
    def update(self, pos=None, dt=1, **kwargs):
        for btn in self.botones:
            btn['btn'].update()
        return super().update(pos=pos, dt=dt, **kwargs)
    def update_hover(self, mouse_pos=(-1000,-10000)):
        for btn in self.botones:
            btn['btn'].update_hover(mouse_pos=Vector2(mouse_pos)-self.rect.topleft)