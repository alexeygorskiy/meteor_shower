import pyglet
from pyglet.window import key
from brain import Brain
import utils

class SpaceshipObject(pyglet.sprite.Sprite):

    def __init__(self, human_controlled=False, *args, **kwargs):
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
        self.brain = Brain()

        self.sight = 8
        self.speed = 1

        # added every time update is called as long as self.dead is False
        self.alive_reward = 0.1
        # added every time update is called if the spaceship moves
        self.movement_award = 0.05


        # state
        # always zeros, so make sure to set (self.x, self.y) to somewhere where there is no initial collisions
        self.x, self.y = utils.get_spawn_coords(self)
        self.dead = False
        self.fitness = 0
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.visible = True
        self.ray_points = utils.get_raypoints(self)

        #### FOR THE QUADTREE ITEM IMPLEMENTATION ####
        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]
        # The variable names don't make sense but I don't
        # want to rummage through the QuadTree implementation
        ##############################################

    def reset(self):
        self.x, self.y = utils.get_spawn_coords(self)
        self.dead = False
        self.fitness = 0
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.visible = True
        self.ray_points = utils.get_raypoints(self)

        # QUADTREE
        self.corner_points = utils.get_corner_points(self)
        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]

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
    def move_ai(self):
        # if the collision state hasn't changed, use the decisions from the last update.
        # self.collisions is updated by update_raypoint_collisions(), which is called before this method
        if self.collisions == self.last_collisions:
            decisions = self.last_decisions
        else:   # if the the collision state has changed, make new decisions and make that the most recent decision
            decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
            self.last_decisions = decisions

        # decisions: {-1,0,1}
        # decisions[0][0]: x
        # decisions[0][1]: y
        dx = self.speed*decisions[0][0]
        dy = self.speed*decisions[0][1]

        self.x += dx
        self.y += dy

        for point in self.ray_points:
            point[0] += dx
            point[1] += dy

        for point in self.corner_points:
            point[0] += dx
            point[1] += dy

        self.left = self.corner_points[0][0]
        self.bottom = self.corner_points[0][1]
        self.right = self.corner_points[1][0]
        self.top = self.corner_points[1][1]

        self.fitness += self.alive_reward
        if dx != 0 or dy != 0:
            self.fitness += self.movement_award

    def move(self):
        if self.human_controlled:
            self.move_human()
        else:
            self.move_ai()

    def update(self, dt):
        if self.dead:
            return

        self.move()

        if utils.is_outside_map(self.x, self.y):
            self.dead = True
            self.visible = False

