import pygame as pag
import Utilidades_pygame as uti_pag
from typing import Iterable

from ..scroll import Screen_scroll
from ..texts import Button, Text
from .base import Base_win

class Classic_window(Base_win):
    def __init__(self,pos: tuple[int,int],header: str,body: str|list[str],size=(500,300), func = None, font=None, **kwargs):
        super().__init__(pos,size, background_color=(0,0,0,0), border_radius=20, border_width=2, **kwargs)

        self.func = func

        self.font = font
        self.title = Text(
            header, 30, self.font, (0,0), 'topleft', 'black', False, padding=(20,0),
            min_height=40
        )

        self.boton_x = Button(
            'X',25,self.font,(self.width,0),0,'topright', 'black', color_rect='lightgrey', 
            color_rect_active='darkgrey', border_radius=0, border_top_right_radius=20, 
            border_width=-1, min_height=40, min_width=40, func=self.func_cerrar
        )
        
        self.body = Text(
            body,25,self.font,(30,size[1]/2),'left', 'black', False, 'grey', padding=20, text_align='left', max_width=size[0]*.7
            )

        self.add(self.body,'(30,{}/2)'.format(self.size[1]), drawing=True)
        self.add(self.title,'(0,0)', drawing=True)
        self.add(self.boton_x, '(self.width,0)', drawing=True, clicking=True)


        self.scroll_class = Screen_scroll(self.rect.h-self.list_objs[0]['GUI'].height)
        self.scroll_class.pos = (self.rect.w,self.list_objs[0]['GUI'].height)

    def draw_before(self):
        pag.draw.rect(self.surf, (245,245,245), (0,0,*self.size), border_radius=20)
        pag.draw.rect(self.surf,'lightgrey',[0,0,self.size[0],40], border_top_left_radius=20, border_top_right_radius=20)
        ...
    def move_objs(self):
        for x in self.list_objs:
            x["GUI"].pos = pag.Vector2(eval(f"{x['pos']}"))+(0,self.scroll_class.diff)
        self.scroll_class.inside_height = max([eval(f"{x['pos']}")[1] for x in self.list_objs]) - self.list_objs[0]['GUI'].height - self.border_radius
        self.scroll_class.rodar(0)
        if self.redraw < 1:
            self.redraw = 1

class Info(Classic_window):
    def __init__(self,pos: tuple[int,int],encabezado: str,text: str|list[str],size=(500,300), func = None,font=None):
        super().__init__(pos,encabezado,text,size,func,font=font)

        self.btn_aceptar = Button('Aceptar',24,self.font,(0,0), 15, 'bottomright','black','white', border_width=-1, func=self.func_aceptar)

        self.add(self.btn_aceptar,(pag.Vector2(size)-(20,20)), clicking=True)

    def func_aceptar(self):
        if self.func:
            self.func('aceptar')
        self.active = False
        return True
        
class Desicion(Classic_window):
    def __init__(self,pos: tuple[int,int],encabezado: str,text: str|list[str], size=(500,300), font=None, func=None, options=None):
        super().__init__(pos,encabezado,text,size,func, font=font)

        # self.add(Button('Cancelar',24,self.font,pag.Vector2(size)-(20,20), 15, 'bottomright','black','white', border_width=-1 ,func=self.func_cancelar),(pag.Vector2(size)-(20,20)), clicking=True)
        # self.add(Button('Aceptar',24,self.font,(pag.Vector2(size)-(20,20))-(100+20,0), 15, 'bottomright','black','white', border_width=-1, func=self.func_aceptar),(pag.Vector2(size)-(20,20))-(100+20,0), clicking=True)

        self.__botons_pointer = -1
        self.options = ('aceptar', 'cancelar') if options is None else options
  
    @property
    def options(self):
        return self.__options
    @options.setter
    def options(self, value: list[str]):
        if not isinstance(value, Iterable) or not all(isinstance(i, str) for i in value):
            raise ValueError("options debe ser una lista de strings")
        if self.__botons_pointer >= 0:
            for x in reversed(range(self.__botons_pointer, self.__botons_pointer + len(self.__options))):
                self.list_objs.pop(x)
                
        self.__options = value
        last_g = len(self.list_objs)-1
        self.__botons_pointer = len(self.list_objs)
        
        for i, op in enumerate(self.options):
            # gui = uti_pag.Button(op, 20, self.font, (0,0), (15,15), 'bottomright','black','purple', color_rect_active='cyan', border_width=-1, border_radius=0, func=lambda n=i, op=op: self.execute_func('{}'.format(n), '{}'.format(op)))
            gui = uti_pag.Button(op, 20, self.font, (0,0), (15,15), 'bottomright', border_width=-1, func=lambda n=i, op=op: self.execute_func('{}'.format(n), '{}'.format(op)))
            pos = '({},{})'.format((self.list_objs[last_g]['GUI'].left-10) if i > 0 else (self.size[0]-20), self.size[1]-20)
            self.add(gui, pos, clicking=True)
            last_g += 1
        
    def execute_func(self, index:int ,text: str):
        if not self.active:
            return True
        self.active = False
        if self.func:
            self.func({'index':int(index), 'text':text})
        return True

    # def func_aceptar(self):
    #     if self.func:
    #         self.func('aceptar')
    #     self.active = False
    #     return True

    # def func_cancelar(self):
    #     if self.func:
    #         self.func('cancelar')
    #     self.active = False
    #     return True

        