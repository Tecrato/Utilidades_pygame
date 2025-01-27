import pygame as pag
from .Animaciones import Second_Order_Dinamics

class Screen_scroll:
    '''
    ## Scroll bar
    ### Other options:
        - color_hover
    '''
    def __init__(
            self, limit: int, inside_height: int = 1, visible: bool = True, min_bar_lenght: int = 10, bar_thickness: int = 10,
                 bar_orientation: str = 'vertical', color: tuple[int,int,int] = (255,255,255), smoth = True, **kwargs
        ) -> None:
        self.limit = limit
        self.visible = visible
        self.pos = pag.Vector2(0, 0)
        self.__desplazamiento = 0
        self.min_bar_lenght = min_bar_lenght
        self.inside_height = inside_height
        self.bar_length = 10
        self.bar_thickness = bar_thickness
        self.bar_active = True
        self.bar_orientation = bar_orientation
        self.color = color
        self.color_hover = kwargs.get('color_hover',(150,150,150,255))
        self.top = 0
        self.scroll = False
        self.redraw = 1
        self.hover = False
        self.rect = pag.Rect(0,0,0,0)
        self.last_rect = pag.Rect(0,0,0,0)
        self.set_bar_length()

        self.smoth = smoth
        self.smoth_movent = Second_Order_Dinamics(60, 1.5, 1, 1.5, 0)
        self.smoth_pos = 0

    def set_bar_length(self) -> None:
        if self.inside_height < self.limit:
            self.bar_active = False
            return
        
        self.bar_active = True
        if self.bar_orientation == 'vertical':
            self.rect.h = max(self.min_bar_lenght,self.limit * (self.limit / self.inside_height))
            self.bar_length = self.rect.h
            self.rect.w = self.bar_thickness
            self.rect.x = self.pos[0] - self.bar_thickness

    def rodar(self, y) -> None:
        if not self.bar_active:
            return
        self.desplazamiento += y

    def rodar_mouse(self, delta):
        try:
            self.top += delta
            self.desplazamiento = -((self.inside_height-self.limit) / ((self.limit - self.bar_length) / self.top))
        except ZeroDivisionError:
            pass

    def draw(self, surface) -> None:
        if not self.visible or not self.bar_active:
            return [] 
        self.redraw = 0
        pag.draw.rect(surface, self.color if not self.hover else self.color_hover, self.rect)
        r = self.last_rect.union(self.rect.copy()).copy()
        self.last_rect = self.rect.copy()
        return (self.rect,r)
    
    def click(self, pos):
        if self.bar_orientation == 'vertical' and self.rect.collidepoint(pos):
            self.scroll = True
            return True
        self.scroll = False
        return False

    def update(self, dt=1, pos=None, **kwargs) -> None:
        if self.smoth:
            self.smoth_pos = self.smoth_movent.update(self.__desplazamiento)[0]
            self.top = -(self.limit - self.bar_length) * (self.desplazamiento / (self.inside_height-self.limit))

        if self.bar_orientation == 'vertical' and int(self.top) != int(self.rect.top):
            # self.top = -(self.limit - self.bar_length) * (self.desplazamiento / (self.inside_height-self.limit))
            self.rect.top = self.top
            if self.redraw < 1:
                self.redraw += 1


    def update_hover(self, mouse_pos=(-10000,-1000)):
        if (self.rect.collidepoint(pag.Vector2(mouse_pos)) and self.bar_active and not self.hover and self.visible) or \
            (not self.rect.collidepoint(pag.Vector2(mouse_pos)) and self.bar_active and self.hover and self.visible):
            self.hover = not self.hover
            self.redraw += 1

    @property
    def inside_height(self):
        return self.__inside_height
    @inside_height.setter
    def inside_height(self, inside_height):
        self.__inside_height = inside_height
        if self.__inside_height <= 0:
            self.__inside_height = 1
        if self.inside_height < self.limit:
            self.desplazamiento = 0
        else:
            self.desplazamiento += 0
        self.set_bar_length()
    
    @property
    def desplazamiento(self):
        return self.__desplazamiento
    @desplazamiento.setter
    def desplazamiento(self,d):
        self.__desplazamiento = min(0, d)
        self.__desplazamiento = max(-(abs(self.inside_height-self.limit)), self.__desplazamiento)

        if self.inside_height < self.limit:
            self.__desplazamiento = 0

    @property
    def diff(self) -> float:
        return self.__desplazamiento if not self.smoth else self.smoth_pos
    
    def collide(self, rect: pag.Rect) -> bool:
        return self.rect.collidepoint(rect.center)
    