import pygame as pag

from ..scroll import Screen_scroll
from ..texts import Button, Text
from .base import Base_win

class Classic_window(Base_win):
    def __init__(self,pos: tuple[int,int],header: str,body: str|list[str],size=(500,300), func = None, font=None, **kwargs):
        super().__init__(pos,size, background_color=(0,0,0,0), border_radius=20, border_width=2, **kwargs)

        self.func = func

        self.font = font
        self.header = Text(header, 30, self.font, (0,0), 'topleft', 'black', False, padding=20)
        self.boton_x = Button('X',28,self.font,(size[0],0),20,'topright', 'black', color_rect='lightgrey', color_rect_active='darkgrey', border_radius=0, border_top_right_radius=20, border_width=-1, func=self.func_cerrar)
        self.body = Text(body,25,self.font,(30,size[1]/2),'left', 'black', False, 'grey', padding=20)

        self.add(self.body,'(30,{}/2)'.format(self.size[1]), drawing=True)
        self.add(self.header,'(0,-self.scroll_class.diff)', drawing=True)
        self.add(self.boton_x, '(self.size[0],-self.scroll_class.diff)', drawing=True, clicking=True)


        self.scroll_class = Screen_scroll(self.rect.h-self.list_objs[0]['GUI'].height)
        self.scroll_class.pos = (self.rect.w,self.list_objs[0]['GUI'].height)

    def draw_before(self):
        pag.draw.rect(self.surf, (245,245,245), (0,0,*self.size), border_radius=20)
        pag.draw.rect(self.surf,'lightgrey',[0,0,self.size[0],40], border_top_left_radius=20, border_top_right_radius=20)
        ...
    def move_objs(self):
        for x in self.list_objs:
            x["GUI"].pos = pag.Vector2(eval(f"{x['pos']}"))+(0,self.scroll_class.diff)
        self.scroll_class.inside_height = max([eval(f"{x['pos']}")[1]+x["GUI"].height for x in self.list_objs]) - self.list_objs[0]['GUI'].height - self.border_radius
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
    def __init__(self,pos: tuple[int,int],encabezado: str,text: str|list[str], size=(500,300), font=None, func=None):
        super().__init__(pos,encabezado,text,size,func, font=font)

        self.add(Button('Cancelar',24,self.font,pag.Vector2(size)-(20,20), 15, 'bottomright','black','white', border_width=-1 ,func=self.func_cancelar),(pag.Vector2(size)-(20,20)), clicking=True)
        self.add(Button('Aceptar',24,self.font,(pag.Vector2(size)-(20,20))-(100+20,0), 15, 'bottomright','black','white', border_width=-1, func=self.func_aceptar),(pag.Vector2(size)-(20,20))-(100+20,0), clicking=True)

    def func_aceptar(self):
        if self.func:
            self.func('aceptar')
        self.active = False
        return True

    def func_cancelar(self):
        if self.func:
            self.func('cancelar')
        self.active = False
        return True

        