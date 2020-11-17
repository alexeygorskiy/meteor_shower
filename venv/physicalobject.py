import pyglet
import random
from pyglet.window import key
from brain import Brain

class PhysicalObject(pyglet.sprite.Sprite):

    def __init__(self, human_controlled=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.brain = Brain()

        self.human_controlled = human_controlled
        if human_controlled:
            self.key_handler = key.KeyStateHandler()

        self.dead = False
        self.sight = 10
        self.speed = 100

        self.collisions = [0,0,0,0,0,0,0,0]

        self.fitness = 0
        self.time_since_reward = 0
        self.next_gate = 0
        self.reward_gates = [
            # achieved, x bounds, y bounds
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

    def update_fitness(self):
        x_bounds = self.reward_gates[self.next_gate][0]
        y_bounds = self.reward_gates[self.next_gate][1]

        if x_bounds[0]<=self.x<=x_bounds[1] and y_bounds[0]<=self.y<=y_bounds[1]:
            self.fitness += 1
            self.time_since_reward = 0
            if self.next_gate == len(self.reward_gates)-1:
                self.next_gate = 0
                self.fitness += 9
            else:
                self.next_gate += 1

    def move_human(self, dt):
        constant = self.speed * dt

        if self.key_handler[key.LEFT]:
            self.x -= constant

        if self.key_handler[key.RIGHT]:
            self.x += constant

        if self.key_handler[key.UP]:
            self.y += constant

        if self.key_handler[key.DOWN]:
            self.y -= constant

    def move_ai(self, dt):
        constant = self.speed * dt
        decisions = self.brain.make_decisions(ray_points=self.collisions)

        if decisions[0][0] < 0:
            self.x -= constant
        elif decisions[0][0] > 0:
            self.x += constant

        if decisions[0][1] < 0:
            self.y -= constant
        elif decisions[0][1] > 0:
            self.y += constant

    def move(self, dt):
        if self.human_controlled:
            self.move_human(dt)
        else:
            self.move_ai(dt)

    def update(self, dt):
        if self.dead:
            return

        self.time_since_reward += 0.1

        self.update_raypoints()

        self.move(dt)

        if self.is_dead():
            self.dead = True
            self.fitness -= 100

        self.update_fitness()

    def is_point_colliding(self, point):
        if ( (100<=point[0]<=700 and 100<=point[1]<=700) or # inner wall
            (point[0]<=0) or    # left wall
            (800<=point[0]) or  # right wall
            (point[1]<=0) or       # bottom wall
            (800<=point[1])   # top wall
        ):
            return True
        else:
            return False

    def is_dead(self):
        pt1 = (self.x-(self.width/2), self.y+(self.height)/2)
        pt2 = (pt1[0]+self.width, pt1[1])
        pt3 = (pt2[0], pt2[1]-self.height)
        pt4 = (pt3[0]-self.width, pt3[1])

        corner_points = [pt1, pt2, pt3, pt4]

        for point in corner_points:
            if self.is_point_colliding(point) or self.time_since_reward >= 40:
                return True

        return False

    def update_raypoints(self):
        hw = (self.width/2)
        hh = (self.height/2)

        pt1 = (self.x-hw-self.sight, self.y)
        pt2 = (pt1[0], pt1[1]+hh+self.sight)

        pt3 = (self.x, self.y+hh+self.sight)
        pt4 = (pt3[0]+hw+self.sight, pt3[1])

        pt5 = (self.x+hw+self.sight, self.y)
        pt6 = (pt5[0], pt5[1]-hh-self.sight)

        pt7 = (self.x, self.y - hh - self.sight)
        pt8 = (pt7[0] - hw - self.sight, pt7[1])

        ray_points = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]

        colliding = []

        for point in ray_points:
            colliding.append(1 if self.is_point_colliding(point) else 0)

        self.collisions = colliding


