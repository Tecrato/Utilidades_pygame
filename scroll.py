import pygame as pag

class Screen_scroll:
    def __init__(
            self, limit: int, inside_height: int = 1, visible: bool = True, min_bar_lenght: int = 10, bar_thickness: int = 10,
                 bar_orientation: str = 'vertical', color: tuple[int,int,int] = (255,255,255)
        ) -> None:
        self.limit = limit
        self.inside_height = inside_height
        self.visible = visible
        self.pos = pag.Vector2(0, 0)
        self.desplazamiento = 0
        self.bar_length = 10
        self.bar_thickness = bar_thickness
        self.bar_active = True
        self.min_bar_lenght = min_bar_lenght
        self.bar_orientation = bar_orientation
        self.color = color
        self.top = 0
        self.scroll = False
        self.set_bar_length()

    def set_bar_length(self) -> None:
        if self.limit >= self.inside_height:
            self.bar_active = False
            return
        self.bar_active = True
        self.bar_length = max(self.min_bar_lenght,self.limit * (self.limit / (self.inside_height+self.limit)))
        self.rodar(0)

    def rodar(self, y) -> None:
        self.desplazamiento += y
        self.desplazamiento = min(0, self.desplazamiento)
        self.desplazamiento = max(-self.inside_height, self.desplazamiento)
        if self.bar_orientation == 'vertical':
            self.top = -(self.limit - self.bar_length) * (self.desplazamiento / self.inside_height)

    def rodar_mouse(self, delta):
        self.top += delta
        if self.top <= 0:
            self.top = 0
            self.desplazamiento = 0
            self.rodar(0)
            return
        self.desplazamiento = -(self.inside_height / ((self.limit - self.bar_length) / self.top))
        self.rodar(0)

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

    def update(self, pos=None) -> None:
        ...

    @property
    def inside_height(self):
        return self.__inside_height
    @inside_height.setter
    def inside_height(self, inside_height):
        self.__inside_height = inside_height - self.limit
        if self.__inside_height <= 0:
            self.__inside_height = 1
        self.set_bar_length()