import pygame as pag
from .Animaciones import Second_Order_Dinamics

class Screen_scroll:
    def __init__(
            self, limit: int, inside_height: int = 1, visible: bool = True, min_bar_lenght: int = 10, bar_thickness: int = 10,
                 bar_orientation: str = 'vertical', color: tuple[int,int,int] = (255,255,255), smoth = True
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
        self.top = 0
        self.scroll = False
        self.redraw = 1
        self.set_bar_length()

        self.smoth = smoth
        self.smoth_movent = Second_Order_Dinamics(60, 1.5, 1, 1.5, 0)
        self.smoth_pos = 0

    def set_bar_length(self) -> None:
        if self.inside_height < self.limit:
            self.bar_active = False
            return
        
        self.bar_active = True
        self.bar_length = max(self.min_bar_lenght,self.limit * (self.limit / self.inside_height))

    def rodar(self, y) -> None:
        if not self.bar_active:
            return
        self.desplazamiento += y

    def rodar_mouse(self, delta):
        self.desplazamiento = -(self.inside_height / ((self.limit - self.bar_length) / (-(self.limit - self.bar_length) * (self.desplazamiento / self.inside_height) + delta)))

    def draw(self, surface) -> None:
        if not self.visible:
            return False
        if not self.bar_active:
            return False
        if self.bar_orientation == 'vertical':
            r = pag.Rect(self.pos[0]-self.bar_thickness, self.pos[1]+self.top, self.bar_thickness, self.bar_length)
        pag.draw.rect(surface, self.color, r)
        return True
    
    def click(self, pos):
        if self.bar_orientation == 'vertical' and \
            pag.Rect(self.pos[0]-self.bar_thickness, self.pos[1]+self.top, self.bar_thickness, self.bar_length).collidepoint(pos):
            self.scroll = True
            return True
        self.scroll = False
        return False

    def update(self, dt=1, pos=None, **kwargs) -> None:
        if self.bar_orientation == 'vertical':
            self.top = -(self.limit - self.bar_length) * (self.desplazamiento / (self.inside_height-self.limit))
        if self.smoth:
            self.smoth_pos = self.smoth_movent.update(self.__desplazamiento)[0]
            return True

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