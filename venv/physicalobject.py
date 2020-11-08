import pyglet
import math
import numpy as np
from pyglet.window import key

class PhysicalObject(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity_x, self.velocity_y, self.rotation = 0.0, 0.0, 180

        # Set some easy-to-tweak constants
        self.thrust = 300.0
        self.rotate_speed = 200.0

        # edge points
        self.pt1 = np.array((self.position[0], self.position[1]+self.height/2))
        self.pt2 = np.array((self.position[0]+self.width/2, self.position[1]))
        self.pt3 = np.array((self.position[0], self.position[1]-self.height/2))
        self.pt4 = np.array((self.position[0]-self.width/2, self.position[1]))
        self.update_edges()

        self.edge_points = [self.pt1, self.pt2, self.pt3, self.pt4]

        self.key_handler = key.KeyStateHandler()


    def check_bounds(self):
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = 800 + self.image.width / 2
        max_y = 600 + self.image.height / 2
        if self.x < min_x:
            self.x = max_x
        elif self.x > max_x:
            self.x = min_x
        if self.y < min_y:
            self.y = max_y
        elif self.y > max_y:
            self.y = min_y

    def update_edges(self):
        theta = -np.radians(self.rotation)

        r = np.array(((np.cos(theta), -np.sin(theta)),
                      (np.sin(theta), np.cos(theta))))

        self.pt1 = abs(r.dot(self.pt1))
        self.pt2 = abs(r.dot(self.pt2))
        self.pt3 = abs(r.dot(self.pt3))
        self.pt4 = abs(r.dot(self.pt4))

    def update(self, dt):

        if self.key_handler[key.LEFT]:
            self.rotation -= self.rotate_speed * dt
        if self.key_handler[key.RIGHT]:
            self.rotation += self.rotate_speed * dt

        if self.key_handler[key.UP]:
            angle_radians = math.radians(self.rotation)
            self.x += 100 * dt * math.sin(angle_radians)
            self.y += 100 * dt * math.cos(angle_radians)

        if self.key_handler[key.DOWN]:
            angle_radians = math.radians(self.rotation)
            self.x += -100 * dt * math.sin(angle_radians)
            self.y += -100 * dt * math.cos(angle_radians)

        self.update_edges()
        self.check_bounds()


    def collides_with(self, other_object):
        return True

    def handle_collision_with(self, other_object):
        self.opacity = 100


