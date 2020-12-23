# Meteor Shower - Food Problem Branch
This branch aims to solve a different problem than the master branch: to train the red square to chase the grey square (envisioned as food).

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/master/resources/food_problem.gif)

The mechanics for this are quite similar to the Meteor Shower problem (master branch). The exceptions are:

* QuadTree is not used
* The NEAT algorithm is used instead of the genetic algorithm on the master branch

## The NEAT algoritm
NeuroEvolution of Augmenting Topologies (or NEAT for short) is a method developed by Kenneth O. Stanley and Risto Miikkulainen. The original paper can be found [here](http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf).

NEAT is a method for evolving both the weights and the topology of neural networks, which usually outperforms fixed-topology methods. The network starts with the minimal amount of nodes (usually the input and output nodes) and introduces new nodes and connections through mutations. The minimalistic start allows the final network to be the minimal solution to a problem.

As topological mutations usually result in lower short-term fitness while the network adapts to the change in its structure, the NEAT method uses speciation to protect topological innovation. If two individuals have very different network topologies or weights, they are classified as different species. An individual only competes within its own species which allows it to survive and reproduce as long as it is not doing too poorly compared to other individuals in its species. Stagnating species that show no improvement for several generations are removed from the population to give more space to other species.  

In this project a finished implementation of the NEAT algorithm was used to solve the task at hand. It can be found [here](https://github.com/CodeReclaimers/neat-python). Using this implementation only the fitness evaluation function (eval_genome) needed to be defined to train the population. This method just ran the simulation environment where the red square had 100 update cycles to reach the grey square before dying. The more grey squares it could reach before dying, the higher its fitness.

As inputs, the neural network was given the x and y coordinates of the grey square and itself. The activation function for all the nodes was the sigmoid and the input (the coordinates) were mapped to [-4,4] to prevent the sigmoid from becoming saturated. The training was terminated when an individual managed to "eat" 16 grey squares. Other settings for the simulation can be viewed in the [config](https://github.com/alexeygorskiy/meteor_shower/blob/food_problem/config) file.

The reason for using the NEAT algorithm instead of the one implemented on the master branch was because it could not solve this problem. It was originally thought that this was because of wrong network topology or because the algorithm was not complex enough (eg. the diversity was protected in a primitive manner). Therefore, the NEAT algorithm was implemented. However, it could not solve the problem either within a reasonable number of generations. It was therefore concluded that the system has insufficient knowledge of its environment to learn how to survive efficiently. After all, it could only detect collisions when they were only 7 pixels away. Instead, the inputs were changed from the state of collisions around the agent to the coordinates of the nearest food and itself, which solved the problem. 

