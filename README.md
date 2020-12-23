# Meter Shower

The goal of this project was to design an environment where little red squares (envisioned as spaceships in space) learn to avoid little grey squares (envisioned as meteors). Below is a demonstration of the whole population as well as the best individual after 20 generations of training:

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/gen20.gif)
![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/bestof_gen20.gif)

## How It Works
The red squares die if they are hit by one of the grey squares. The red squares have 8 points around them which detect collisions:

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/spaceship_img.png)

The state of these points is stored in an array of ones and zeros (one: collision detected, zero: no collision) which is then fed into a neural network:

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/neural_network.png)

To speed up collision detection a special datastructure called a QuadTree is used to divide and subdivide the map into quadrants recursively. To check if one of the red squares is colliding only its sub-quadrant needs to be checked for the presence of any grey squares. [Pygame's implementation](https://www.pygame.org/wiki/QuadTree) of a QuadTree was used.

The neural network uses the tanh activation function and maps its outputs to movement in the environment. The tanh is rounded so that the possible outputs are -1,0 or 1 which in turn correspond to decreasing, leaving unchanged or increasing one of the coordinates respectively. 

When the simulation begins, a 100 red squares are spawned in the middle whereas the grey squares are spawned around the edges. Every grey square has a velocity vector pointing towards a random red square. Everytime a grey square moves outside the bounds of the map, it respawns with a new velocity vector pointing towards one of the alive red squares. A generation ends when all of the red squares haves died.

A genetic algorithm is utilised to spawn the next generation. The parent individuals are chosen based on how long they survived (fitness) as well as how diverse they are. Diversity in this project is defined as the distance of one neural network's weight sum to the average of the whole population of neural networks. The adjusted fitness of an individual is therefore calculated as the product of their fitness and diversity. The top 8 individuals with the highest adjusted fitness are then chosen as the parents for the next generation. The goal of diversity is to somewhat reward innovation and keep a diverse population in the hopes of not getting stuck in local minima.

During crossover every individual weight and bias is chosen at random from one of the parents' individual weights at the same position. After crossover there is a 15% chance that a uniform distribution between -0.5 and 0.5 is added to one of the weights or biases (mutation). If the next generation ends up having a lower average fitness than the last, the population is rolled back to the previous and the crosssover and mutation are repeated once again in hopes of spawning a fitter generation.

Over many generations, through the process of artificial natural selection, the population gets better and better at avoiding the grey squares as only those that are good at avoiding the grey squares are chosen as parents for the next generation.



## Other Branches
This project has two branches with two other problems solved using the same environment and a genetic algorithm:
* Food Problem: the red square chases a grey square (envisioned as food).

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/food_problem.gif)

* Track Problem: the squares learn to nagivate a track.

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/track_problem.gif)

* Meteor Shower Replay Mode: loads saved models to replay individuals from the master branch (this branch). 

## This Project Was Built Using
* Pyglet (graphics)
* Tensorflow (neural networks)
* Numpy (matrix calculations)
