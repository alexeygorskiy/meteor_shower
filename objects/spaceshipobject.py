import pyglet
from pyglet.window import key
from utils import utils

class SpaceshipObject(pyglet.sprite.Sprite):
    def __init__(self, human_controlled=False, termination_fitness=1600, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
            --------------   NOTE:   --------------
            EVERY TIME YOU ADD A NEW VARIABLE HERE
            MAKE SURE TO RESET IT IN reset() IF
            APPLICABLE!!!
            ---------------------------------------
        """
        self.human_controlled = human_controlled
        if human_controlled:
            self.key_handler = key.KeyStateHandler()


        self.sight = 7
        self.speed = self.sight/2   # can move within half of its sight radius

        self.food_reward = 100
        self.survival_time_without_reward = 100
        self.termination_fitness = termination_fitness

        # state
        # always zeros, so make sure to set (self.x, self.y) to somewhere where there is no initial collisions
        self.x, self.y = utils.get_spawn_coords(self)
        self.dead = False
        self.fitness = 0
        self.visible = True
        self.ray_points = utils.get_raypoints(self)
        self.corner_points = utils.get_corner_points(self)
        self.time_since_reward = 0

    def reset(self):
        self.x, self.y = utils.get_spawn_coords(self)
        self.dead = False
        self.fitness = 0
        self.visible = True
        self.ray_points = utils.get_raypoints(self)
        self.corner_points = utils.get_corner_points(self)
        self.time_since_reward = 0


    """
        method for moving self using the keyboard keys
    """
    def move_human(self):
        if self.key_handler[key.LEFT]:
            dx = self.speed * -1
        elif self.key_handler[key.RIGHT]:
            dx = self.speed
        else:
            dx = 0

        if self.key_handler[key.UP]:
            dy = self.speed
        elif self.key_handler[key.DOWN]:
            dy = self.speed * -1
        else:
            dy = 0

        self.x += dx
        self.y += dy


    """
        method for moving self using its neural net
    """
    def move_ai(self, action):
        dx = 1 if action[0] >= 0.5 else -1
        dy = 1 if action[1] >= 0.5 else -1

        sum = ((dx)**2 + (dy)**2)**(0.5)

        if sum == 0:
            return

        dx = (dx/sum) * self.speed
        dy = (dy/sum) * self.speed

        self.x += dx
        self.y += dy

        for point in self.ray_points:
            point[0] += dx
            point[1] += dy

        for point in self.corner_points:
            point[0] += dx
            point[1] += dy


    def update_fitness(self):
        self.time_since_reward = 0
        self.fitness += self.food_reward


    def move(self, action):
        if self.human_controlled:
            self.move_human()
        else:
            self.move_ai(action=action)

    def update(self, action):
        self.move(action=action)

        self.time_since_reward += 1

        if utils.is_outside_map(self.corner_points[0][0], self.corner_points[0][1]) \
                or utils.is_outside_map(self.corner_points[1][0], self.corner_points[1][1]) \
                or self.time_since_reward >= self.survival_time_without_reward \
                or self.fitness >= self.termination_fitness:
            self.dead = True
            self.visible = False
            return