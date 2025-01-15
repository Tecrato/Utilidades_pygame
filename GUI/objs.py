import pyperclip
from pygame.math import Vector2

from ..texts import Button, Text, Input
from .base import Base_win

configs = {}

class Info(Base_win):
    def __init__(self,centro: tuple[int,int],encabezado: str,text: str|list[str],size=(500,300)):
        super().__init__(centro,encabezado,size)

        Text(text,25,None,(30,size[1]/2.3),'left', 'black').draw(self.surface)

        self.botones.append({
            'btn':Button('Aceptar',30,None,Vector2(size)-(20,20), 20, 'bottomright','black','white', border_width=-1),
            'return':'aceptar',
            'result': lambda: True
            })
        
class Desicion(Base_win):
    def __init__(self,centro: tuple[int,int],encabezado: str,text: str|list[str], size=(500,300)):
        super().__init__(centro,encabezado,size)

        Text(text,25,None,(30,size[1]/2.3),'left', 'black').draw(self.surface)

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

class Text_return(Base_win):
    def __init__(self, centro, encabezado, texto, large=False, size = (500,300)) -> None:
        super().__init__(centro, encabezado, size)
        try:
            configs['fuente_simbolos']
        except Exception as err:
            raise Exception('Debes incluir la siguiente linea de codigo: Utilidades.GUI.configs[\'fuente_simbolos\'] = "tu path hasta la fuente de symbols"')
        
        Text(texto,30,None,(250,50),'center', 'black').draw(self.surface)
        if large:
            self.input = Input((50,150), 20, None, width=375, height=40, border_top_left_radius=20, border_bottom_left_radius=20, max_letter=400)
        else:
            self.input = Input((size[0]-(150*2.25),150), 20, None, width=150, height=40, border_top_left_radius=20, border_bottom_left_radius=20, max_letter=40)

        self.input.draw(self.surface)

        self.botones.append({
            'btn':Button('Cancelar',30,None,Vector2(size)-(20,20), 20, 'bottomright','black','white', border_width=-1),
            'return':'cancelar',
            'result': lambda:'cancelar'
        })
        self.botones.append({
            'btn':Button('Aceptar',30,None,(Vector2(size)-(20,20))-(self.botones[1]['btn'].rect.w+20,0), 20, 'bottomright','black','white', border_width=-1),
            'return':'aceptar',
            'result': lambda: self.input.get_text()
            })
        self.botones.append({
            'btn':Button('',25,configs['fuente_simbolos'],self.input.topright, (20,7), 'topleft','black','white', border_width=1, border_radius=0, border_top_right_radius=20, border_bottom_right_radius=20),
            'return':'function',
            'result': lambda: self.input.set(pyperclip.paste())
        })
        self.inputs.append(self.input)
        
    def draw(self,surface) -> None:
        self.input.draw(self.surface)
        super().draw(surface)
    
    def update(self,eventos, mouse_pos=(-10000,-100000), **kwargs) -> None:
        for inp in self.inputs:
            inp.eventos_teclado(eventos)

        