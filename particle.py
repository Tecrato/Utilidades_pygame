import pygame as pag, math
from pygame import Vector2
from functools import lru_cache

@lru_cache(maxsize=100_000)
def radial(radius, startcolor, endcolor):
    # print(str(radius),str(startcolor),str(endcolor))
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
    __slots__ = ["__pos", "__radio", "__color", "vel", "__angle", "angle_rad", "angle_sin", "angle_cos", "last_rect", "rect", "image", "start_pos"]
    def __init__(self, pos, radio: float, color=(255,255,255), velocidad=0, angle: float=0):
        self.__pos = Vector2(pos)
        self.start_pos = Vector2(pos)
        self.__radio = radio
        self.__color = color
        self.vel = velocidad
        self.__angle = float(angle)
        self.angle_rad = math.radians(angle)
        self.angle_sin = math.sin(self.angle_rad)
        self.angle_cos = math.cos(self.angle_rad)
        self.last_rect = pag.Rect(0,0,0,0)
        self.rect = pag.Rect(0,0,0,0)
        self.generate()

    def draw(self,surface: pag.Surface):
        if self.rect.colliderect(surface.get_rect()):
            surface.blit(self.image,self.rect)
        r = self.last_rect.copy()
        self.last_rect = self.rect.copy()
        return (self.rect,r)

    def generate(self):
        if self.radio > 1:
            self.image = radial(int(self.radio), self.color+(255,), self.color+(0,))
            self.rect = self.image.get_rect(center=self.pos)

    def update(self,dt=1):
        self.__pos += (self.angle_cos*self.vel*2*dt,self.angle_sin*self.vel*2*dt)
        self.rect.center = self.__pos

    @property
    def pos(self) -> Vector2:
        return self.__pos
    @pos.setter
    def pos(self,pos):
        if isinstance(pos, Vector2):
            self.__pos = pos
            return
        self.__pos = Vector2(pos)
    @property
    def radio(self) -> int:
        return self.__radio
    @radio.setter
    def radio(self,radio):
        if self.radio == radio:
            return
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
    def angle(self) -> Vector2:
        return self.__angle
    @angle.setter
    def angle(self,angle):
        self.__angle = float(angle)
        self.angle_rad = math.radians(angle)
        self.angle_sin = math.sin(self.angle_rad)
        self.angle_cos = math.cos(self.angle_rad)