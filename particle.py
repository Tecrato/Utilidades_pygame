import pygame as pag
from pygame import Vector2
from Utilidades.optimize import memosize

@memosize
def radial(radius, startcolor, endcolor):
    print(str(radius),str(startcolor),str(endcolor))
    """
    Draws a linear raidal gradient on a square sized surface and returns
    that surface.
    """
    radius = int(radius)
    bigSurf = pag.Surface((2*radius, 2*radius), pag.SRCALPHA)
    bigSurf.fill((0,0,0,0))
    dd = -1.0/radius
    sr, sg, sb, sa = endcolor
    er, eg, eb, ea = startcolor
    rm = (er-sr)*dd
    gm = (eg-sg)*dd
    bm = (eb-sb)*dd
    am = (ea-sa)*dd
    
    draw_circle = pag.draw.circle
    for rad in range(radius, 0, -1):
        draw_circle(bigSurf, (er + int(rm*rad),
                              eg + int(gm*rad),
                              eb + int(bm*rad),
                              ea + int(am*rad)), (radius, radius), rad)
    return bigSurf

class Particle:
    def __init__(self, pos, radio: float, color=(255,255,255), velocidad=0, direccion=(0,0)):
        self.__pos = Vector2(pos)
        self.__radio = radio
        self.color = color
        self.vel = velocidad
        self.direccion = Vector2(direccion)
        self.surf = radial(int(self.radio), self.color+(255,), self.color+(0,))

    def draw(self,surface: pag.Surface):
        surface.blit(self.surf,(self.pos-(self.radio,self.radio)))

    def generate(self):
        self.surf = radial(int(self.radio), self.color+(255,), self.color+(0,))

    def update(self,dt=1):
        self.pos += self.direccion*self.vel*dt

    @property
    def pos(self) -> Vector2:
        return self.__pos
    @pos.setter
    def pos(self,pos):
        self.__pos = Vector2(pos)
    @property
    def radio(self) -> int:
        return self.__radio
    @radio.setter
    def radio(self,radio):
        self.__radio = float(radio)
        self.generate()

    @property
    def color(self) -> tuple[int,int,int]:
        return self.__color
    @color.setter
    def color(self,color):
        if len(color) == 3:
            color = color + (255,)
        self.__color = (int(color[0]),int(color[1]),int(color[2]))
        self.generate()
          
    @property
    def direccion(self) -> Vector2:
        return self.__direccion
    @direccion.setter
    def direccion(self,direccion):
        self.__direccion = Vector2(direccion)