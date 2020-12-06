import pyglet
from random import randint
from math import sqrt

class MeteorObject(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = 1
        self.x, self.y = self.get_spawn_coords()
        self.dx, self.dy = self.calc_velocity_vector()

        self.corner_points = self.get_corner_points()


    def get_spawn_coords(self):
        area = randint(0,3)

        if area == 0:
            return randint(5, 795), 795
        elif area == 1:
            return 795, randint(5, 795)
        elif area == 2:
            return randint(5, 795), 5
        else:
            return 5, randint(5, 795)


    def calc_velocity_vector(self):
        dx = 400-self.x
        dy = 400-self.y
        sum = sqrt( (abs(dx))^2 + (abs(dy))^2 )

        if sum == 0:
            dx = randint(-400, 400)
            dy = randint(-400, 400)
            sum = sqrt((abs(dx)) ^ 2 + (abs(dy)) ^ 2)

        dx = dx * randint(1, 10) * self.speed / (sum*5)
        dy = dy * randint(1, 10) * self.speed / (sum*5)

        return dx, dy

    def move(self):
        self.x += self.dx/100
        self.y += self.dy/100

        for pt in self.corner_points:
            pt[0] += self.dx/100
            pt[1] += self.dy/100


    def is_outside_map(self):
        return not (0 <= self.x <= 800 and 0 <= self.y <= 800)

    def update(self, dt):
        self.move()

        if self.is_outside_map():
            self.reset()

    def get_corner_points(self):
        bottom_left = [self.x-(self.width/2), self.y-(self.height)/2]
        top_right = [self.x+(self.width/2), self.y+(self.height)/2]

        return [bottom_left, top_right]


    def reset(self):
        self.x, self.y = self.get_spawn_coords()
        self.corner_points = self.get_corner_points()
        self.dx, self.dy = self.calc_velocity_vector()

