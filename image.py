import pygame as pag
from .obj_Base import Base
from functools import lru_cache
# from io import BytesIO

@lru_cache(100)
def import_img(path):
    return pag.image.load(path)

class Image(Base):
    def __init__(self,image,pos,direccion: str = 'center', size = None,color_key=(254,1,1), dir=[1,0],vel=0, always_draw = False):
        super().__init__(pos,direccion)
        self.path: str = image
        self.__size = (int(size[0]),int(size[1])) if size else None
        self.color_key = color_key
        self.always_draw = always_draw

        self.raw_image = self.path

        self.cache = {}
        self.generate_img()

        if vel:
            self.simple_acceleration_move(vel,dir,'forward')

        self.direccion(self.rect)


    def generate_img(self):
        if str(self.__size)+str(self.color_key) in self.cache:
            self.image: pag.Surface = self.cache[str(self.__size) + str(self.color_key)]
            self.rect = self.image.get_rect().copy()
            self.rect.center = self.pos
            self.direccion(self.rect)
            return

        # if self.__size:
        #     im = self.raw_image.resize((int(self.__size[0]), int(self.__size[1])))
        # else:
        #     im = self.raw_image

        # img_bytes = BytesIO()
        # im.save(img_bytes,'PNG')
        # img_bytes.seek(0)
        # self.image = pag.image.load(img_bytes)
        self.image = pag.transform.smoothscale(import_img(self.raw_image), self.__size) if self.__size else import_img(self.raw_image)
        # self.surf = pag.Surface(self.image.get_size(), pag.SRCALPHA)

        # self.surf.fill(self.color_key)
        # self.surf.set_colorkey(self.color_key)
        # self.surf.blit(self.image,(0,0))
        self.rect = self.image.get_rect().copy()


        self.rect.center = self.pos
        self.direccion(self.rect)
        self.create_border(self.rect, 1)

        self.cache[str(self.__size) + str(self.color_key)] = self.image



    def draw(self,surface: pag.Surface, always_draw = False) -> list[pag.Rect]|None:
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