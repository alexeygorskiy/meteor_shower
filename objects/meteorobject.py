import pyglet
from utils import utils

class MeteorObject(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x, self.y = utils.get_spawn_coords(self)
        #self.x, self.y = 400, 450
        self.eaten = False

        #### FOR THE QUADTREE ITEM IMPLEMENTATION ####
        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]
        ##############################################

    def update(self):
        if self.eaten:
            self.reset()

    def reset(self):
        self.x, self.y = utils.get_spawn_coords(self)

        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]

        self.eaten = False

