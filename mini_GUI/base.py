import pygame as pag
from pygame import Vector2

from ..obj_Base import Base as primary_base
from ..texts import Button


class Base(primary_base):
    def __init__(self,pos,dir = 'center', size = (200,125), border_radius = 10, inside_limits=True) -> None:
        self.limits = pag.Rect(0,0,600,550)
        self.inside_limits = inside_limits
        super().__init__(pos,dir)

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

    def click(self,pos):
        for btn in self.botones:
            if btn['btn'].rect.collidepoint(Vector2(pos)-self.rect.topleft):
                return btn['result']

    def draw(self, surface,pos,update=True):
        for btn in self.botones:
            btn['btn'].draw(self.surf,Vector2(pos)-self.rect.topleft)
        surface.blit(self.surf,self.rect)
        if update:
            return self.rect