import pyglet
from random import randint
from math import sqrt
import utils

class MeteorObject(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = 100
        self.x, self.y = utils.get_spawn_coords(self)
        self.dx, self.dy = self.calc_velocity_vector()
        self.corner_points = utils.get_corner_points(self)

    def calc_velocity_vector(self):
        dx = 400-self.x
        dy = 400-self.y
        sum = sqrt((abs(dx))^2 + (abs(dy))^2)

        if sum == 0:
            dx = randint(-400, 400)
            dy = randint(-400, 400)
            sum = sqrt((abs(dx)) ^ 2 + (abs(dy)) ^ 2)

        dx = dx * randint(1, 10) * self.speed / sum
        dy = dy * randint(1, 10) * self.speed / sum

        return dx, dy

    def move(self):
        self.x += self.dx/100
        self.y += self.dy/100

        for pt in self.corner_points:
            pt[0] += self.dx/100
            pt[1] += self.dy/100

    def update(self, dt):
        self.move()
        if utils.is_outside_map(self.x, self.y):
            self.reset()

    def reset(self):
        self.x, self.y = utils.get_spawn_coords(self)
        self.corner_points = utils.get_corner_points(self)
        self.dx, self.dy = self.calc_velocity_vector()

