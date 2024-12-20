import pygame as pag, time
from pygame.math import Vector2
from ..obj_Base import Base
from .text import Text

def lerp(a, b, t):
    return a + (b - a) * t

class Input(Base):
    '''
    for x in self.lista_inputs:
        x.eventos_teclado(eventos)
    '''
    def __init__(self, pos: tuple, text_size: int, font: str, text_value: str = 'Type here',max_letter = 20, padding = 20,
        width=100, height=20, text_color='white',text_value_color='grey', background_color = 'black', dire: str = 'topleft', **kwargs) -> None:
        
        super().__init__(pos,dire)
        self.border_radius = kwargs.get('border_radius',0)
        self.border_top_left_radius = kwargs.get('border_top_left_radius',-1)
        self.border_bottom_left_radius = kwargs.get('border_bottom_left_radius',-1)
        self.border_top_right_radius = kwargs.get('border_top_right_radius',-1)
        self.border_bottom_right_radius = kwargs.get('border_bottom_right_radius',-1)
        self.border_width = kwargs.get('border_width', -1)
        self.border_color = kwargs.get('border_color', 'black')
        self.pointer_color = kwargs.get('pointer_color', 'white')

        self.text_size = text_size
        self.text_color = text_color
        self.text_value_color = text_value_color

        self.padding = Vector2(padding)
        self.raw_text = ''
        self.text_value = text_value
        self.max_letter = max_letter
        self.background_color = background_color
        self.font = font
        
        self.width = width
        self.height = height
        self.generate()

        self.typing = False
        self.typing_pos = 0
        self.backspace = False
        self.supr = False
        self.deleting = False
        self.del_time = 0
        self.left_b = False
        self.left_time = 0
        self.right_b = False
        self.right_time = 0
        self.typing_line = False
        self.typing_line_time = time.time()
        self.letter_pos = [0]
        self.button_pressed_time = 0
        self.draw_surf()

    def generate(self):
        t = Text('', self.text_size, self.font, self.pos, 'left', padding=self.padding,width=self.width,height=self.height)
        self.rect = t.rect.copy()

        self.text = Text('abdc123--||', self.text_size, self.font, self.pos, 'left',self.text_color,True, self.background_color,width=self.width-self.padding.x*2, padding=5)
        self.rect2 = self.text.rect.copy()
        self.input_surface = pag.Surface(self.rect2.size)
        self.input_surface.fill(self.background_color)
        self.surf_rect = self.input_surface.get_rect()

        self.text = Text(self.raw_text, self.text_size, self.font, (0,self.input_surface.get_height()/2), 'left',self.text_color,True, self.background_color, padding=0)
        self.text_value = Text(self.text_value, self.text_size, self.font, (0,self.input_surface.get_height()/2), 'left',self.text_value_color,True, self.background_color, padding=0)

        self.surf_rect.center = self.rect.center
        self.create_border(self.rect, self.border_width)
        self.direccion(self.rect)


    def draw_surf(self):
        self.input_surface.fill(self.background_color)
        if self.raw_text == '':
            self.text_value.redraw = 1
            self.text_value.draw(self.input_surface)
        else:
            self.text.redraw = 1
            self.text.draw(self.input_surface)
        if self.typing_line:
            pag.draw.line(self.input_surface, self.pointer_color, (sum(self.letter_pos[:self.typing_pos])+self.text.left,0),
                          (sum(self.letter_pos[:self.typing_pos])+self.text.left,self.input_surface.get_height()))
        if self.redraw < 1:
            self.redraw = 1

    def draw(self, surface) -> None:
        self.update_pressed_keys()
        if self.redraw < 1:
            return []

        pag.draw.rect(surface, self.background_color, self.rect, 0, self.border_radius, self.border_top_left_radius, 
                      self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius, 
                      self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, 
                      self.border_bottom_right_radius)
    
        if self.typing and time.time()-self.typing_line_time > .7:
            self.typing_line = not self.typing_line
            self.typing_line_time = time.time()
            self.draw_surf()

        self.surf_rect.center = self.rect.center
        surface.blit(self.input_surface, self.surf_rect)
        
        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border, r]


    def update_pressed_keys(self):
        if time.time() - self.button_pressed_time > .5:
            if self.backspace and time.time() - self.del_time > .03:
                self.del_letter()
                self.del_time = time.time()
            elif self.left_b and time.time() - self.left_time > .03:
                self.to_left()
                self.left_time = time.time()
            elif self.right_b and time.time() - self.right_time > .03:
                self.to_right()
                self.right_time = time.time()
            self.draw_surf()

    def eventos_teclado(self, eventos):
        for evento in eventos:
            if evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                self.click(evento.pos)
            if not self.typing:
                continue
            
            if evento.type == pag.KEYDOWN and not (self.backspace or self.left_b or self.right_b):
                if evento.key == pag.K_LEFT:
                    self.to_left()
                elif evento.key == pag.K_RIGHT:
                    self.to_right()
                elif evento.key == pag.K_BACKSPACE:
                    self.del_letter()
                elif evento.key == pag.K_DELETE:
                    self.del_letter(-1)
                elif evento.key == pag.K_RETURN:
                    return "enter"
                elif evento.key == pag.K_TAB:
                    return "tab"
                self.button_pressed_time = time.time()
            elif evento.type == pag.TEXTINPUT:
                self.add_letter(evento.text)
                self.draw_surf()
            elif evento.type == pag.KEYUP:
                if evento.key == pag.K_BACKSPACE:
                    self.backspace = False
                    self.deleting = False
                elif evento.key == pag.K_DELETE:
                    self.deleting = False
                    self.supr = False
                elif evento.key == pag.K_LEFT:
                    self.left_b = False
                elif evento.key == pag.K_RIGHT:
                    self.right_b = False

    def check_pos_letter_click(self,x):
        acumulacion = 0
        for pos, i in enumerate(self.letter_pos):
            if x < acumulacion+self.text.rect_text.left:
                return pos
            acumulacion += i
        else:
            return len(self.raw_text)

    def click(self, pos) -> None:

        if self.rect.collidepoint(pos): 
            self.typing = True
            if 'left' in self.dire:
                neg = self.pos.x
            elif 'center' in self.dire:
                neg = self.pos.x - self.rect.w/2
            elif 'right' in self.dire:
                neg = self.pos.x - self.rect.w
            self.typing_pos = self.check_pos_letter_click(pos[0]-neg-(self.padding.x)-self.text_size/3)
            self.typing_line = True
            self.typing_line_time = time.time()
        else:
            self.typing = False
            self.backspace = False
            self.typing_line = False
            self.typing_line_time = time.time()
            self.text.text = self.raw_text
        self.draw_surf()

    def add_letter(self, t) -> None:
        if len(self.raw_text) < self.max_letter:
            self.raw_text = self.raw_text[:self.typing_pos] + t + self.raw_text[self.typing_pos:]
            self.text.text = self.raw_text
            w = Text(self.raw_text[:self.typing_pos]+t,self.text_size, self.font, (0,0), padding=0).rect.w - sum(self.letter_pos[:self.typing_pos])
            self.letter_pos.insert(self.typing_pos,w)
            self.typing_pos += 1
            self.center_text()
        self.typing_line = True
        self.typing_line_time = time.time()

    def to_left(self) -> None:
        if not self.left_b:
            self.left_b = True
            self.left_time = time.time()
        self.typing_pos = max(0,self.typing_pos -1)
        self.typing_line = True
        self.typing_line_time = time.time()
        self.center_text()

    def center_text(self) -> None:
        suma = sum(self.letter_pos[:self.typing_pos+1])
        text_width = self.text.width
        surf_width = self.surf_rect.w

        if text_width <= surf_width:
            self.text.left = 0
        else:
            if suma - self.text.left > surf_width:
                self.text.left = -suma + surf_width - 1
            elif suma - self.text.left < 0:
                self.text.left = -suma-1
            else:
                # Ensure the cursor is visible within the surface 
                cursor_x = sum(self.letter_pos[:self.typing_pos])
                if cursor_x - self.text.left < 0:
                    self.text.left = -cursor_x-1
                elif cursor_x - self.text.left > surf_width:
                    self.text.left = -cursor_x + surf_width-1

        self.draw_surf()

    def to_right(self) -> None:
        if not self.right_b:
            self.right_b = True
            self.right_time = time.time()
        self.typing_pos = min(len(self.raw_text),self.typing_pos + 1)
        self.typing_line = True
        self.typing_line_time = time.time()
        self.center_text()
        

    def del_letter(self,dire=1) -> None:
        if not self.deleting:
            if dire == 1:
                self.backspace = True
            else:
                self.supr = True
            self.del_time = time.time()
            self.deleting = True
        if len(str(self.raw_text)) > 0:
            if (self.backspace and self.typing_pos == 0) or (self.supr and self.typing_pos == len(self.raw_text)):
                return
            if self.backspace:
                self.raw_text = self.raw_text[:self.typing_pos-1] + self.raw_text[self.typing_pos:]
                self.letter_pos.pop(self.typing_pos)
                self.typing_pos -= 1
                self.center_text()
            else: 
                self.raw_text = self.raw_text[:self.typing_pos] + self.raw_text[self.typing_pos+1:]
                self.letter_pos.pop(self.typing_pos+1)
                self.center_text()

            self.text.text = self.raw_text
        self.typing_line = True
        self.typing_line_time = time.time()
        self.draw_surf()

    def clear(self):
        self.letter_pos = [0]
        self.raw_text = ''
        self.typing_pos = 0
        self.typing_line = False
        self.typing_line_time = time.time()
        self.text.text = self.raw_text
        self.text.pos = (0,self.input_surface.get_height()/2)
        self.draw_surf()


    def set(self, text) -> None:
        'Cambiar el texto'
        self.clear()
        for x in f'{text}':
            self.add_letter(x)
        self.draw_surf()

    def get_text(self) -> str:
        return self.raw_text
    
    def __str__(self) -> str:
        return self.raw_text
