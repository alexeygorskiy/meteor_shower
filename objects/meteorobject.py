import pyglet
import random
from utils import utils

class MeteorObject(pyglet.sprite.Sprite):
    def __init__(self, target_coords, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = 1.75  # movement limited to self.speed pixels in any direction, currently set to half spaceship speed
        self.x, self.y = utils.get_spawn_coords(self)
        self.target_coords = target_coords
        self.dx, self.dy = self.calc_velocity_vector()

        #### FOR THE QUADTREE ITEM IMPLEMENTATION ####
        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]
        ##############################################

    def calc_velocity_vector(self):
        target = random.choice(self.target_coords)

        dx = target[0]-self.x
        dy = target[1]-self.y
        sum = ((dx)**2 + (dy)**2)**(0.5)

        if sum == 0:    # spawned in the same coords as a spaceship
            dx = (400-self.x)
            dy = (400-self.y)
            sum = ((dx)**2 + (dy)**2)**(0.5)

        dx = (dx * self.speed) / sum
        dy = (dy * self.speed) / sum

        return dx, dy

    def move(self):
        self.x += self.dx
        self.y += self.dy

        for pt in self.corner_points:
            pt[0] += self.dx
            pt[1] += self.dy

        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]

    def update(self, dt, target_coords):
        self.move()
        if utils.is_outside_map(self.x, self.y):
            self.reset(target_coords=target_coords)

    def reset(self, target_coords):
        self.x, self.y = utils.get_spawn_coords(self)
        self.target_coords = target_coords
        self.dx, self.dy = self.calc_velocity_vector()

        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]

