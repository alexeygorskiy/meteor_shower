import pyglet
from pyglet.window import key
from brain import Brain

class PhysicalObject(pyglet.sprite.Sprite):

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

        # properties
        self.sight = 10
        self.speed = 200

        # rewards and fitness
        self.fitness = 0
        self.survival_time_without_reward = 15

        self.death_punishment = 50
        # smaller than the reward of a gate so that those that get a reward and die
        # are considered better than those that choose to not get the reward and not die

        # added every time update is called as long as self.dead is False
        # doesn't seem to work that great from empirical observations, so keep it at 0
        self.alive_reward = 0

        self.gate_reward = 100
        self.lap_reward = 10000

        # state
        # always zeros, so make sure to set (self.x, self.y) to somewhere where there is no initial collisions
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]

        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.time_since_reward = 0
        self.dead = False
        self.ray_points = self.get_raypoints()
        self.corner_points = self.get_corner_points()

        # reward gates
        self.next_gate = 0  # index to keep track of the next reward gate (prevents skipping of reward gates)
        self.reward_gates = [
            # [(x bounds), (y bounds)]
            [(0,100), (100,110)],
            [(0,100), (200,210)],
            [(0,100), (400,410)],
            [(0,100), (700,710)],

            [(100,110), (700, 800)],
            [(200,210), (700, 800)],
            [(400,410), (700, 800)],
            [(700,710), (700, 800)],

            [(700, 800), (690, 700)],
            [(700, 800), (390, 400)],
            [(700, 800), (190, 200)],
            [(700, 800), (90, 100)],

            [(690, 700), (0, 100)],
            [(390, 400), (0, 100)],
            [(190, 200), (0, 100)],
            [(90, 100), (0, 100)],
        ]

    def reset(self):
        self.dead = False
        self.time_since_reward = 0
        self.fitness = 0
        self.next_gate = 0
        self.x = 50
        self.y = 50
        self.collisions = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_collisions = self.collisions
        self.last_decisions = self.brain.make_decisions(ray_point_collisions=self.collisions)
        self.visible = True
        self.ray_points = self.get_raypoints()
        self.corner_points = self.get_corner_points()

    """
        check if self is within the bounds of a reward gate and if so add
        the corresponding reward. when a lap is finished resets the next_gate index.
        also adds the alive_reward every time the method is called and reset self.time_since_reward
        when a gate is reached
    """
    def update_fitness(self):
        x_bounds = self.reward_gates[self.next_gate][0]
        y_bounds = self.reward_gates[self.next_gate][1]
        self.fitness += self.alive_reward

        if x_bounds[0] <= self.x <= x_bounds[1] and y_bounds[0] <= self.y <= y_bounds[1]:
            self.fitness += self.gate_reward
            self.time_since_reward = 0

            # if lap complete reset next_gate index
            if self.next_gate == len(self.reward_gates)-1:
                self.next_gate = 0
                self.fitness += self.lap_reward
            else:
                self.next_gate += 1

    """
        method for moving self using the keyboard keys
    """
    def move_human(self, dt):
        constant = int(self.speed * dt)

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
    def move_ai(self, dt):
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
        constant = int(self.speed * dt)
        dx = constant*decisions[0][0]
        dy = constant*decisions[0][1]

        self.x += dx
        self.y += dy

        for point in self.ray_points:
            point[0] += dx
            point[1] += dy

        for point in self.corner_points:
            point[0] += dx
            point[1] += dy



    def move(self, dt):
        if self.human_controlled:
            self.move_human(dt)
        else:
            self.move_ai(dt)

    def update(self, dt):
        if self.dead:
            return

        self.time_since_reward += dt*3

        self.update_raypoint_collisions()

        self.move(dt)

        # if they die by hitting a wall, they get punished
        if self.is_dead():
            self.dead = True
            self.fitness -= self.death_punishment
            self.visible = False

        # if they haven't received any rewards in a long time they still die, but without punishment
        elif self.time_since_reward >= self.survival_time_without_reward:
            self.dead = True
            self.visible = False

        # called one last time if they have died so that if they managed to
        # reach a reward as they died they still get the reward
        self.update_fitness()


    """
        returns true if the point is overlapping with the inner wall or the game window
        (this is hardcoded for the current map and window size)
        point[0]: x
        point[1]: y
    """
    def is_point_colliding(self, point):
        if ( (100 <= point[0] <= 700 and 100 <= point[1] <= 700) or # inner wall
            (point[0] <= 0) or    # left wall
            (800 <= point[0]) or  # right wall
            (point[1] <= 0) or       # bottom wall
            (800 <= point[1])   # top wall
        ):
            return True
        else:
            return False

    """
        :returns an array of all the corners points ath the current coordinates (self.x, self.y)
    """
    def get_corner_points(self):
        pt1 = [self.x-(self.width/2), self.y+(self.height)/2]
        pt2 = [pt1[0]+self.width, pt1[1]]
        pt3 = [pt2[0], pt2[1]-self.height]
        pt4 = [pt3[0]-self.width, pt3[1]]

        return [pt1, pt2, pt3, pt4]

    """
        returns true if one of the corners of self are colliding
    """
    def is_dead(self):
        for point in self.corner_points:
            if self.is_point_colliding(point):
                return True

        return False


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

    """
        updates self.collisions array based on raypoint collision
        1: collision detected 
        0: collision not detected
    """
    def update_raypoint_collisions(self):
        colliding = []
        for point in self.ray_points:
            colliding.append(1 if self.is_point_colliding(point) else 0)

        # keep track of the last collision state to compare whether new decisions need to be made
        self.last_collisions = self.collisions  # save the last collision state
        self.collisions = colliding     # update the current collision state


