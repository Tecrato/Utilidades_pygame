import pygame as pag
from math import pi, cos, sin, atan2
from pygame.math import Vector2

class Spark():
	def __init__(self, surface, loc, angle, speed, color, scale=1):
		self.surface = surface
		self.loc = Vector2(loc)
		self.angle = angle
		self.speed = speed
		self.scale = scale
		self.color = color
		self.alive = True

	def point_towards(self, angle, rate):
		rotate_direction = ((angle - self.angle + pi * 3) % (pi * 2)) - pi
		try:
			rotate_sign = -rotate_direction / rotate_direction
		except ZeroDivisionError:
			rotate_sing = 1
		if abs(rotate_direction) < rate:
			self.angle = angle
		else:
			self.angle += rate * rotate_sign

	def calculate_movement(self, dt):
		return [cos(self.angle) * self.speed * dt, sin(self.angle) * self.speed * dt]


    # gravity and friction
	def velocity_adjust(self, friction, force, terminal_velocity, dt):
		movement = self.calculate_movement(dt)
		movement[1] = min(terminal_velocity, movement[1] + force * dt)
		movement[0] *= friction
		self.angle = atan2(movement[1], movement[0])
		self.angle = self.angle % (2 * pi)
        # if you want to get more realistic, the speed should be adjusted here

	def move(self, dt):
		movement = self.calculate_movement(dt)
		movement
		self.loc[0] += movement[0]
		self.loc[1] += movement[1]

        # a bunch of options to mess around with relating to angles...
		# self.point_towards(numpy.pi / 2, 0.12)
		# self.velocity_adjust(0.995, .3, 8, dt)
		# self.angle += 0.1

		self.speed -= 0.1

		if self.speed <= 0:
			self.alive = False

	def draw(self, surf, offset=[0, 0]):
		if self.alive:
			points = (
				(self.loc[0] + cos(self.angle) * self.speed * self.scale, self.loc[1] + sin(self.angle) * self.speed * self.scale),
				(self.loc[0] + cos(self.angle + pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + sin(self.angle + pi / 2) * self.speed * self.scale * 0.3),
				(self.loc[0] - cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - sin(self.angle) * self.speed * self.scale * 3.5),
				(self.loc[0] + cos(self.angle - pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - sin(self.angle + pi / 2) * self.speed * self.scale * 0.3),
			)
			pag.draw.polygon(self.surface, self.color, points)