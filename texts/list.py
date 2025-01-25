import pygame as pag
import math
from pygame.math import Vector2
from ..obj_Base import Base
from .text import Text
from ..Animaciones import Second_Order_Dinamics



class List(Base):
    '''
    ### More options
     - padding_top
     - padding_left
     - scroll_bar_active
     - barra_color
     - barra_color_hover

     - header_top_right_radius
     - header_top_left_radius
     - header_border_color

    ## Ejemplo Codigo:

    elif evento.type == MOUSEMOTION and [lista].scroll:
        [lista].rodar_mouse(evento.rel[1])
    '''
    def __init__(self, size: tuple, pos: tuple, lista: list = [None], text_size: int = 20, separation: int = 0,
        selected_color = (100,100,100,100), text_color= 'white', header: bool =False, text_header:str = None,
        background_color = 'black', font=None, smothscroll=False, dire='topleft',border_width=2,border_radius=20, **kwargs) -> None:

        super().__init__(pos,dire)
        self.__size = Vector2(size)
        self.__width = size[0]
        self.__height = size[1]
        self.text_size = max(6,text_size)
        self.__smothscroll = bool(smothscroll)
        self.background_color = background_color
        self.selected_color = selected_color
        self.padding_top = kwargs.get('padding_top',10)
        self.padding_left = kwargs.get('padding_left',20)
        self.border_width = border_width
        self.border_radius = border_radius
        self.text_color = text_color
        self.header = header
        self.text_header = text_header
        self.raw_font = font
        self.font = pag.font.Font(self.raw_font, text_size)
        self.separacion = separation

        self.header_top_right_radius = kwargs.get('header_top_right_radius',20)
        self.header_top_left_radius = kwargs.get('header_top_left_radius',20)
        self.header_border_color = kwargs.get('header_border_color',20)
        self.scroll_bar_active = kwargs.get('scroll_bar_active',True)

        self.letter_size = self.font.render('ssss|.)0_-',1, self.text_color).get_height()

        self.__lista_palabras = list(lista)
        self.lista_objetos: list[pag.Surface] = []

        self.barra = pag.rect.Rect(0, 0, 15, 50)
        self.barra_hover = False
        self.barra_color = kwargs.get('barra_color',(255,255,255))
        self.barra_color_hover = kwargs.get('barra_color_hover',(150,150,150))

        self.desplazamiento = 0
        self.total_content_height = 0
        self.desplazamiento_movent = Second_Order_Dinamics(60, 1.5, 1, 1.5, 0)
        self.desplazamiento_smoth = 0
        self.last_dezplazamiento_pos = 0
        self.selected_nums: list[int] = []


        self.scroll = False

        self.__generate()
        self.resize(size)


    def __generate(self):

        if self.header:
            self.text_header: Text = Text(self.text_header, 23, None, self.pos, 'bottomleft', 'black', True, 'darkgrey',
            padding=(5,15),border_width=1, border_top_left_radius=self.header_top_left_radius,
            border_top_right_radius=self.header_top_right_radius, border_color=self.header_border_color, width=self.size[0])
            self.rect = pag.rect.Rect(self.pos[0], self.pos[1]+self.text_header.rect.h, self.size[0], self.size[1]-self.text_header.rect.h)
            self.text_header.bottomleft = self.rect.topleft
        else:
            self.rect = pag.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        self.lista_surface= pag.surface.Surface(self.rect.size)
        self.lista_surface_rect = self.lista_surface.get_rect()
        self.lista_surface_rect.topleft = self.pos
        self.lista_surface.fill((254,1,1))
        self.lista_surface.set_colorkey((254,1,1))

        self.__gen_list()
        self.resize(self.__size)

    def resize(self,size):
        self.__width = max(size[0],30)
        self.__height = max(size[1],100)
        self.__size = Vector2(self.__width,self.__height)
        if self.header:
            self.rect = pag.rect.Rect(self.pos[0], self.pos[1]+ self.text_header.height, self.size[0], self.size[1]-self.text_header.height)
            self.text_header.width = self.size[0]
            self.text_header.pos = self.rect.topleft
        else:
            self.rect = pag.rect.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        self.lista_surface= pag.surface.Surface(self.rect.size)
        self.lista_surface_rect = self.lista_surface.get_rect()
        self.lista_surface_rect.topleft = self.pos
        self.lista_surface.fill((254,1,1))
        self.lista_surface.set_colorkey((254,1,1))

        self.select_box = pag.rect.Rect(0,-5000,self.lista_surface_rect.w,self.letter_size + self.separacion)

        self.rodar(0)

        self.set_height()
        self.barra.right = self.lista_surface_rect.w

        self.select(self.selected_nums[0] if self.selected_nums else False, diff=True, more=True)

        self.draw_surf()

        p = self.rect.union(self.text_header.rect) if self.header else self.rect
        self.create_border(p, self.border_width)
        self.last_rect = self.last_rect.union(self.rect_border)

    def create_text(self,text:str):
        return self.font.render(str(text),1,self.text_color)

    def __gen_list(self):
        self.lista_objetos.clear()
        for text in self.lista_palabras:
            self.lista_objetos.append(self.create_text(text))
        self.set_height()

    def draw_surf(self):
        self.lista_surface.fill(self.background_color)

        if self.selected_nums:
            for num in self.selected_nums:
                self.select_box.top = self.padding_top + ((self.letter_size+self.separacion)*num) + self.desplazamiento_smoth - self.separacion/2
                pag.draw.rect(self.lista_surface, self.selected_color, self.select_box)

        o = (math.floor((-self.desplazamiento_smoth-self.padding_top)/(self.letter_size+self.separacion)), math.ceil((self.lista_surface_rect.h+(-self.desplazamiento_smoth-self.padding_top))/(self.letter_size+self.separacion)))
        for x in range(min(o[0],len(self.lista_objetos)-1),min(o[1],len(self.lista_objetos))):
            if x < 0:
                continue
            self.lista_surface.blit(self.lista_objetos[x], (self.padding_left, self.padding_top + ((self.letter_size+self.separacion)*x) + self.desplazamiento_smoth))

        if self.scroll_bar_active and self.total_content_height + self.lista_surface_rect.h > self.rect.h:
            pag.draw.rect(self.lista_surface, self.barra_color_hover if (self.barra_hover or self.scroll) else self.barra_color, self.barra,border_radius=5)
        if self.redraw < 1:
            self.redraw = 1

    def draw(self,surface, always_draw = False):
        if (self.smothscroll and self.lista_objetos and int(self.last_dezplazamiento_pos) != int(self.desplazamiento_movent.y.y)) or self.redraw > 0:
            self.draw_surf()
            self.last_dezplazamiento_pos = int(self.desplazamiento_movent.y.y)

        if always_draw:
            self.text_header.redraw += 1
            self.redraw += 1

        if self.header:
            self.text_header.draw(surface)

        if self.redraw < 1:
            return []
        
        surface.blit(self.lista_surface,self.rect)
        pag.draw.rect(surface, 'black', self.rect_border, self.border_width, border_radius=self.border_radius, border_bottom_left_radius=0, border_bottom_right_radius=0)
        r = self.rect_border.union(self.text_header.rect) if self.header else self.rect_border
        if self.redraw < 2:
            self.redraw = 0
            return [r]
        else:
            self.redraw = 0
            r2 = self.last_rect.union(r).copy()
            self.last_rect = r.copy()
            return [r, r2]
        

    def update(self,dt=1, mouse_pos=(-100000,-10000), **kwargs):
        if self.smothscroll:
            self.desplazamiento_smoth = int(self.desplazamiento_movent.update(self.desplazamiento).x)
        super().update()
        if self.header:
            self.text_header.bottomleft = self.rect.topleft
            self.rect_border.bottom = self.rect.bottom

        if (self.barra.collidepoint(pag.Vector2(mouse_pos)-self.topleft) and self.scroll_bar_active and not self.barra_hover) or \
            (not self.barra.collidepoint(pag.Vector2(mouse_pos)-self.topleft) and self.scroll_bar_active and self.barra_hover):
            self.barra_hover = not self.barra_hover
            self.redraw += 1

    def set_height(self):
        if not self.lista_palabras:
            return
        self.total_content_height = (self.letter_size+self.separacion)*(len(self.lista_palabras)) + self.padding_top - self.lista_surface_rect.h
        # self.barra.h = max(10,self.lista_surface_rect.h*(self.lista_surface_rect.h/(self.total_content_height + self.rect.height)))
        self.barra.h = max(10,self.lista_surface_rect.h*(self.lista_surface_rect.h/(self.total_content_height+self.lista_surface_rect.h)))

    def rodar(self, y) -> None:
        if self.total_content_height + self.lista_surface_rect.h < self.rect.h:
            if not self.smothscroll or abs(sum(self.desplazamiento_movent.yd.xy)) < 0.1:
                self.draw_surf()
            return

        self.desplazamiento += y
        self.desplazamiento = min(0, self.desplazamiento)
        self.desplazamiento = max(-self.total_content_height, self.desplazamiento)

        if not self.smothscroll:
            self.desplazamiento_smoth = self.desplazamiento

        if self.scroll_bar_active and self.total_content_height > 0:
            self.barra.top = -(self.lista_surface_rect.h - self.barra.h) * (self.desplazamiento / self.total_content_height)
        else:
            self.barra.top = 0


        if not self.smothscroll or abs(sum(self.desplazamiento_movent.yd.xy)) < 0.1:
            self.draw_surf()

    def rodar_mouse(self, rel):
        self.barra.centery += rel
        if self.barra.top <= 0:
            self.barra.top = 0
            self.desplazamiento = 0
            self.rodar(0)
            return
        self.desplazamiento = -(self.total_content_height / ((self.lista_surface_rect.h - self.barra.h) / self.barra.top))
        self.rodar(0)

    def select(self, index: int = False, diff = True, more = False,button=1) -> str:
        if isinstance(index,int) and index > len(self.lista_palabras)-1 or index < 0:
            index = False

        if index is False:
            self.selected_nums.clear()
            self.select_box.top = -200
            if not self.smothscroll or abs(sum(self.desplazamiento_movent.yd.xy)) < 0.1:
                self.draw_surf()
            return False
        elif isinstance(index,int):
            if (not more and index not in self.selected_nums) or (button == 1 and not more):
                self.selected_nums.clear()
            if index not in self.selected_nums:
                self.selected_nums.append(index)
            if diff:
                self.desplazamiento = (-self.letter_size*(index+1) + self.padding_top) + self.lista_surface_rect.h/2
            self.rodar(0)
            return {'text': self.lista_palabras[index], 'index': index}
        else:
            raise ValueError('Invalid index, must be an int or False')

    def click(self, pos, ctrl=False, button=1):
        if not self.rect.collidepoint(pos):
            self.select(False)
            return False
        m = Vector2(pos) - self.rect.topleft
        m += (0,5)

        if self.scroll_bar_active and self.barra.collidepoint(m):
            self.scroll = True
            return 'scrolling'
        touch = round((m.y-self.padding_top - self.desplazamiento_smoth)//(self.letter_size+self.separacion))
        self.select(touch if touch > -1 else False,False, ctrl, button)

        return {'text': self.lista_palabras[touch], 'index': touch} if touch > -1 and touch < len(self.lista_palabras) else False

    def append(self, text: str):
        self.lista_palabras.append('{}'.format(text))
        self.lista_objetos.append(self.create_text(text))
        self.set_height()
        self.rodar(0)

    def insert(self, index: int, text: str):
        self.lista_palabras.insert(index, text)
        self.lista_objetos.insert(index, self.create_text(text))
        self.set_height()
        self.rodar(0)

    def pop(self,index:int = -1):
        self.lista_palabras.pop(index)
        self.lista_objetos.pop(index)
        self.set_height()
        self.rodar(0)

    def clear(self):
        self.lista_palabras.clear()
        self.lista_objetos.clear()
        self.selected_nums.clear()
        self.desplazamiento = 0
        self.set_height()
        self.rodar(0)

    def get_selects(self) -> list[str]:
        return [(x,self.lista_palabras[x]) for x in self.selected_nums]

    @property
    def lista_palabras(self):
        return self.__lista_palabras
    @lista_palabras.setter
    def lista_palabras(self, lista_palabras):
        self.__lista_palabras = list(lista_palabras)
        self.__generate()

    @property
    def selected_color(self):
        return self.__selected_color

    @selected_color.setter
    def selected_color(self, selected_color):
        self.__selected_color = selected_color

    @property
    def smothscroll(self):
        return self.__smothscroll

    @smothscroll.setter
    def smothscroll(self, smothscroll):
        self.__smothscroll = bool(smothscroll)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.resize(size)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        self.resize((width,self.size.y))

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        self.resize((self.size.x,height))

    def __len__(self):
        return len(self.lista_palabras)

    def __getitem__(self, index):
        return self.lista_palabras[index]

    def __setitem__(self, index, value: str):
        self.lista_palabras[index] = str(value)
        self.lista_objetos[index] = self.create_text(value)
        self.rodar(0)
    def __repr__(self):
        return '\n'.join(self.lista_palabras)

    def __str__(self) -> str:
        text = f'{'_':_>20}\n'
        text += f'{self.text_header if self.header else "   ----   "}\n['
        for x in self.lista_palabras:
            text += '{},'.format(x)
        # if self.lista_palabras:
        #     text += '\n'.join(self.lista_palabras)
        text += f']\n{'-':-^20}\n'
        return text