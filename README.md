# Meteor Shower - Track Problem Branch
This branch aims to solve a different problem than the master branch: to train squares to navigate a track.

![alt text](https://github.com/alexeygorskiy/meteor_shower/blob/track_problem/resources/track_problem.gif)

The mechanics for this are quite similar to the Meteor Shower problem (master branch). The exceptions are:
* QuadTree is not used 
* Population size is 200 and the top 10 are chosen as parents
* Diversity is not taken into account
* If all the individuals die in generation 0 without making any progress the whole population is restarted with new neural networks

The fitness in this problem is defined as how far an individual gets along the track. There are 16 reward gates around the track. Every reward gate, except the last one, increase the fitness of an individual by 100. The last reward gate increases by 10 000 instead as that counts as completing an entire lap around the track.
