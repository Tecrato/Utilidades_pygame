import pygame as pag
from pygame import Vector2

class Particle:
    def __init__(self, pos, radio: int, color=[255,255,255], direccion=[1,0], vel=0) -> None:
        self.__pos = Vector2(pos)
        self.__radio = radio
        self.__color: tuple[int] = color
        self.direccion = direccion
        self.vel = vel
        self.surf = pag.Surface

    def draw(self,surface):
        surface.blit(self.surf,(self.pos-(self.radio,self.radio)))

    def generate(self):
        self.surf = pag.Surface((self.radio*2,self.radio*2), pag.SRCALPHA)
        matriz_colores = []
        for y in range(self.radio*2):
            fila = []
            for x in range(self.radio*2):
                distancia = Vector2(Vector2(x,y)-Vector2(self.radio,self.radio)).length() / self.radio
                color = (
                        self.lighting_color[0] * (1-distancia),
                        self.lighting_color[1] * (1-distancia),
                        self.lighting_color[2] * (1-distancia),
                        self.lighting_color[3] * (1-distancia),
                    )
                fila.append(color if color[0] > 1 else (0,0,0,0))
            matriz_colores.append(fila)
        
        for y in range(self.radio*2):
            for x in range(self.radio*2):
                self.surf.set_at((x,y),matriz_colores[y][x])

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
        self.__radio = int(radio)
        self.generate()

    @property
    def color(self) -> tuple[int]:
        return self.__color
    @color.setter
    def color(self,color):
        self.__color = color
        self.generate()
          