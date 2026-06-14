from typing import Literal
import pygame as pag
import math
from pygame.math import Vector2
from ..obj_Base import Base
from ..constants import ALING_DIRECTION


class Text(Base):
    """
    # Otras variables
    - border_radius: int

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
            self,text: str,size: int,font: str|None|pag.font.Font=None, pos: tuple = (0,0),
            dire: ALING_DIRECTION ='center', color='white',with_rect = False, color_rect ='black', 
            border_width = -1, padding: int|list|tuple = 0, min_width = 0,max_width=math.inf, min_height = 0, rect_width= 0, 
            always_draw=False, border_radius=0, wrap=True, text_align='center', max_lines=math.inf,
            underline = False, border_top_left_radius = -1, border_top_right_radius = -1,
            border_bottom_left_radius = -1, border_bottom_right_radius = -1,
            border_color = 'black', **kwargs
        ) -> None:
        super().__init__(pos,dire)
        if not pag.font.get_init():
            pag.font.init()
        self.raw_text = str(text)
        self.__underline = underline
        self.__size: int = size
        self.raw_font = 'asasdas' if font is None else None
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
        self.lista_text_rects: list[pag.Rect] = []


        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        self.lista_text: list[pag.Surface] = []
        self.font = font

        self.smothmove_bool = False
        self.movimiento = None
        self.cursor = pag.SYSTEM_CURSOR_ARROW

        self.__generate()

    def __generate(self):
        self.last_rect = self.last_rect.copy().union(self.rect_border.copy())
        self.lista_text.clear()
        if self.max_width <= 0 and not "\n" in self.raw_text:
            self.lista_text.append(self.__font.render(str(self.raw_text), True, self.__color))
            self.create_rect()
            return
        NEWLINE_TOKEN = f'$$$NEWLINE$$${self.__hash__()}$$$'
        splited_text = [] # [" ", "hola", " ", "mundo", "\n", "hola", "mundo"]
        parrafos = self.raw_text.split('\n')

        for i,txt in enumerate(parrafos):
            palabras = [palabra for palabra in txt.split(' ') if palabra]

            splited_text.extend(palabras)

            if i < len(parrafos)-1:
                splited_text.append(NEWLINE_TOKEN)

        if not splited_text:
            self.create_rect()
            return
        actual_txt = splited_text[0] if splited_text else ""
        token_index = 1

        while token_index < len(splited_text):
            next_token = splited_text[token_index]
            if next_token == NEWLINE_TOKEN:
                if actual_txt:
                    self.lista_text.append(self.__font.render(actual_txt, True, self.__color))
                actual_txt = ""
                token_index += 1
                continue
            potential_line = (actual_txt + " " + next_token) if actual_txt else next_token
            potential_width = self.__font.render(potential_line, True, self.__color).get_width()

            if potential_width > self.max_width and self.wrap and self.max_width > 0:
                if not actual_txt:
                    self.lista_text.append(self.get_txt_ajustado(str(next_token)))
                    token_index += 1
                else:
                    self.lista_text.append(self.__font.render(actual_txt, True, self.__color))                    
                    actual_txt = next_token
                    token_index += 1
                    
            elif self.max_lines > 0 and len(self.lista_text) >= self.max_lines:
                self.lista_text.append(self.get_txt_ajustado(str(actual_txt), always_elipsis=True))
                break
            else:
                actual_txt = potential_line
                token_index += 1
        
        if actual_txt:
            if self.max_lines > 0 and len(self.lista_text) >= self.max_lines:
                pass
            else:
                self.lista_text.append(self.get_txt_ajustado(str(actual_txt)))
        
        self.create_rect()

    
    def create_rect(self):
        self.last_rect = self.last_rect.copy().union(self.rect_border.copy())
        if self.border_radius == -1:
            s = max(
                max([x.get_width()+self.padding[0]*2 for x in self.lista_text]+[self.min_width]),
                max(self.min_height,(self.text_height*len(self.lista_text)) + self.padding[1])
            )
            size = (s,s)
        else:
            size = (
                max([x.get_width()+self.padding[0]*2 for x in self.lista_text]+[self.min_width]),
                max(self.min_height,(self.text_height*len(self.lista_text)) + self.padding[1]*2),
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
        self.create_texts_rects()

        self.redraw += 3

    def update(self, pos = None,dt=1, **kwargs):
        if super().update(pos,dt=dt):
            self.create_texts_rects()
        self.last_rect: pag.Rect = self.last_rect.copy().union(self.rect_border.copy())
        if self.redraw > 0:
            self.create_texts_rects()
    
    def create_texts_rects(self):
        self.redraw += 2
        self.lista_text_rects.clear()
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
            self.lista_text_rects.append(r.copy())

    def draw(self, surface, always_draw = False, diff_pos = (0,0)) -> list[pag.Rect]|None:
        if always_draw or self.always_draw:
            self.redraw += 2
        if not self.visible and self.redraw > 0:
            return [self.rect_border]
        if self.redraw < 1 or not self.visible:
            return []
        
        if self.with_rect:
            pag.draw.rect(surface, self.color_rect, self.rect.move(diff_pos), self.rect_width,self.border_radius if self.border_radius != -1 else self.rect.width, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        pag.draw.rect(surface, self.border_color,self.rect_border.move(diff_pos), self.border_width, self.border_radius if self.border_radius != -1 else self.rect.width, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)

        for i,txt in enumerate(self.lista_text):
            surface.blit(txt, self.lista_text_rects[i].move(diff_pos))

        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border.move(diff_pos)]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect.move(diff_pos), r.move(diff_pos)]

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
        texto = str(texto)
        if self.raw_text == texto:
            return
        self.raw_text = texto
        self.__generate()
    @property
    def font(self):
        return self.__font
    @font.setter
    def font(self,font: str|pag.font.Font):
        if self.raw_font == font:
            return
        if isinstance(font, pag.font.Font):
            self.raw_font = font
            self.__font = font
        elif isinstance(font, str) or font is None:
            self.raw_font = font
            self.__font = pag.font.Font(self.raw_font, self.size)
        else:
            raise TypeError('El tipo de font debe ser "str" o "pag.font.Font"')
        self.__font.set_underline(self.underline)
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
    def underline(self):
        return self.__underline
    @underline.setter
    def underline(self,underline):
        if self.__underline == underline:
            return
        self.__underline = underline
        self.__font.set_underline(self.__underline)
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
        if width < 1:
            raise ValueError("El ancho máximo debe ser mayor o igual a 1")
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
        if self.__max_lines == max_lines:
            return
        self.__max_lines = max_lines
        self.__generate()
    def __str__(self) -> str:
        return 'Text: {} - pos: {}'.format(self.raw_text,self.pos)
    def __repr__(self) -> str:
        return self.__str__()
    
