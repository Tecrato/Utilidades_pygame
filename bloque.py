import pygame as pag
from pygame import Vector2

from Utilidades.maths import Hipotenuza
from .Animaciones import Curva_de_Bezier, Second_Order_Dinamics, Simple_acceleration
from .obj_Base import Base
from .scroll import Screen_scroll

from .texts import Text, Button, Input, List, Multi_list

class Bloque(Base):
    def __init__(self,pos,size,dire:str='center', background_color=(0,0,0,0), border_radius=0, border_width=-1, border_color=(0,0,0,0), scroll_y=1, scroll_x=1) -> None:
        super().__init__(pos,dire)

        self.surf = pag.Surface(size, pag.SRCALPHA)
        self.surf.fill((255, 0, 128))
        self.rect = self.surf.get_rect()
        self.create_border(self.rect, border_width)

        self.last_rect = self.rect.copy()

        self.background_color = background_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.border_color = border_color
        self.size = size
        self.index = -1

        self.updates = []

        self.list_objs: list[dict[str,Any]] = []
        self.scroll_class = Screen_scroll(self.rect.h)
        self.scroll_class.pos = (self.rect.w,0)
        self.actual_smoth_pos = 0
        self.pos = pos

    def add(self,clase, relative_pos, *, drawing: bool=True, clicking=False) -> int:
        """
        ## relative_pos examples:
         - (200,200)
         - (200,200*2)
         - (200*.01,200)
         - pag.Vector2(200,200)
         - pag.Vector2(self.rect.size)*.4
         - (self.rect.w*.1,self.rect.h*.4)
        """
        self.list_objs.append({"GUI":clase,"pos":relative_pos,"drawing":drawing,"clicking":clicking, "index":self.index})
        # self.list_objs[-1]["GUI"].pos = pag.Vector2(eval(f"{self.list_objs[-1]["pos"]}"))+(0,self.scroll_class.diff)
        setattr(self.list_objs[-1]["GUI"],"bloque_index",int("{i}".format(i=self.index)))
        setattr(self.list_objs[-1]["GUI"],"move",lambda *args, **kwargs: self.move(*args, index=self.list_objs[-1]["GUI"].bloque_index, **kwargs))
        # self.scroll_class.inside_height = max([x['GUI'].bottom+10 for x in self.list_objs])
        self.index += 1
        self.move_objs()
        return len(self.list_objs)-1
    
    def move(self, pos, index):
        self.list_objs[index]["pos"] = pos
        self.move_objs()

    def clear(self):
        self.list_objs.clear()
        self.scroll_class.inside_height = 1


    def click(self,pos):
        pos = Vector2(pos)
        if not self.rect.collidepoint(pos):
            return False
        if self.scroll_class.click(pos-self.topleft):
            return True
        for x in self.list_objs:
            if not x["clicking"]:
                continue
            if x["GUI"].click(pos-self.topleft):
                self.redraw += 1
                return True
        return True
    
    def draw(self, surface) -> list[pag.Rect]:
        self.surf.fill(self.background_color)
            
        if self.redraw > 0:
            for x in self.list_objs:
                if x['GUI'].redraw < 1:
                    x['GUI'].redraw = 1

        self.updates.clear()
        for i,x in sorted(enumerate(self.list_objs),reverse=False):
            if not x['drawing']:
                continue
            r = x['GUI'].draw(self.surf)
            for s in r:
                s.center = self.topleft + s.center
                self.updates.append(s)
            for y in r:
                for p in self.list_objs[i+1:]:
                    if p['GUI'].collide(y):
                        p['GUI'].redraw = 1
        self.scroll_class.draw(self.surf)
        surface.blit(self.surf, self.rect)
        pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius)
        if self.redraw < 1:
            return self.updates
        elif self.redraw < 2:
            self.redraw = 0
            return [self.rect_border]
        else:
            self.redraw = 0
            r = self.last_rect.union(self.rect_border.copy()).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border, r]
        return []


    def update(self, pos=None, dt=1, mouse_pos=(-100000,-100000)):
        
        self.scroll_class.update()
        
        if self.actual_smoth_pos != int(self.scroll_class.diff):
            self.actual_smoth_pos = int(self.scroll_class.diff)
            print(self.actual_smoth_pos)
            self.move_objs()

        for x in self.list_objs:
            x["GUI"].update(mouse_pos=Vector2(mouse_pos)-self.topleft)
            if x["GUI"].redraw > 0 and self.redraw < 1:
                self.redraw = 1
        
        return super().update(pos)
    
    def move_objs(self):
        for x in self.list_objs:
            x["GUI"].pos = pag.Vector2(eval(f"{x['pos']}"))+(0,self.scroll_class.diff)
        self.scroll_class.inside_height = max([eval(f"{x['pos']}")[1]+x["GUI"].height for x in self.list_objs])
        self.scroll_class.rodar(0)
        if self.redraw < 1:
            self.redraw = 1

    def rodar_mouse(self, delta):
        self.scroll_class.rodar_mouse(delta)
        self.move_objs()
        if self.redraw < 1:
            self.redraw += 1
        
    def rodar(self, delta):
        self.scroll_class.rodar(delta)
        self.move_objs()
        if self.redraw < 1:
            self.redraw += 1

    @property
    def scroll(self):
        return self.scroll_class.scroll
    @scroll.setter
    def scroll(self,scroll):
        self.scroll_class.scroll = scroll