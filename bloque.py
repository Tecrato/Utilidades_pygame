import pygame as pag
import Utilidades as uti

from pygame import Vector2
from typing import Any
from .obj_Base import Base
from .scroll import Screen_scroll
from .constants import ALIGN_DIRECTION

def _unir_rects(rects: list[pag.Rect]) -> list[pag.Rect]:
    """Une los rectángulos que se solapan o se tocan, para no repintar dos veces."""
    pendientes = [r.copy() for r in rects]
    unidos: list[pag.Rect] = []
    while pendientes:
        actual = pendientes.pop()
        cambio = True
        while cambio:
            cambio = False
            for otro in pendientes[:]:
                if actual.inflate(2, 2).colliderect(otro):
                    actual.union_ip(otro)
                    pendientes.remove(otro)
                    cambio = True
        unidos.append(actual)
    return unidos


class Bloque(Base):
    def __init__(
            self,pos,size,dire: ALIGN_DIRECTION ='center', background_color=(0,0,0,0), border_radius=0, 
            border_width=-1, border_color=(0,0,0,0), scroll_y=True, scroll_x=True, func_to_hover=None, func_out_hover=None
            ) -> None:
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
        self.hover_to_func = True
        self.func_to_hover = func_to_hover
        self.func_out_hover = func_out_hover

        self.updates = []


        self.scroll_class = Screen_scroll(self.rect.h)
        self.scroll_class.pos = (self.rect.w,0)
        self.scroll_class_x = Screen_scroll(self.rect.w, bar_orientation='horizontal')
        self.scroll_class_x.pos = (0,self.rect.h)

        self.actual_smooth_pos = 0
        self.actual_smooth_pos_x = 0
        self.__last_scroll = None
        self.pos = pos
        

    def draw_before(self): ...
    def draw_after(self): ...

    def add(self,clase, *, drawing: bool=True, clicking=False) -> int:
        self.list_objs.append({"GUI":clase,"drawing":drawing,"clicking":clicking, "index":self.index})
        self.index += 1
        self.move_objs()
        self.redraw = max(self.redraw, 1)      # hay un hijo nuevo que pintar
        return len(self.list_objs)-1

    def clear(self):
        self.list_objs.clear()
        self.scroll_class.inside_height = 1
        self.scroll_class_x.inside_height = 1
        self.redraw = max(self.redraw, 1)      # quedan huecos que limpiar


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
    
    def draw(self, surface, diff_pos = (0,0)) -> list[pag.Rect]:
        """Pinta solo lo sucio y recorta los hijos al tamaño del bloque.

        Los hijos viven en coordenadas de *contenido* (sin scroll) y se dibujan
        desplazados por `diff`; el viewport es (0, 0, ancho, alto). La superficie
        propia hace de caché: solo se rellena y se repintan las zonas sucias.
        """
        view = pag.Rect(0, 0, self.rect.w, self.rect.h)
        diff = (
            self.scroll_class_x.diff if self.scroll_x else 0,
            self.scroll_class.diff if self.scroll_y else 0,
        )

        # ---- 1) qué trozos del viewport hay que repintar ----
        repintar_todo = self.redraw >= 1 or diff != self.__last_scroll
        self.__last_scroll = diff

        if repintar_todo:
            sucios = [view.copy()]
        else:
            sucios = []
            for x in self.list_objs:
                gui = x["GUI"]
                if not x["drawing"] or gui.redraw < 1:
                    continue
                r = gui.collide_rect.union(gui.last_rect).move(diff).clip(view)
                if r.w > 0 and r.h > 0:
                    sucios.append(r)
            for barra, activa in ((self.scroll_class, self.scroll_y),
                                  (self.scroll_class_x, self.scroll_x)):
                if activa and barra.redraw > 0:
                    r = barra.last_rect.union(barra.rect).clip(view)
                    if r.w > 0 and r.h > 0:
                        sucios.append(r)

        if not sucios:
            return []

        # ---- 2) repintar solo esas zonas de la superficie propia ----
        self.updates.clear()
        self.draw_before()

        for region in _unir_rects(sucios):
            self.surf.set_clip(region)
            self.surf.fill(self.background_color, region)

            for x in self.list_objs:
                gui = x["GUI"]
                if not x["drawing"] or not getattr(gui, "visible", True):
                    continue
                area = gui.collide_rect.union(gui.last_rect).move(diff)
                if not area.colliderect(region):
                    if not area.colliderect(view):
                        gui.redraw = 0      # fuera del cuadro: ni se dibuja ni queda sucio
                    continue
                if gui.redraw < 2:
                    gui.redraw = 2          # lo que hubiera debajo también se repinta
                gui.draw(self.surf, diff_pos=diff)

            if self.scroll_y and self.scroll_class.rect.colliderect(region):
                self.scroll_class.redraw = max(self.scroll_class.redraw, 1)
                self.scroll_class.draw(self.surf)
            if self.scroll_x and self.scroll_class_x.rect.colliderect(region):
                self.scroll_class_x.redraw = max(self.scroll_class_x.redraw, 1)
                self.scroll_class_x.draw(self.surf)

            self.surf.set_clip(None)

            superficie = (self.rect.x + diff_pos[0] + region.x,
                          self.rect.y + diff_pos[1] + region.y)
            surface.blit(self.surf, superficie, area=region)
            self.updates.append(region.move(self.rect.topleft).move(diff_pos))

        # el borde va sobre la ventana: su mitad exterior no cabe en self.surf
        pag.draw.rect(surface, self.border_color, self.rect_border.move(diff_pos),
                      self.border_width, self.border_radius)

        self.draw_after()
        self.redraw = 0

        if repintar_todo:
            r = self.last_rect.union(self.rect_border).copy()
            self.last_rect = self.rect_border.copy()
            return [self.rect_border.move(diff_pos), r.move(diff_pos)]
        return self.updates


    def update(self, pos=None, dt=1, mouse_pos=(-10000, -10000), **kwargs):
        self.scroll_class.update(dt=dt)
        self.scroll_class_x.update(dt=dt)
        if self.scroll_y and self.scroll_class.redraw > 3 and self.scroll_class.visible and self.scroll_class.bar_active:
            self.redraw += 1
        if self.scroll_x and self.scroll_class_x.redraw > 3 and self.scroll_class_x.visible and self.scroll_class_x.bar_active:
            self.redraw += 1

        if self.scroll_y and self.actual_smooth_pos != int(self.scroll_class.diff):
            self.actual_smooth_pos = int(self.scroll_class.diff)
            self.move_objs()
        if self.scroll_x and self.actual_smooth_pos_x != int(self.scroll_class_x.diff):
            self.actual_smooth_pos_x = int(self.scroll_class_x.diff)
            self.move_objs()

        for x in self.list_objs:
            x["GUI"].update(dt=dt, mouse_pos=mouse_pos)
        
        return super().update(pos, dt=dt)

    def update_hover(self, mouse_pos=(-100000,-100000)):
        self.last_mouse_pos = pag.Vector2(mouse_pos)
        if self.rect.collidepoint(self.last_mouse_pos) and not self.hover_to_func and self.func_to_hover:
            self.hover_to_func = True
            self.func_to_hover()
        elif not self.rect.collidepoint(self.last_mouse_pos) and self.hover_to_func and self.func_out_hover:
            self.hover_to_func = False
            self.func_out_hover()
        if self.use_mouse_motion:
            return True
        # overflow: hidden tambien para el raton; fuera del cuadro no hay hover
        dentro = self.rect.collidepoint(self.last_mouse_pos)
        local = (self.last_mouse_pos - self.topleft) if dentro else pag.Vector2(-100000, -100000)
        contenido = local - (self.scroll_class_x.diff if self.scroll_x else 0,
                             self.scroll_class.diff if self.scroll_y else 0)
        self.scroll_class.update_hover(mouse_pos=local)
        self.scroll_class_x.update_hover(mouse_pos=local)
        cursor_setted = False
        for i,x in sorted(enumerate(self.list_objs), reverse=True):
            x["GUI"].update_hover(mouse_pos=contenido)
            # if x['GUI'].hover and not cursor_setted and x['GUI'].cursor:
            if x['GUI'].is_hover(contenido) and not cursor_setted and getattr(x['GUI'],'cursor',None):
                cursor_setted = True
                self.cursor = x['GUI'].cursor
                self.hover = True
        if not cursor_setted:
            self.hover = False
            self.cursor = None
            return False
        return True

    
    def move_objs(self):
        """Recalcula el tamaño del contenido de cada eje, por separado.

        Antes salía en cuanto uno de los dos scrolls estaba apagado, así que con
        scroll vertical solo el `inside_height` se quedaba en 1 y la barra no
        aparecía nunca.
        """
        if not self.list_objs:
            return

        ancho = 0
        alto = 0
        for x in self.list_objs:
            gui = x["GUI"]
            pos = gui.pos.copy()
            if 'left' in gui.dire:
                pos[0] += gui.width
            elif 'right' in gui.dire:
                pass
            else:
                pos[0] += gui.width // 2

            if 'top' in gui.dire:
                pos[1] += gui.height
            elif 'bottom' in gui.dire:
                pass
            else:
                pos[1] += gui.height // 2

            ancho = max(ancho, pos[0])
            alto = max(alto, pos[1])

        if self.scroll_y:
            self.scroll_class.inside_height = alto
            self.scroll_class.rodar(0)
        if self.scroll_x:
            self.scroll_class_x.inside_height = ancho
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
            return False
        for i,x in enumerate(self.list_objs):
            if x["GUI"].on_wheel(delta):
                return True
        if not self.scroll_class.bar_active and not self.scroll_class_x.bar_active:
            return False
        if self.scroll_y or self.scroll_x:
            dez_y = int(self.scroll_class.desplazamiento)
            self.scroll_class.rodar(delta)
            if self.scroll_class.desplazamiento == dez_y and self.scroll_x:
                self.scroll_class_x.rodar(delta)
            self.move_objs()
            return True
        return False

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
        """El bloque ocupa su propia caja: los hijos van recortados dentro."""
        return self.rect.colliderect(rect) or self.last_rect.colliderect(rect)

    