import pygame as pag
from pygame.math import Vector2
from ..obj_Base import Base
from .text import Text
import math

class Multilist(Base):
    def __init__(self,pos=(0,0),direccion='center',size=(400,400),num_lists=(2), lists_start=[.0,.5], text_size=20,separacion=5,header=True, headers_texts=['id','obj'],
                 background_color='black', selected_color='grey', text_color='white', padding_top=25,smothscroll=True, color_key=(1,1,1)):
        super().__init__(pos,direccion)

        self.size = Vector2(size)
        self.num_list = num_lists
        self.lists_start = lists_start
        self.text_size = text_size
        self.text_color = text_color
        self.separacion = separacion
        self.header = header
        self.headers_texts = headers_texts
        self.backgroun_color = background_color
        self.__smothscroll = smothscroll
        self.color_key = color_key
        self.padding_top = padding_top

        self.re_draw = True
        self.desplazamiento = 0

        self.text_height = Text('|asd_-@*_+[{',self.text_size,None,(0,0),padding=0).height
        self.__lista_palabras = [[None for _ in range(num_lists)]]
        self.lista_textos = []

        self.selected_box = pag.rect.Rect(0,-500,self.size.x,self.text_height)

        self.__generate()

    def __generate(self):
        self.generate_objs()

        self.surf = pag.Surface(self.size)
        self.surf.fill(self.color_key)
        self.surf.set_colorkey(self.color_key)
        self.rect = self.surf.get_rect()
        self.direccion(self.rect)

    def draw_surf(self):
        self.surf.fill(self.color_key)
        self.surf.set_colorkey(self.color_key)


        # for x in self.lista_textos:
        #     x.draw(self.surf)

    def draw(self,surface: pag.Surface = None, update=False):
        # if self.re_draw:
        #     self.draw_surf()
        #     self.re_draw = False
        #     print('hola')

        pag.draw.rect(self.surf,'grey',self.selected_box)
        # surface.blit(self.surf,self.rect)
        for x in self.lista_textos:
            x.draw(surface)
        pag.draw.rect(surface,'white', self.rect, 1)

        if update:
            return self.rect

    def generate_objs(self):
        self.lista_textos.clear()
        for i,x in enumerate(self.__lista_palabras):
            for j,y in enumerate(x):
                self.lista_textos.append(
                    Text(x,self.text_size,None, (self.size.x*self.lists_start[i],self.padding_top+(self.text_height+self.separacion)*j), 'left', self.text_color)
                )

    def click(self,pos):
        if not self.rect.collidepoint(pos):
            return
        pos = (Vector2(pos)-(self.topleft)).y - self.padding_top

        print((math.ceil((pos/self.text_height)+(self.desplazamiento/self.text_height))))
        if -1 < (i := (pos/self.text_height)+(self.desplazamiento/self.text_height)) <= len(self.__lista_palabras):
            self.selected_text = i
            self.selected_box.centery = (int(i) * (self.text_height + self.separacion)) + self.padding_top
            self.re_draw = True
        else:
            self.selected_text = -1
            self.selected_box.top = -500
            self.re_draw = True

    @property
    def list(self):
        return self.__lista_palabras
    @list.setter
    def list(self,list):
        self.__lista_palabras = list
        self.generate_objs()
        self.re_draw = True
