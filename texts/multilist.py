import pygame as pag
from pygame.math import Vector2
from ..obj_Base import Base
from .text import Text
from .list import List

class Multi_list(Base):
    '''
    ### More options
     - with_index
     - padding_top
     - padding_left
    
    ## Plantillas
    elif evento.type == MOUSEMOTION:
        for x in self.listas:
            if x.scroll:
                x.rodar(-evento.rel[1])
    '''
    def __init__(self, size:tuple,pos:tuple,num_lists:int=2,lista: list[list] = None, text_size: int = 20, separation: int = 0,
        background_color = 'black', selected_color = (100,100,100,100), text_color= 'white', colums_witdh= -1, header: bool =True,
        header_text: list = None, dire: str = 'topleft', fonts: list[str]|None = None, default: list[list]=None,
        smothscroll=False, **kwargs) -> None:
        
        super().__init__(pos,dire)
        self.size = Vector2(size)
        self.default = [None for _ in range(num_lists)] if not default else default
        self.lista_palabras = self.default if not lista else lista
        self.text_size = text_size
        self.separation = separation
        self.__smothscroll = smothscroll
        self.background_color = background_color
        self.selected_color = selected_color
        self.padding_top = kwargs.get('padding_top',10)
        self.padding_left = kwargs.get('padding_left',20)
        self.with_index = kwargs.get('with_index',False)
        self.text_color = text_color
        if num_lists <= 0: raise Exception('\n\nComo vas a hacer 0 listas en una multilista\nPensá bro...')
        self.num_list = num_lists
        self.colums_witdh = [((self.size.x/self.num_list)*x)/self.size.x for x in range(self.num_list)] if colums_witdh == -1 else list(colums_witdh)
        self.colums_witdh.append(1.0)
        self.header = header
        self.text_header = [None for x in range(num_lists)] if header_text == None else header_text
        self.fonts = [None for x in range(num_lists)] if fonts == None else fonts
        self.header_radius = kwargs.get('header_radius',0)
        self.border_color = kwargs.get('border_color', 'black')
        self.dire = dire

        self.listas: list[List] = []
        self.lineas = []
        self.scroll = False
        self.smothmove_bool = False
        self.actual_index = -1

        self.rect = pag.rect.Rect(pos[0], pos[1], size[0], size[1])
        self.direccion(self.rect)
        self.lista_surface= pag.surface.Surface(self.rect.size)
        self.lista_surface_rect = self.lista_surface.get_rect()
        self.lista_surface.fill((0,0,0))
        self.lista_surface.set_colorkey((0,0,0))
        self.lista_surface_rect.topleft = self.pos
        for x in range(num_lists):
            separar = Text('Hola|', self.text_size, self.fonts[-1], (0,0)).rect.h - Text('Hola|', self.text_size, self.fonts[0], (0,0)).rect.h

            l_size = ((self.size.x*self.colums_witdh[x+1]) - (self.size.x*self.colums_witdh[x]), self.size.y)
            l_pos = Vector2(self.size.x*self.colums_witdh[x],0) + self.pos
            l_list = [self.lista_palabras[x]]
            l_separacion = self.separation+(separar if x != num_lists-1 else 0)
            l_padding_top = self.padding_top-(separar//2 if x == num_lists-1 else 0)
            l_with_index = self.with_index if x == 0 and self.with_index else False
            l_scroll_bar_active = False if x != num_lists-1 else True
            l_header_top_left_radius = 20 if x == 0 else 0
            l_header_top_right_radius = 20 if x == self.num_list-1 else 0

            self.listas.append(List(l_size, l_pos, l_list, self.text_size, l_separacion, self.selected_color, self.text_color, 
                background_color=self.background_color, smothscroll=self.smothscroll, padding_top=l_padding_top,
                padding_left=self.padding_left, with_index=l_with_index, scroll_bar_active=l_scroll_bar_active,
                header=True, text_header=self.text_header[x], header_top_left_radius=l_header_top_left_radius, 
                header_top_right_radius=l_header_top_right_radius, font=self.fonts[x], header_border_color=self.border_color,
                border_width=-1))
            self.lineas.append([((self.size.x*self.colums_witdh[x] -1),self.listas[0].text_header.rect.h+1), ((self.size.x*self.colums_witdh[x] -1),self.rect.h)])
        
        self.create_border(self.rect, 2)

    def resize(self,size):
        self.size = Vector2(size)

        self.rect = pag.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.direccion(self.rect)
        self.lista_surface= pag.surface.Surface(self.rect.size)
        self.lista_surface_rect = self.lista_surface.get_rect()
        self.lista_surface.fill((0,0,0))
        self.lista_surface.set_colorkey((0,0,0))

        self.lineas.clear()
        for x in range(self.num_list):
            self.listas[x].resize(((self.size.x*self.colums_witdh[x+1]) - (self.size.x*self.colums_witdh[x]), self.size.y))
            self.listas[x].pos = Vector2(self.size.x*self.colums_witdh[x],30) + self.pos
            
            self.lineas.append([((self.size.x*self.colums_witdh[x] -1),self.listas[0].text_header.rect.h+1), ((self.size.x*self.colums_witdh[x] -1),self.rect.h)])
        self.create_border(self.rect, 2)

    def update(self,pos=None,dt=1, mouse_pos=(-10000,-10000)):
        super().update(pos,dt=1)
        if self.smothmove_bool:
            for x in range(self.num_list):
                self.listas[x].pos = Vector2(self.size.x*self.colums_witdh[x],30) + self.pos
        
        for x in self.listas:
            x.update()


    def draw(self,surface) -> pag.Rect:
        
        for x in self.listas:
            if self.redraw > 0:
                x.redraw += 2
            if x.draw(surface):
                self.redraw = 1

        if self.redraw < 1:
            return []

        for x in self.listas:
            pag.draw.rect(surface, self.border_color, x.rect, 1)
            
        for line in self.lineas[1:]:
            pag.draw.line(surface, self.border_color, Vector2(line[0])+self.raw_pos-(0,0)-(0,30), Vector2(line[1])+self.raw_pos-(0,1), 2)
        
        self.redraw = 0
        return (self.rect,)

    def rodar(self,y) -> None:
        for x in self.listas:
            x.rodar(y)
    def rodar_mouse(self,y) -> None:
        self.listas[-1].rodar_mouse(y)
        for i,x in sorted(enumerate(self.listas[:-1]),reverse=True):
            x.desplazamiento = self.listas[-1].desplazamiento
            self.rodar(0)

    def append(self,data) -> None:
        for i in range(self.num_list):
            if i < len(data):
                self.listas[i].append(data[i])
            else:
                self.listas[i].append(self.default[i])

    def change_list(self, list: list) -> None:
        self.clear()
        for x in list:
            self.append(x)

    def clear(self) -> None:
        [x.clear() for x in self.listas]

    def click(self,pos,ctrl=False,button=1):
        m = Vector2(pos)
        if not self.rect.collidepoint(m):
            return
        
        for i,x in sorted(enumerate(self.listas),reverse=True):
            if not x.rect.collidepoint(pos):
                continue
            a = x.click(m,ctrl,button)
            if a == 'scrolling' and i==len(self.listas)-1:
                self.scroll = True
                x.scroll = False
                return
            elif isinstance(a,dict):
                minilista = {'index':a['index'],'result':[l.select(a['index'], False,ctrl,button)['text'] for l in self.listas]}
                return minilista
        for x in self.listas:
            x.select(False)

    def select(self, index: int = False, diff: bool=True) -> str:
        return [l.select(index=int(index),diff=diff)['text'] for l in self.listas]

    def detener_scroll(self) -> None:
        self.scroll = False
        for x in self.listas:
            x.scroll = False

    def get_list(self) -> list:
        var1 = [x.get_list() for x in self.listas]
        return list([list(x) for x in zip(*var1)])

    def pop(self, index=-1):
        for i,x in sorted(enumerate(self.listas),reverse=True):
            x.pop(index)

    def get_selects(self):
        # return self.listas[0].get_selects()
        # return [x.get_selects() for x in self.listas]
        seleccionados = self.listas[0].get_selects()
        return [dict([('index',j)]+[(self.text_header[i],x[j]) for i,x in enumerate(self.listas)]) for j,y in seleccionados]


    @property
    def smothscroll(self):
        return self.__smothscroll
    @smothscroll.setter
    def smothscroll(self,smothscroll):
        self.__smothscroll = smothscroll
        for x in self.listas:
            x.smothscroll = self.smothscroll
        
    def __len__(self) -> int:
        return len(self.listas[0])

    def __getitem__(self,index: int):
        return self.listas[index]
    def __setitem__(self,index,value):
        self.listas[index] = value
    def __repr__(self) -> str:
        var = ''
        for x in self.listas:
            var += '\n'
            var += str(x)
        return var
    
