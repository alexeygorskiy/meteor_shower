import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from random import randint, uniform

class Brain:
    def __init__(self):
        self.mutation_rate = 15
        self.decision_multiplier = 100
        self.model = keras.Sequential(
            [
                layers.Dense(units=8, activation="relu", bias_initializer="RandomUniformV2"),
                layers.Dense(units=4, activation="relu", bias_initializer="RandomUniformV2"),
                layers.Dense(units=2, activation="tanh", bias_initializer="RandomUniformV2"),
            ]
        )

    def make_decisions(self, ray_points):
        ray_points = np.reshape(ray_points, newshape=(1, 8))
        decisions = np.round(self.model(ray_points, training=False) * self.decision_multiplier)
        return decisions

    def evolve(self, parent1, parent2):
        parent1_weights = parent1.brain.model.get_weights()
        parent2_weights = parent2.brain.model.get_weights()

        for layer in range(0, len(parent1_weights)):
            for row in range(0, parent1_weights[layer].shape[0]):
                if (layer % 2) == 0:  # for non-bias weights
                    for col in range(0, parent1_weights[layer].shape[1]):
                        if randint(0, 1):  # crossover
                            parent1_weights[layer][row][col] = parent2_weights[layer][row][col]
                        if randint(0, 100) >= (100-self.mutation_rate):  # mutation
                            parent1_weights[layer][row][col] += uniform(-0.5, 0.5)

                else:  # for biases
                    if randint(0, 1):  # crossover
                        parent1_weights[layer][row] = parent2_weights[layer][row]
                    if randint(0, 100) >= (100-self.mutation_rate):  # mutation
                        parent1_weights[layer][row] += uniform(-0.5, 0.5)

        self.model.set_weights(parent1_weights)
