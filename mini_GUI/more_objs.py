import pygame as pag

from pygame import Vector2
from ..texts import Button, Text

from .base import Base

class aviso1(Base):
    def __init__(self, pos, dire, text: str, font=None, size=(200,50)) -> None:
        txt = Text(text, 16, font, (20,size[1]//2-10), 'topleft', 'black', padding=1)
        super().__init__(pos, dire, (max(txt.width + 40,size[0]), size[1]), 20, inside_limits=True)
        self.text: str = text

        self.botones.clear()

        pag.draw.rect(self.surf, 'lightgrey', self.rect, 0, 20)
        pag.draw.rect(self.surf, 'black', self.rect, 1, 20)

        txt.draw(self.surf)

    def click(self,pos):
        if self.rect.collidepoint(Vector2(pos)):
            return 'exit'
    
    @property
    def width(self):
        return self.size[0]