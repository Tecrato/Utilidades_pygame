import pygame as pag
import random
import time
import math
from pygame.math import Vector2

from .particle import Particle
from Utilidades import Angulo, Hipotenuza

def apply_gravity(part):
    angle = Angulo((0,0),part.direccion)
    v = Vector2(math.cos(math.radians(angle))*part.vel,math.sin(math.radians(angle))*part.vel)
    v.y += part.gravity*dt
    part.vel = Hipotenuza((0,0),v)
    part.direccion = v.normalize()

class Particles:
    def __init__(
            self, spawn_pos, radio: int, color = (255,255,255), velocity=.1, gravity=0, direccion = (0,1), radio_down: float = 0,
            vel_dispersion = 0, angle_dispersion = 0, radio_dispersion = 0, max_particles = 100, time_between_spawns = .1,
            max_distance = 1000, spawn_count = 1, random_color = False
        ) -> None:
        self.particles: list[Particle] = []
        self.spawn_pos = spawn_pos
        self.radio = radio
        self.color = color
        self.velocity = velocity
        self.gravity = gravity
        self.radio_down = radio_down
        self.vel_dispersion = vel_dispersion
        self.angle_dispersion = angle_dispersion
        self.radio_dispersion = radio_dispersion
        self.max_particles = max_particles
        self.time_between_spawns = time_between_spawns
        self.direccion = direccion
        self.max_distance = max_distance
        self.spawn_count = spawn_count
        self.random_color = random_color

        self.last_pos = 0
        self.last_time = time.time()

    def update(self, dt = 1) -> None:
        if time.time() - self.last_time > self.time_between_spawns and len(self.particles) < self.max_particles and self.radio >= 1:
            for _ in range(self.spawn_count):
                self.__add_particle()
            self.last_time = time.time()

        for i,part in sorted(enumerate(self.particles),reverse=True):
            part.update(dt)
            part.radio -= self.radio_down
            if part.radio-self.radio_down < 1:
                self.particles.pop(i)
                continue
            if self.gravity > 0:
                angle = Angulo((0,0),part.direccion)
                v = Vector2(math.cos(math.radians(angle))*part.vel,math.sin(math.radians(angle))*part.vel)
                v.y += self.gravity*dt
                part.vel = Hipotenuza((0,0),v)
                part.direccion = v.normalize()
            if Hipotenuza(part.pos, part.start_pos) > self.max_distance:
                self.particles.pop(i)
            
    def draw(self,surface):
        for part in self.particles:
            part.draw(surface)

    def __add_particle(self):
        vel = self.velocity + self.vel_dispersion * random.uniform(0, 1)
        radio = self.radio + self.radio_dispersion * random.uniform(-1, 1)
        direccion = Angulo((0,0),self.direccion) + self.angle_dispersion * random.uniform(-1, 1)
        direccion = Vector2(math.cos(math.radians(direccion)),math.sin(math.radians(direccion))).normalize()
        color = self.color if not self.random_color else (random.randrange(0,255,50),random.randrange(0,255,50),random.randrange(0,255,50))
        particula = Particle(self.spawn_pos, radio, color, vel, direccion)
        particula.start_pos = self.spawn_pos
        self.particles.append(particula)

    def clear(self):
        self.particles.clear()

    def __len__(self):
        return len(self.particles)