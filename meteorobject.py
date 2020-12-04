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

        dx = dx * randint(1, 10) * self.speed / (sum*5)
        dy = dy * randint(1, 10) * self.speed / (sum*5)

        return dx, dy

    def move(self):
        self.x += self.dx/100
        self.y += self.dy/100


    def is_outside_map(self):
        return not (0 <= self.x <= 800 and 0 <= self.y <= 800)

    def update(self, dt):
        self.move()

        if self.is_outside_map():
            self.reset()



    """
        :returns an array of all the corners points ath the current coordinates (self.x, self.y)
    """
    def get_corner_points(self):
        pt1 = [self.x-(self.width/2), self.y+(self.height)/2]
        pt2 = [pt1[0]+self.width, pt1[1]]
        pt3 = [pt2[0], pt2[1]-self.height]
        pt4 = [pt3[0]-self.width, pt3[1]]

        return [pt1, pt2, pt3, pt4]

    def reset(self):
        self.x, self.y = self.get_spawn_coords()
        self.corner_points = self.get_corner_points()
        self.dx, self.dy = self.calc_velocity_vector()

