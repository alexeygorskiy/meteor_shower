import pyglet
from pyglet.window import key
from brain import Brain
from random import randint

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

        self.x, self.y = self.get_spawn_coords()

        self.human_controlled = human_controlled
        if human_controlled:
            self.key_handler = key.KeyStateHandler()

        self.brain = Brain()

        # properties
        self.sight = 8
        self.speed = 1

        # rewards and fitness
        self.fitness = 0

        # smaller than the reward of a gate so that those that get a reward and die
        # are considered better than those that choose to not get the reward and not die

        # added every time update is called as long as self.dead is False
        # doesn't seem to work that great from empirical observations, so keep it at 0
        self.alive_reward = 0.1
        self.movement_award = 0.05

        # state
        # always zeros, so make sure to set (self.x, self.y) to somewhere where there is no initial collisions
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.dead = False
        self.ray_points = self.get_raypoints()


    def get_spawn_coords(self):
        return randint(60,740), randint(60,740)


    def reset(self):
        self.dead = False
        self.fitness = 0
        self.x, self.y = self.get_spawn_coords()
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.visible = True
        self.ray_points = self.get_raypoints()

    """
        check if self is within the bounds of a reward gate and if so add
        the corresponding reward. when a lap is finished resets the next_gate index.
        also adds the alive_reward every time the method is called and reset self.time_since_reward
        when a gate is reached
    """
    def update_fitness(self):
        self.fitness += self.alive_reward

    """
        method for moving self using the keyboard keys
    """
    def move_human(self):
        constant = int(self.speed)

        if self.key_handler[key.LEFT]:
            dx = constant * -1
        elif self.key_handler[key.RIGHT]:
            dx = constant
        else:
            dx = 0

        if self.key_handler[key.UP]:
            dy = constant
        elif self.key_handler[key.DOWN]:
            dy = constant * -1
        else:
            dy = 0

        self.x += dx
        self.y += dy

        for point in self.corner_points:
            point[0] += dx
            point[1] += dy



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
        constant = int(self.speed)
        dx = constant*decisions[0][0]
        dy = constant*decisions[0][1]

        self.x += dx
        self.y += dy

        for point in self.ray_points:
            point[0] += dx
            point[1] += dy

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

        self.update_fitness()

        if self.is_outside_map():
            self.dead = True
            self.visible = False

    def is_outside_map(self):
        return not (0 <= self.x <= 800 and 0 <= self.y <= 800)

    """
        :returns an array of all the raypoints at the current coordinates (self.x, self.y)
    """
    def get_raypoints(self):
        hw = (self.width/2)
        hh = (self.height/2)

        pt1 = [self.x-hw-self.sight, self.y]
        pt2 = [pt1[0], pt1[1]+hh+self.sight]

        pt3 = [self.x, self.y+hh+self.sight]
        pt4 = [pt3[0]+hw+self.sight, pt3[1]]

        pt5 = [self.x+hw+self.sight, self.y]
        pt6 = [pt5[0], pt5[1]-hh-self.sight]

        pt7 = [self.x, self.y - hh - self.sight]
        pt8 = [pt7[0] - hw - self.sight, pt7[1]]

        return [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]

