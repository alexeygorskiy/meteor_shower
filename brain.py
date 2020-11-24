import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from random import randint, uniform

class Brain:
    def __init__(self):
        self.mutation_rate = 15
        self.model = keras.Sequential(
            [
                layers.Dense(units=8, activation="tanh", bias_initializer="glorot_uniform"),
                layers.Dense(units=4, activation="tanh", bias_initializer="glorot_uniform"),
                layers.Dense(units=2, activation="tanh", bias_initializer="glorot_uniform"),
                #layers.Dense(units=8, activation="tanh"),
                #layers.Dense(units=4, activation="tanh"),
                #layers.Dense(units=2, activation="tanh"),
            ]
        )

    """
        given an array of ray_point_collisions (1x8), which indicates which points are colliding,
        returns a decisions array (1x2) describing in what direction to move
        decisions[0]: x
        decisions[1]: y
    """
    def make_decisions(self, ray_point_collisions):
        ray_point_collisions = np.reshape(ray_point_collisions, newshape=(1, 8))
        decisions = np.round(self.model(ray_point_collisions, training=False))
        return decisions



    """
        parent_weights: array of weights
    """

    def evolve(self, parent_weights):
        new_weights = self.model.get_weights()

        for layer in range(len(parent_weights[0])):  # loops through every weight layer
            # crossover
            parent = randint(0, len(parent_weights)-1)
            new_weights[layer] = parent_weights[parent][layer]

            if randint(0, 100) < self.mutation_rate:  # mutation
                new_weights[layer] += uniform(-0.5, 0.5)

        self.model.set_weights(new_weights)

    """
        swaps every weight layer of self for one of parents' weight layers in the same position.  
        also has a chance to mutate the whole weight layer by adding a uniform distribution to it 
    """
    """
    def evolve(self, parent1, parent2):
        parent1_weights = parent1.brain.model.get_weights()
        parent2_weights = parent2.brain.model.get_weights()

        for layer in range(0, len(parent1_weights)):
            if randint(0, 1):  # crossover
                parent1_weights[layer] = parent2_weights[layer]
            if randint(0, 100) < self.mutation_rate:  # mutation
                parent1_weights[layer] += uniform(-0.5, 0.5)

        self.model.set_weights(parent1_weights)
    """

    """
        swaps every individual weight in every weight layer of self for one of parents' weights in the 
        same position. also has a chance to mutate the individual weight by adding a uniform distribution to it 
    """
    """
    def evolve(self, parent1, parent2):
        parent1_weights = parent1.brain.model.get_weights()
        parent2_weights = parent2.brain.model.get_weights()

        for layer in range(0, len(parent1_weights)):
            for row in range(0, parent1_weights[layer].shape[0]):
                if (layer % 2) == 0:  # for non-bias weights
                    for col in range(0, parent1_weights[layer].shape[1]):
                        if randint(0, 1):  # crossover
                            parent1_weights[layer][row][col] = parent2_weights[layer][row][col]
                        if randint(0, 100) < self.mutation_rate:  # mutation
                            parent1_weights[layer][row][col] += uniform(-0.5, 0.5)

                else:  # for biases
                    if randint(0, 1):  # crossover
                        parent1_weights[layer][row] = parent2_weights[layer][row]
                    if randint(0, 100) < self.mutation_rate:  # mutation
                        parent1_weights[layer][row] += uniform(-0.5, 0.5)
        # bias layers only have rows so a different loop is used for
        # every odd layer, which is a bias layer to only loop through the rows

        self.model.set_weights(parent1_weights)
    """