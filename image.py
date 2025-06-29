import pygame as pag
from pathlib import Path, WindowsPath
from Utilidades.win32_tools import extract_icon

from .obj_Base import Base
from functools import lru_cache

from .constants import ALING_DIRECTION

@lru_cache
def import_img(path) -> pag.Surface:
    return pag.image.load_extended(path)

class Image(Base):
    def __init__(
            self,image: bytes|pag.Surface,pos,dire: ALING_DIRECTION = 'center', size = None,color_key=(254,1,1), 
            always_draw = False, border_width = -1, border_color = (0,0,0,0), border_radius = 0,
            angle = 0,
            **kwargs):
        super().__init__(pos,dire, **kwargs)
        self.__path: str = image
        self.__size = (int(size[0]),int(size[1])) if size else None
        self.color_key = color_key
        self.always_draw = always_draw
        self.border_width = border_width
        self.border_color = border_color
        self.border_radius = border_radius
        self.__angle = angle


        self.cache = {}
        self.generate_img()


    def generate_img(self):
        if not self.path:
            return
        elif isinstance(self.path,pag.Surface):
            self.image = self.path
            if self.__size:
                self.image = pag.transform.scale(self.image, self.__size)
            if self.__angle:
                self.image = pag.transform.rotate(self.image, self.__angle)
        else:
            if isinstance(self.path,(str,Path,WindowsPath)):
                self.image = import_img(self.path)
            elif isinstance(self.path,bytes):
                self.image = pag.image.frombytes(self.path, (self.__size[0],self.__size[1]), "BGRA", False)
            else:
                raise TypeError('Path must be a string or a pygame.Surface')
            if self.__size:
                if self.image.get_bitsize() > 24:
                    self.image = pag.transform.smoothscale(self.image, self.__size)
                else:
                    self.image = pag.transform.scale(self.image, self.__size)
            if self.__angle:
                self.image = pag.transform.rotate(self.image, self.__angle)


        self.rect = self.image.get_rect()


        self.rect.center = self.pos
        self.direccion(self.rect)
        self.create_border(self.rect, self.border_width)

        self.redraw += 3



    def draw(self,surface: pag.Surface, always_draw = False, diff_pos= (0,0)) -> list[pag.Rect]|None:
        if not self.path:
            return []
        if always_draw or self.always_draw:
            self.redraw += 2
        if self.redraw < 1:
            return []

        if self.border_width > -1:
            pag.draw.rect(surface, self.border_color, self.rect_border.move(diff_pos), self.border_width,self.border_radius)
        surface.blit(self.image,self.rect.move(diff_pos))

        if self.redraw < 1:
            return []
        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border.move(diff_pos), r.move(diff_pos)]

    @property
    def size(self):
        return self.__size
    @size.setter
    def size(self,size):
        self.__size = (int(size[0]),int(size[1]))
        self.generate_img()

    @property
    def height(self):
        return self.image.get_height()
    @property
    def width(self):
        return self.image.get_width()

    @property
    def path(self):
        return self.__path
    @path.setter
    def path(self,path):
        self.__path = path
        self.generate_img()

    @property
    def angle(self):
        return self.__angle
    @angle.setter
    def angle(self,angle):
        self.__angle = angle % 360
        self.generate_img()

        
def from_exe(path):
    b = extract_icon(path)
    surf: pag.Surface = pag.image.frombytes(b, (32,32), "BGRA", False)
    return Image(surf,(0,0),'center')