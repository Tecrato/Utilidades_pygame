import pygame as pag
from pygame import Vector2

from .Animaciones import Curva_de_Bezier, Second_Order_Dinamics, Simple_acceleration
from .obj_Base import Base

from .texts import Text, Button, Input, List, Multi_list

class Bloque(Base):
    def __init__(self,pos,size,dire:str='center', background_color=None,color_key=(255, 0, 128), border_radius=0) -> None:
        super().__init__(pos,dire)

        self.surf = pag.Surface(size)
        self.surf.fill((255, 0, 128))
        self.surf.set_colorkey(color_key)
        self.rect = self.surf.get_rect()

        self.color_key = color_key
        self.background_color = background_color
        self.border_radius = border_radius

        self.redraw = True

        self.list_objs: list[dict] = []

    def add(self,clase, relative_pos, *, drawing=True, clicking=False):
        """
        ## relative_pos examples:
         - (200,200)
         - (200,200*2)
         - (200*.01,200)
         - pag.Vector2(200,200)
         - pag.Vector2(self.rect.size)*.4
         - (self.rect.w*.1,self.rect.h*.4)
        """
        self.list_objs.append({"GUI":clase,"pos":relative_pos,"drawing":drawing,"clicking":clicking})
        self.list_objs[-1]["GUI"].pos = eval(f"{self.list_objs[-1]["pos"]}")

        return self

    def clear(self):
        self.list_objs.clear()

    def move_objs(self):
        for x in self.list_objs:
            x["GUI"].pos = eval(f"{x['pos']}")

    def click(self,pos):
        pos = Vector2(pos)
        if not self.rect.collidepoint(pos):
            return
        pos = pos-self.topleft
        for x in self.list_objs:
            if not x["clicking"]:
                continue
            if x["GUI"].click(pos):
                self.redraw = True
                return True
        return False
    def draw(self, surf,pos=(-500,-500)):
        mx, my = Vector2(pos)-self.topleft
        # if self.redraw:
        self.surf.fill(self.color_key)

        for x in self.list_objs:
            if not x["drawing"]:
                continue
            if isinstance(x["GUI"], Button):
                x["GUI"].draw(self.surf, (mx,my))
            elif isinstance(x["GUI"], Multi_list):
                if x["GUI"].listas[0].lista_palabras:
                    x["GUI"].draw(self.surf)
            # elif isinstance(x["GUI"], Text):
            #     x["GUI"].draw(self.surf) if self.redraw else None
            else:
                x["GUI"].draw(self.surf)
        self.redraw = False

        surf.blit(self.surf, self.rect)
        return self.rect

    def update(self, pos=None):
        for x in self.list_objs:
            x["GUI"].update(pos)
        return super().update(pos)