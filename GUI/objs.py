import pyperclip
from pygame.math import Vector2

from ..texts import Button, Text
from .base import Base_win


class Info(Base_win):
    def __init__(self,centro: tuple[int,int],encabezado: str,text: str|list[str],size=(500,300)):
        super().__init__(centro,encabezado,size)

        Text(text,25,None,(30,size[1]/2.3),'left', 'black', padding=20).draw(self.surface)

        self.botones.append({
            'btn':Button('Aceptar',30,None,Vector2(size)-(20,20), 20, 'bottomright','black','white', border_width=-1),
            'return':'aceptar',
            'result': lambda: True
            })
        
class Desicion(Base_win):
    def __init__(self,centro: tuple[int,int],encabezado: str,text: str|list[str], size=(500,300)):
        super().__init__(centro,encabezado,size)

        Text(text,25,None,(30,size[1]/2.3),'left', 'black', padding=20).draw(self.surface)

        self.botones.append({
            'btn':Button('Cancelar',24,None,Vector2(size)-(20,20), 15, 'bottomright','black','white', border_width=-1),
            'return':'cancelar',
            'result': lambda: 'cancelar'
            })
        self.botones.append({
            'btn':Button('Aceptar',24,None,(Vector2(size)-(20,20))-(self.botones[1]['btn'].rect.w+20,0), 15, 'bottomright','black','white', border_width=-1),
            'return':'aceptar',
            'result': lambda: 'aceptar'
            })


        