import pygame as pag

from pygame import Vector2
from ..texts import Button, Text

from .base import Base

class aviso1(Base):
    def __init__(self, pos, dire, text: str, font=None):
        super().__init__(pos, dire, (200,50), 20, inside_limits=True)
        self.text = text

        self.botones.clear()

        pag.draw.rect(self.surf, 'lightgrey', self.rect, 0, 20)
        pag.draw.rect(self.surf, 'black', self.rect, 1, 20)

        Text(self.text, 14, font, (20,25), 'left', 'black').draw(self.surf)

    def click(self,pos):
        if self.rect.collidepoint(Vector2(pos)):
            return 'exit'