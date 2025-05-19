import pygame as pag
from .obj_Base import Base
from functools import lru_cache

from .constants import ALING_DIRECTION

@lru_cache(100)
def import_img(path):
    return pag.image.load_extended(path)

class Image(Base):
    def __init__(self,image,pos,dire: ALING_DIRECTION = 'center', size = None,color_key=(254,1,1), always_draw = False):
        super().__init__(pos,dire)
        self.__path: str = image
        self.__size = (int(size[0]),int(size[1])) if size else None
        self.color_key = color_key
        self.always_draw = always_draw


        self.cache = {}
        self.generate_img()

        self.direccion(self.rect)


    def generate_img(self):
        if not self.path:
            return
        if str(self.__size)+str(self.color_key) in self.cache:
            self.image: pag.Surface = self.cache[str(self.__size) + str(self.color_key)]
            self.rect = self.image.get_rect().copy()
            self.rect.center = self.pos
            self.direccion(self.rect)
            self.create_border(self.rect, 1)
            self.redraw += 3
            return


        surf = import_img(self.path)
        if self.__size:
            if surf.get_bitsize() > 24:
                surf = pag.transform.smoothscale(surf, self.__size)
            else:
                surf = pag.transform.scale(surf, self.__size)
        self.image = surf
        self.image.set_colorkey(self.color_key)

        self.rect = self.image.get_rect().copy()


        self.rect.center = self.pos
        self.direccion(self.rect)
        self.create_border(self.rect, 1)

        self.cache[str(self.__size) + str(self.color_key)] = self.image

        self.redraw += 3



    def draw(self,surface: pag.Surface, always_draw = False) -> list[pag.Rect]|None:
        if not self.path:
            return []
        if always_draw or self.always_draw:
            self.redraw += 2
        if self.redraw < 1:
            return []

        surface.blit(self.image,self.rect)

        if self.redraw < 1:
            return []
        if self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border, r]

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
        self.cache.clear()
        self.generate_img()