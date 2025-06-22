from typing import Literal
import pygame as pag
import math
from pygame.math import Vector2
from ..obj_Base import Base
from ..constants import ALING_DIRECTION

import Utilidades as uti


class Text(Base):
    """
    # Otras variables
    - border_radius: int
    - border_top_left_radius: int
    - border_top_right_radius: int
    - border_bottom_left_radius: int
    - border_bottom_right_radius: int
    - border_color: str

    ## Anotaciones
    - Si colocas border radius -1 sera redondo\n

    ### Comandos
    - draw() - Dibuja el texto\n
    - change_text() - Cambia el texto\n
    - change_color() - Cambia el color del texto\n
    - get_text() - Retorna el texto actual
    - move() - Mueve el texto al sitio seleccionado\n
    - smothmove() - permite una transicion suave en el movimiento utilizando la clase Second Order Dinamics
    """
    def __init__(
            self,text: str,size: int,font: str|None=None, pos: tuple = (0,0),
            dire: ALING_DIRECTION ='center', color='white',with_rect = False, color_rect ='black', 
            border_width = -1, padding: int|list|tuple = 0, min_width = 0,max_width=math.inf, min_height = 0, rect_width= 0, 
            always_draw=False, border_radius=0, wrap=True, text_align='center', max_lines=math.inf, **kwargs
        ) -> None:
        super().__init__(pos,dire)
        if not pag.font.get_init():
            pag.font.init()
        self.raw_text = str(text)
        self.__size: int = size
        self.raw_font: str = font
        self.__color: str = color
        self.with_rect: bool = with_rect
        self.color_rect: str = color_rect
        self.padding: Vector2 = Vector2(padding)
        self.rect_width: int = rect_width
        self.__min_width: int = min_width
        self.__max_width: int = max_width
        self.__min_height: int = min_height
        self.always_draw: bool = always_draw
        self.wrap: bool = wrap
        self.text_align = text_align
        self.__max_lines = max_lines


        self.border_color = kwargs.get('border_color', 'black')
        self.border_width = border_width
        self.border_radius = border_radius
        self.border_top_left_radius = kwargs.get('border_top_left_radius',-1)
        self.border_bottom_left_radius = kwargs.get('border_bottom_left_radius',-1)
        self.border_top_right_radius = kwargs.get('border_top_right_radius',-1)
        self.border_bottom_right_radius = kwargs.get('border_bottom_right_radius',-1)

        self.lista_text: list[pag.Surface] = []
        self.__font = pag.font.Font(self.raw_font, size)
        self.text_height = self.__font.render('hola|-|█', True, self.__color).get_height()

        self.smothmove_bool = False
        self.movimiento = None
        self.cursor = pag.SYSTEM_CURSOR_ARROW

        self.__generate()

    
    def __generate(self):
        self.last_rect = self.last_rect.copy().union(self.rect_border.copy())
        self.lista_text.clear()
        if self.max_width <= 0:
            self.lista_text.append(self.__font.render(str(self.raw_text), True, self.__color))
            self.create_rect()
            return
        index = 1

        splited_text = self.raw_text.split(' ')
        actual_txt = splited_text[0]
        lines_count = 0
        if '\n' in actual_txt:
            pass
        elif len(splited_text) == 1 and self.max_width <= 0:
            self.lista_text.append(self.__font.render(actual_txt, True, self.__color))
            actual_txt = ''
        elif self.max_width > 0 and len(splited_text) == 1:
            self.lista_text.append(self.get_txt_ajustado(str(actual_txt)))
            actual_txt = ''

        while index < len(splited_text):
            txt = splited_text[index]
            actual_rendered_txt: pag.Surface = self.__font.render(str(actual_txt+ ' ' +txt), True, self.__color)
            
            if '\n' in actual_txt:
                if actual_txt == '\n':
                    actual_txt = ''
                    lines_count += 1
                    continue
                actual_txt = actual_txt.split('\n',maxsplit=1)
                if lines_count >= self.max_lines:
                    index += math.inf
                    break
                self.lista_text.append(self.__font.render(actual_txt[0], True, self.__color))
                lines_count += 1
                actual_txt = actual_txt[1]
                index -= 1
            elif index >= len(splited_text):
                self.lista_text.append(self.get_txt_ajustado(str(actual_txt)))
                lines_count += 1
                actual_txt = ''
                break
            elif lines_count > self.max_lines:
                self.lista_text.append(self.get_txt_ajustado(str(actual_txt), always_elipsis=True))
                lines_count += 1
                index += math.inf
                actual_txt = ''
            elif actual_rendered_txt.get_width() > self.max_width and self.wrap:
                lines_count += 1
                if self.max_lines > 0 and lines_count >= self.max_lines:
                    self.lista_text.append(self.get_txt_ajustado(str(actual_txt), always_elipsis=True))
                    lines_count += math.inf
                    index += math.inf
                    actual_txt = ''
                else:
                    self.lista_text.append(self.__font.render(str(actual_txt), True, self.__color))
                    index -= 1

                actual_txt = txt
            elif actual_rendered_txt.get_width() > self.max_width and not self.wrap:
                self.lista_text.append(self.get_txt_ajustado(str(actual_txt)))
                index += math.inf
                math.inf
                lines_count += 1
                actual_txt = ''
            else:
                actual_txt += ' ' + txt
            index += 1
        
        if actual_txt:
            self.lista_text.append(self.__font.render(actual_txt, True, self.__color))
        
        self.create_rect()
    
    def create_rect(self):
        self.last_rect = self.last_rect.copy().union(self.rect_border.copy())
        if self.border_radius == -1:
            s = max(
                max([x.get_width()+self.padding[0]*2 for x in self.lista_text]+[self.min_width]),
                max(self.min_height,self.text_height*len(self.lista_text) + self.padding[1])
            )
            size = (s,s)
        else:
            size = (
                max([x.get_width()+self.padding[0]*2 for x in self.lista_text]+[self.min_width]),
                max(self.min_height,self.text_height*len(self.lista_text) + self.padding[1]*2),
            )
        self.rect = pag.Rect(
            self.pos[0],
            self.pos[1],
            size[0],
            size[1],
        )
        self.direccion(self.rect)
        self.create_border(self.rect, self.border_width)
        self.last_rect = self.last_rect.copy().union(self.rect_border.copy())

        self.redraw += 3

    def update(self, pos = None,dt=1, **kwargs):
        super().update(pos,dt=dt)
        self.last_rect: pag.Rect = self.last_rect.copy().union(self.rect_border.copy())
    
    def draw(self, surface, always_draw = False) -> list[pag.Rect]|None:
        if always_draw or self.always_draw:
            self.redraw += 2
        if self.redraw < 1:
            return []
        
        if self.with_rect:
            pag.draw.rect(surface, self.color_rect, self.rect, self.rect_width,self.border_radius if self.border_radius != -1 else self.rect.width, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        pag.draw.rect(surface, self.border_color,self.rect_border, self.border_width, self.border_radius if self.border_radius != -1 else self.rect.width, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)

        for i,txt in enumerate(self.lista_text):
            r = txt.get_rect()
            if self.text_align == 'center':
                r.centerx = self.rect.centerx
            elif 'left' in self.text_align:
                r.left = self.rect.left + self.padding[0]
            elif 'right' in self.text_align:
                r.right = self.rect.right - self.padding[0]
            else:
                r.centerx = self.rect.centerx

            if 'top' in self.text_align:
                r.top = self.rect.top + self.padding[1] + (i*self.text_height)
            elif 'bottom' in self.text_align:
                r.bottom = self.rect.bottom - self.padding[1] - (i*self.text_height)
            else:
                r.centery = self.rect.centery + ((i-(len(self.lista_text)-1)/2)*self.text_height)
            # r.centery = self.rect.top + self.padding[1] + (i*self.text_height) + self.text_height//2
            # r.centery = self.rect.centery + ((i-(len(self.lista_text)-1)/2)*self.text_height)
            surface.blit(txt, r)

        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect, r]

    def click(self, mouse_pos) -> Literal[False]:
        return False

    def get_txt_ajustado(self, text, always_elipsis=False):
        txt = self.__font.render(text+('...' if always_elipsis else ''), True, self.__color)
        total_width = txt.get_width()
        if total_width <= self.max_width:
            return txt
        
        i = 0
        for i in range(1,len(text)):
            txt = self.__font.render(text[:-i]+'...', True, self.__color)
            if txt.get_width() <= self.max_width:
                break
            
        return txt

    @property
    def text(self):
        return self.raw_text
    @text.setter
    def text(self,texto):
        if self.raw_text == str(texto):
            return
        self.raw_text = str(texto)
        self.__generate()
    @property
    def font(self):
        return self.__font
    @font.setter
    def font(self,font):
        if self.raw_font == str(font):
            return
        self.raw_font = font
        self.__font = pag.font.Font(self.raw_font, self.size)
        self.text_height = self.__font.render('hola|-|█', True, self.__color).get_height()
        self.__generate()
    @property
    def size(self):
        return self.__size
    @size.setter
    def size(self,size):
        if self.__size == int(size) or size < 1:
            return
        self.__size = int(size)
        self.__font = pag.font.Font(self.raw_font, self.__size)
        self.text_height = self.__font.render('hola|-|█', True, self.__color).get_height()
        self.__generate()
    @property
    def color(self):
        return self.__color
    @color.setter
    def color(self,color):
        if self.__color == color:
            return
        self.__color = color
        self.__generate()
    @property
    def min_width(self):
        return self.__min_width
    @min_width.setter
    def min_width(self,width):
        if self.__min_width == int(width):
            return
        self.__min_width = int(width)
        self.__generate()
        
    @property
    def max_width(self):
        return self.__max_width
    @max_width.setter
    def max_width(self,width):
        if self.__max_width == int(width):
            return
        self.__max_width = int(width)
        self.__generate()
    

    @property
    def min_height(self) -> int:
        return self.__min_height
    @min_height.setter
    def min_height(self,height: int):
        if self.__min_height == int(height):
            return
        self.__min_height = int(height)
        self.__generate()
        
    @property
    def height(self):
        return self.rect.height
    @property
    def width(self):
        return self.rect.width
    
    @property
    def max_lines(self):
        return self.__max_lines
    @max_lines.setter
    def max_lines(self,max_lines):
        if self.__max_lines == int(max_lines):
            return
        self.__max_lines = int(max_lines)
        self.__generate()
    def __str__(self) -> str:
        return 'Text: {} - pos: {}'.format(self.raw_text,self.pos)
    def __repr__(self) -> str:
        return self.__str__()
    
