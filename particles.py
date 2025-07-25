import random
import time
from pygame.math import Vector2


from .particle import Particle

v_0 = Vector2(0,0)

class Particles:
    def __init__(
            self, spawn_pos, radio: int, color = (255,255,255), velocity=.1, gravity=0, angle = 0, radio_down: float = 0,
            vel_dispersion = 0, angle_dispersion = 0, radio_dispersion = 0, max_particles = 100, time_between_spawns = .1,
            max_distance = 1000, spawn_count = 1, random_color = False, auto_spawn: bool = True
        ) -> None:
        self.particles: list[Particle] = []
        self.spawn_pos = spawn_pos
        self.radio = radio
        self.color = color
        self.velocity = velocity
        self.__gravity = gravity
        self.radio_down = radio_down
        self.vel_dispersion = vel_dispersion
        self.angle_dispersion = angle_dispersion
        self.radio_dispersion = radio_dispersion
        self.max_particles = max_particles
        self.time_between_spawns = time_between_spawns
        self.angle = angle
        self.max_distance = max_distance
        self.spawn_count = spawn_count
        self.random_color = random_color
        self.auto_spawn = auto_spawn
        self.updates_rects = []
        self.redraw = 2
        self.use_mouse_motion = False
        self.use_wheel = False

        self.last_pos = 0
        self.last_time = time.time()



    def update(self, dt=1, **kwargs) -> None:
        for i,part in sorted(enumerate(self.particles),reverse=True):
            part.update(dt=dt)
            if self.radio_down > 0:
                part.radio -= self.radio_down
                if (part.radio-self.radio_down < 1):
                    self.particles.pop(i)
                    continue
            if  (part.pos-part.start_pos).length() > self.max_distance:
                self.particles.pop(i)
                continue
            if self.gravity > 0:
                v = Vector2(part.angle_cos*part.vel,part.angle_sin*part.vel+self.gravity)
                part.vel = v.length()
                part.angle = v_0.angle_to(v)
    
        if time.time() - self.last_time > self.time_between_spawns and len(self.particles) < self.max_particles and self.radio >= 1 and self.auto_spawn:
            self.spawn()
            return True


    def draw(self,surface):
        self.updates_rects.clear()
        for part in self.particles:
            for r in part.draw(surface):
                self.updates_rects.append(r)
        return self.updates_rects

    def spawn(self):
        for _ in range(min(self.spawn_count,self.max_particles-len(self.particles))):
            self.__add_particle()
        self.last_time = time.time()
        return True

    def __add_particle(self):
        vel = self.velocity + self.vel_dispersion * random.random()
        radio = self.radio + self.radio_dispersion * (random.random()*2 -1)
        angle = self.angle + (self.angle_dispersion * (random.random()*2 - 1) )
        color = self.color if not self.random_color else (random.randrange(0,255,50),random.randrange(0,255,50),random.randrange(0,255,50))
        particula = Particle(self.spawn_pos, radio, color, vel, angle)
        particula.start_pos = self.spawn_pos
        self.particles.append(particula)

    def clear(self):
        self.particles.clear()

    @property
    def gravity(self):
        return self.__gravity
    @gravity.setter
    def gravity(self,gravity):
        self.__gravity = float(gravity)
        if self.__gravity < 0:
            self.__gravity = 0

    def __len__(self):
        return len(self.particles)
    
    def collide(self, rect):
        return True
    def update_hover(self,*args, **kwargs):
        pass
    def is_hover(self,*args, **kwargs):
        pass
    def click(self,*args, **kwargs):
        return False