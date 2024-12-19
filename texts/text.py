import pygame as pag
from pygame.math import Vector2
from typing import Literal
from ..obj_Base import Base


'''
1) Hacer superficies y normalizar una funcion draw.
4) Hacer otra clase multilista, donde las listas sean tuplas y no List_box.
'''

class Text(Base):
    """
    # Funciones

    ### Comandos
    - draw() - Dibuja el texto\n
        - Si colocas border radius -1 sera redondo\n
    - change_text() - Cambia el texto\n
    - change_color() - Cambia el color del texto\n
    - get_text() - Retorna el texto actual
    - move() - Mueve el texto al sitio seleccionado\n
    - smothmove() - permite una transicion suave en el movimiento utilizando la clase Second Order Dinamics
    """
    
    def __init__(self,text: str,size: int,font: str|None=None, pos: tuple = (0,0),
                 dire: Literal["center","left","right","top","bottom","topleft","topright","bottomleft","bottomright"] ='center',
                 color='white',with_rect = False, color_rect ='black', border_width = -1, padding: int|list|tuple = 20, 
                 width = 0, height = 0, rect_width= 0, **kwargs) -> None:
        super().__init__(pos,dire)
        pag.font.init()
        text = str(text)
        self.raw_text = text.replace('\t', '    ').split('\n') if '\n' in text else text
        if len(self.raw_text) == 1:
            self.raw_text = self.raw_text[0]
        self.__size = size
        self.raw_font = font
        self.__color = color
        self.with_rect = with_rect
        self.color_rect = color_rect
        self.padding: Vector2 = Vector2(padding)
        self.rect_width = rect_width
        self.default_width = width
        self.default_height = height
        self.__width = width
        self.__height = height
        
        self.border_radius = kwargs.get('border_radius',0)
        self.border_top_left_radius = kwargs.get('border_top_left_radius',-1)
        self.border_bottom_left_radius = kwargs.get('border_bottom_left_radius',-1)
        self.border_top_right_radius = kwargs.get('border_top_right_radius',-1)
        self.border_bottom_right_radius = kwargs.get('border_bottom_right_radius',-1)
        self.border_width = border_width
        self.border_color = kwargs.get('border_color', 'black')

        self.lista_text: Text = []
        self.mode = 1
        self.__font = pag.font.Font(self.raw_font, size)

        self.smothmove_bool = False
        self.movimiento = None

        self.__generate()
    
    def __generate(self):
        self.last_rect = self.last_rect.union(self.rect)
        self.raw_text = self.text.replace('\t', '    ').split('\n') if '\n' in self.raw_text else self.raw_text
        if len(self.raw_text) == 1:
            self.raw_text = self.raw_text[0]
        self.__width = self.default_width
        self.__height = self.default_height
        if not isinstance(self.raw_text, list):
            self.mode = 1

            self.text_surf = self.__font.render(f'{self.raw_text}', 1, self.__color)
            self.rect = self.text_surf.get_rect()
            self.rect_text = self.text_surf.get_rect()
            if self.border_radius == -1:
                self.border_radius = 100_000
                n = max(self.rect.h + self.padding.y*2,self.rect.w + self.padding.x*2,self.__width,self.__height)
                self.rect.size = (n, n)
            else:
                self.rect.size = (max(self.__width,self.rect.w + self.padding.x), max(self.__height,self.rect.h + self.padding.y))
            self.direccion(self.rect)
            self.rect_text.center = self.rect.center
            self.create_border(self.rect, self.border_width)
        else:
            self.mode = 2
            self.lista_text.clear()

            self.text_surf = self.__font.render(f'{self.raw_text[0]}', 1, self.__color)
            self.text_lines = len(self.raw_text)
            self.text_height = self.text_surf.get_rect().h
            self.rect_text = self.text_surf.get_rect()
            self.rect = self.text_surf.get_rect()

            for txt in range(len(self.raw_text)):
                self.lista_text.append(Text(self.raw_text[txt], self.__size, self.raw_font, (self.pos[0],self.pos[1] + self.rect.h*txt), self.dire, self.color, False, self.color_rect, padding=self.padding, rect_width=0))
            
            if self.border_radius == -1:
                self.border_radius = 100_000
                self.rect.size = (max(self.rect.h * len(self.raw_text) + self.padding[0],max(self.__font.render(txt, 1, self.__color).get_rect().width + self.padding[0] for txt in self.raw_text)), max(self.rect.h * len(self.raw_text) + self.padding[2],max(self.__font.render(tixt, 1, self.color).get_rect().width + self.padding[1] for tixt in self.raw_text)))
            else:
                self.rect.width = min(max(self.__font.render(tixt, 1, self.__color).get_rect().width * 1.2 for tixt in self.raw_text), max(self.__font.render(tixt, 1, self.color).get_rect().width + self.padding[0] for tixt in self.raw_text))
                self.rect.height = (self.text_height * (len(self.raw_text)-1)) + self.padding[0]

            self.direccion(self.rect)
            self.rect.centery = self.rect_text.centery + (self.text_height * (len(self.raw_text)-1))/2
            
            self.create_border(self.rect, self.border_width)
        self.__width = self.rect.w
        self.__height = self.rect.h
        self.redraw = 2

    def update(self, pos = None,dt=1):
        super().update(pos,dt=dt)
        self.last_rect = self.last_rect.union(self.rect_border)
        if self.mode == 1:
            self.rect_text.center = self.rect.center
        elif self.mode == 2:
            self.rect.centery = self.rect_text.centery + (self.rect_text.h * (len(self.raw_text)-1))/2
            for i, txt in enumerate(self.lista_text):
                txt.update((self.pos[0],self.pos[1] + self.text_height*i))

    def draw(self, surface) -> list[pag.Rect]|None:
        if self.redraw < 1:
            return []
        
        self.rect_text.center = self.rect.center

        if self.mode == 2:
            if self.with_rect:
                pag.draw.rect(surface, self.color_rect, self.rect, self.rect_width,self.border_radius
                    , self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
            pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius
                ,self.border_top_left_radius,self.border_top_right_radius,self.border_bottom_left_radius,self.border_bottom_right_radius)
            for txt in self.lista_text:
                txt.draw(surface)
            return [self.rect_border, self.last_rect]
        
        if self.with_rect:
            pag.draw.rect(surface, self.color_rect, self.rect, self.rect_width,self.border_radius
                , self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius
            , self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)

        surface.blit(self.text_surf, self.rect_text)

        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border, r]
        return []


    @property
    def text(self):
        return self.raw_text
    @text.setter
    def text(self,texto):
        self.raw_text = str(texto)
        self.__generate()
    @property
    def font(self):
        return self.__font
    @font.setter
    def font(self,font):
        self.raw_font = font
        self.__font = pag.font.Font(self.raw_font, self.size)
        self.__generate()
    @property
    def size(self):
        return self.__size
    @size.setter
    def size(self,size):
        self.__size = size
        self.__font = pag.font.Font(self.raw_font, self.__size)
        self.__generate()
    @property
    def color(self):
        return self.__color
    @color.setter
    def color(self,color):
        self.__color = color
        if self.mode == 1:
            self.text_surf = self.font.render(f'{self.raw_text}', 1, self.color)
        elif self.mode == 2:
            for txt in self.lista_text:
                txt.color = color
        if self.redraw < 1:
            self.redraw = 1
    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self,width):
        self.__width = max(width,self.rect_text.w + self.padding[0]*2)
        self.default_width = self.__width
        self.rect.width = self.width
        self.create_border(self.rect,self.border_width)
        self.direccion(self.rect)
    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self,height):
        self.__height = max(height,self.rect_text.h + self.padding[1]*2)
        self.rect.height = self.height
        self.create_border(self.rect,self.border_width)
        self.direccion(self.rect)
        
    def __str__(self) -> str:
        return 'text: {} - pos: {} - mode: {}'.format(self.raw_text,self.pos,self.mode)
    def __repr__(self) -> str:
        return self.__str__()