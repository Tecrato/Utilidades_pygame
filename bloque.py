import pygame as pag
import Utilidades as uti

from pygame import Vector2
from typing import Any
from .obj_Base import Base
from .scroll import Screen_scroll
from .constants import ALING_DIRECTION

class Bloque(Base):
    def __init__(self,pos,size,dire: ALING_DIRECTION ='center', background_color=(0,0,0,0), border_radius=0, border_width=-1, border_color=(0,0,0,0), scroll_y=True, scroll_x=True) -> None:
        self.scroll_y = False
        self.scroll_x = False
        self.list_objs: list[dict[str,Any]] = []
        super().__init__(pos,dire)
        self.scroll_y: bool = scroll_y
        self.scroll_x: bool = scroll_x

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
        self.__scroll = False
        self.__use_mouse_motion = False
        self.use_mouse_wheel = True
        self.scroll_item = -1
        self.last_mouse_pos = pag.Vector2(0)
        self.cursor = None

        self.updates = []


        self.scroll_class = Screen_scroll(self.rect.h)
        self.scroll_class.pos = (self.rect.w,0)
        self.scroll_class_x = Screen_scroll(self.rect.w, bar_orientation='horizontal')
        self.scroll_class_x.pos = (0,self.rect.h)

        self.actual_smoth_pos = 0
        self.actual_smoth_pos_x = 0
        self.pos = pos
        

    def draw_before(self): ...
    def draw_after(self): ...

    def add(self,clase, relative_pos, *, drawing: bool=True, clicking=False) -> int:
        """
        ## relative_pos ejemplos:
         - (200,200)
         - (200,200*2)
         - (200*.01,200)
         - pag.Vector2(200,200)
         - pag.Vector2(self.rect.size)*.4
         - (self.rect.w*.1,self.rect.h*.4)
        """
        self.list_objs.append({"GUI":clase,"pos":relative_pos,"drawing":drawing,"clicking":clicking, "index":self.index})
        setattr(self.list_objs[-1]["GUI"],"bloque_index",int("{i}".format(i=self.index)))
        setattr(self.list_objs[-1]["GUI"],"move",lambda pos,index=self.list_objs[-1]["GUI"].bloque_index: self.move(pos=pos, index=index))
        self.index += 1
        self.move_objs()
        return len(self.list_objs)-1
    
    def move(self, pos, index):
        self.list_objs[index]["pos"] = str(pos)
        self.move_objs()

    def clear(self):
        self.list_objs.clear()
        self.scroll_class.inside_height = 1
        self.scroll_class_x.inside_height = 1


    def click(self,pos):
        self.scroll_item = -1
        pos = Vector2(pos)
        if not self.rect.collidepoint(pos):
            return False
        if self.scroll_class.click(pos-self.topleft) and self.scroll_y:
            if self.scroll_class.use_mouse_motion:
                self.use_mouse_motion = True
                self.scroll_class.use_mouse_motion = True
            return True
        if self.scroll_class_x.click(pos-self.topleft) and self.scroll_x:
            if self.scroll_class_x.use_mouse_motion:
                self.use_mouse_motion = True
                self.scroll_class_x.use_mouse_motion = True
            return True
        for i,x in sorted(enumerate(self.list_objs), reverse=True):
            if not x["clicking"]:
                continue
            if (r :=x["GUI"].click(pos-self.topleft)):
                self.redraw += 1
                if x["GUI"].use_mouse_motion:
                    self.use_mouse_motion = True
                    self.scroll_item = i
                return r if r is not None else True
        return False
    
    def draw(self, surface) -> list[pag.Rect]:
        if self.redraw < 2:
            return []
        
        
        # if self.redraw > 1:
        self.surf.fill(self.background_color)
        for x in self.list_objs:
            # if x['GUI'].redraw < 1:
            x['GUI'].redraw += 2
        if self.scroll_y:
            self.scroll_class.redraw += 1
        if self.scroll_x:
            self.scroll_class_x.redraw += 1
        
        self.updates.clear()
        self.draw_before()

        for i,x in sorted(enumerate(self.list_objs),reverse=False):
            h = self.rect.copy()
            h.topleft = (0,0)
            if not x['drawing'] or not x["GUI"].collide(h):
                continue
            re = x["GUI"].redraw
            r = x['GUI'].draw(self.surf)
            for s in r:
                # pag.draw.rect(self.surf, self.background_color, s)
                k = s.copy()
                k.center += self.topleft
                self.updates.append(k)

        # for i,x in sorted(enumerate(self.list_objs),reverse=False):
        #     h = self.rect.copy()
        #     h.topleft = (0,0)
        #     if not x['drawing'] or not x["GUI"].collide(h):
        #         continue
        #     re = x["GUI"].redraw
        #     r = x['GUI'].draw(self.surf)
        #     for s in r:
        #         k = s.copy()
        #         k.center += self.topleft
        #         self.updates.append(k)
        #     for y in r:
        #         for p in self.list_objs[i+1:]:
        #             if p['GUI'].collide(y) and p['GUI'].redraw < 1:
        #                 p['GUI'].redraw += 1
        #     if re < 2:
        #         continue
        #     for y in r:
        #         for p in self.list_objs[:i]:
        #             if p['GUI'].collide(y) and p['GUI'].redraw < 1:
        #                 p['GUI'].redraw += 1
        
        if self.scroll_y and (p := self.scroll_class.draw(self.surf)):
            for l in p:
                k = l.copy()
                k.center += self.topleft
                self.updates.append(k)
        if self.scroll_x and (p := self.scroll_class_x.draw(self.surf)):
            for l in p:
                k: pag.Rect = l.copy()
                k.center += self.topleft
                self.updates.append(k)

        self.draw_after()


        surface.blit(self.surf, self.rect)
        pag.draw.rect(surface, self.border_color, self.rect_border, self.border_width,self.border_radius)
        # if self.redraw < 2:
        #     self.redraw = 2
            # return self.updates
        # else:
        #     self.redraw = 2
        #     # print(self.redraw)
        #     # self.redraw = 2
        #     # return self.updates
        r = self.last_rect.union(self.rect_border.copy()).copy()
        self.last_rect = self.rect_border.copy()
        return [self.rect_border, r]


    def update(self, pos=None, **kwargs):
        self.scroll_class.update()
        self.scroll_class_x.update()
        if self.scroll_y and self.scroll_class.redraw > 3 and self.scroll_class.visible and self.scroll_class.bar_active:
            self.redraw += 1
        if self.scroll_x and self.scroll_class_x.redraw > 3 and self.scroll_class_x.visible and self.scroll_class_x.bar_active:
            self.redraw += 1

        if self.scroll_y and self.actual_smoth_pos != int(self.scroll_class.diff):
            self.actual_smoth_pos = int(self.scroll_class.diff)
            self.move_objs()
        if self.scroll_x and self.actual_smoth_pos_x != int(self.scroll_class_x.diff):
            self.actual_smoth_pos_x = int(self.scroll_class_x.diff)
            self.move_objs()

        for x in self.list_objs:
            x["GUI"].update()
        
        return super().update(pos)

    def update_hover(self, mouse_pos=(-100000,-100000)):
        self.last_mouse_pos = pag.Vector2(mouse_pos)
        if self.use_mouse_motion:
            return True
        self.scroll_class.update_hover(mouse_pos=pag.Vector2(mouse_pos)-self.topleft)
        self.scroll_class_x.update_hover(mouse_pos=pag.Vector2(mouse_pos)-self.topleft)
        cursor_setted = False
        for i,x in sorted(enumerate(self.list_objs), reverse=True):
            x["GUI"].update_hover(mouse_pos=Vector2(mouse_pos)-self.topleft)
            # if x['GUI'].hover and not cursor_setted and x['GUI'].cursor:
            if x['GUI'].is_hover(Vector2(mouse_pos)-self.topleft) and not cursor_setted and getattr(x['GUI'],'cursor',None):
                cursor_setted = True
                self.cursor = x['GUI'].cursor
                self.hover = True
        if not cursor_setted:
            self.hover = False
            self.cursor = None
            return False
        return True

    
    def move_objs(self):
        for x in self.list_objs:
            diff = (
                self.scroll_class_x.diff if self.scroll_x else 0,
                self.scroll_class.diff if self.scroll_y else 0,
            )
            x["GUI"].pos = pag.Vector2(eval(f"{x['pos']}"))+diff
        if not self.scroll_y:
            return
        if not self.scroll_x:
            return

        pos = []
        for i,x in enumerate(self.list_objs):
            sup_pos = list(eval(f"{x['pos']}"))
            pos.append(sup_pos)
            if 'left' in x["GUI"].dire:
                pos[-1][0] += x["GUI"].width
            elif 'right'in x["GUI"].dire:
                pass
            else:
                pos[-1][0] += x["GUI"].width//2
            
            if 'top' in x["GUI"].dire:
                pos[-1][1] += x["GUI"].height
            elif 'bottom' in x["GUI"].dire:
                pass
            else:
                pos[-1][1] += x["GUI"].height//2

        self.scroll_class.inside_height = max([x[1] for x in pos])
        self.scroll_class.rodar(0)
        self.scroll_class_x.inside_height = max([x[0] for x in pos])
        self.scroll_class_x.rodar(0)

    def on_mouse_motion(self, evento):
        if not self.list_objs:
            return
        if isinstance(evento, tuple):
            diff: tuple[int,int] = evento
        else:
            diff: tuple[int,int] = evento.rel
        if self.scroll_item >= 0:
            self.list_objs[self.scroll_item]["GUI"].on_mouse_motion(diff)
        elif self.scroll_y and self.scroll_class.use_mouse_motion:
            self.scroll_class.on_mouse_motion(diff[1])
            self.move_objs()
        elif self.scroll_x and self.scroll_class_x.use_mouse_motion:
            self.scroll_class_x.on_mouse_motion(diff[0])
            self.move_objs()
        
    def on_wheel(self, delta):
        if not self.list_objs:
            return
        for i,x in enumerate(self.list_objs):
            if getattr(x["GUI"],"use_mouse_wheel",False) and x["GUI"].is_hover(self.last_mouse_pos-self.topleft):
                x["GUI"].on_wheel(delta)
                return
        if self.scroll_y or self.scroll_x:
            dez_y = int(self.scroll_class.desplazamiento)
            self.scroll_class.rodar(delta)
            if self.scroll_class.desplazamiento == dez_y and self.scroll_x:
                self.scroll_class_x.rodar(delta)
            self.move_objs()

    @property
    def use_mouse_motion(self):
        return self.__use_mouse_motion
    @use_mouse_motion.setter
    def use_mouse_motion(self,use_mouse_motion):
        self.__use_mouse_motion = use_mouse_motion
        if self.scroll_y:
            self.scroll_class.use_mouse_motion = False
        if self.scroll_x:
            self.scroll_class_x.use_mouse_motion = False
        for x in self.list_objs:
            x["GUI"].use_mouse_motion = False

    @property
    def height(self):
        return self.rect.h
    @property
    def width(self):
        return self.rect.w
    
    def collide(self, rect):
        for x in self.list_objs:
            r = rect.copy()
            r.move_ip(-self.topleft[0],-self.topleft[1])
            if x["GUI"].collide(r):
                # x["GUI"].redraw += 1
                return True
        return False