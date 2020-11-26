import pyglet
import physicalobject

def center_img(img):
    """Sets an image's anchor point to its center"""
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

# finding and centering the images
pyglet.resource.path = ['resources/']
pyglet.resource.reindex()
spaceship_img = pyglet.resource.image("car.png")
meteor_img = pyglet.resource.image("wall.png")
best_fitness_img = pyglet.resource.image("car_green.png")
center_img(spaceship_img)
center_img(meteor_img)
center_img(best_fitness_img)


game_window = pyglet.window.Window(800, 800, caption="Meteor Shower", visible=False)
game_window.set_location(1100,150)
main_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

generation = 0
population_size = 200
number_of_parents = 10
restarts = 0
population_rollbacks = 0
# generates a population of PhysicalObjects equal to population_size
spaceships = [physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch) for i in range(population_size)]

last_generation_spaceships = spaceships
avg_fitness_last_generation = -99999
avg_fitness_this_generation = 0


meteor = pyglet.sprite.Sprite(img=meteor_img, x=400, y=400, batch=main_batch)


label1 = pyglet.text.Label(x=400, y=400, batch=text_batch)
label2 = pyglet.text.Label(x=400, y=380, batch=text_batch)
label3 = pyglet.text.Label(x=400, y=360, batch=text_batch)
label4 = pyglet.text.Label(x=400, y=340, batch=text_batch)
label5 = pyglet.text.Label(x=400, y=320, batch=text_batch)
label6 = pyglet.text.Label(x=400, y=300, batch=text_batch)
label7 = pyglet.text.Label(x=400, y=280, batch=text_batch)
label8 = pyglet.text.Label(x=400, y=260, batch=text_batch)

# all below variables have to be reset at the start of a new generation
highest_fitness = -150
highest_fitness_index = -150
second_highest_fitness = -150
second_highest_fitness_index = -150


"""
    returns the weights of the best individuals from the population equal to the number_of_parents variable 
    if there are less suitable parents than the number_of_parents variable, returns the suitable ones
    if no one is suitable, returns an empty array
"""
def find_best_parent_weights():
    spaceships_dict = {}

    for i in range(len(spaceships)):
        spaceships_dict[i] = spaceships[i].fitness
    spaceships_dict = sorted(spaceships_dict.items(), key=lambda x: x[1], reverse=True)

    best_weights = []
    best_spaceship_indices = []
    for key in spaceships_dict[:number_of_parents]:
        best_weights.append(spaceships[key[0]].brain.model.get_weights())
        best_spaceship_indices.append(key[0])

    return (best_weights, best_spaceship_indices)



"""
    when everyone is dead, "evolves" the population and resets the simulation
"""
def reset():
    global highest_fitness
    global highest_fitness_index
    global second_highest_fitness
    global second_highest_fitness_index
    global generation
    global last_generation_spaceships
    global avg_fitness_last_generation
    global avg_fitness_this_generation
    global spaceships
    global restarts
    global population_rollbacks

    avg_fitness_this_generation = 0

    for spaceship in spaceships:
        avg_fitness_this_generation += spaceship.fitness
    avg_fitness_this_generation /= len(spaceships)

    label8.text = "Avg. Fitness Last Generation: " + str(avg_fitness_this_generation)

    # everybody died without getting a single reward, restart the whole population
    if avg_fitness_this_generation <= -spaceships[0].death_punishment:
        spaceships = [physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch) for i in range(population_size)]
        restarts += 1
    elif avg_fitness_this_generation <= avg_fitness_last_generation: # last generation was better, reset to last
        spaceships = last_generation_spaceships # last gen pre-evolution and pre-reset
        population_rollbacks += 1
    else:   # if current generation is better than last, keep them and update the avg_fitness_last_generation
        avg_fitness_last_generation = avg_fitness_this_generation
        last_generation_spaceships = spaceships # pre-evolution and pre-reset
        population_rollbacks = 0

    # case 1: everybody died without a single reward, will pick random parents and evolve randomly
    # case 2: restart to last generation, will pick best parents from last generation and evolve again
    # case 3: current generation better than last, will evolve the current generation
    best_parent_weights = find_best_parent_weights()
    for spaceship in spaceships:
        spaceship.brain.evolve(best_parent_weights[0])
        spaceship.reset()

    # the below algorithm has an increasing mutation rate depending on how many rollbacks have been made
    """
    best_parent_weights = find_best_parent_weights()
    for spaceship in spaceships:
        if population_rollbacks == 0 and spaceship.brain.mutation_rate != 15:
            spaceship.brain.mutation_rate = 15
        elif population_rollbacks == 5:
            spaceship.brain.mutation_rate = 25
        elif population_rollbacks == 10:
            spaceship.brain.mutation_rate = 35
        elif population_rollbacks == 15:
            spaceship.brain.mutation_rate = 45

        spaceship.brain.evolve(best_parent_weights[0])
        spaceship.reset()
    """

    # the below algorithm keeps the parents unevolved, kinda useless since you can revert to earlier generations
    """
    best_parent_weights = find_best_parent_weights()
    for i in range(len(spaceships)):
        if i not in best_parent_weights[1]:
            # keep the parents unevolved to give them a chance to breed more
            spaceships[i].brain.evolve(best_parent_weights[0])
        spaceships[i].reset()
    """

    # reset the images of the best individuals back to the normal image
    if highest_fitness_index != -150:
        spaceships[highest_fitness_index].image = spaceship_img
    if second_highest_fitness_index != -150:
        spaceships[second_highest_fitness_index].image = spaceship_img

    highest_fitness = -150
    highest_fitness_index = -150
    second_highest_fitness = -150
    second_highest_fitness_index = -150
    generation += 1

"""
    updates all the individuals and checks if everyone is dead
"""
def update(dt):
    global highest_fitness
    global highest_fitness_index
    global second_highest_fitness
    global second_highest_fitness_index

    alive_individuals = 0
    all_dead = True
    shortest_time_without_reward = 99

    for i in range(0, len(spaceships)):
        spaceships[i].update(dt=dt)

        if not spaceships[i].dead:
            all_dead = False
            alive_individuals += 1
            if spaceships[i].time_since_reward < shortest_time_without_reward:
                shortest_time_without_reward = spaceships[i].time_since_reward  # keep track of the one that has longest time to live

        if spaceships[i].fitness > highest_fitness:
            highest_fitness = spaceships[i].fitness
            if highest_fitness_index != -150:   # change the last one to normal colour
                spaceships[highest_fitness_index].image = spaceship_img

            highest_fitness_index = i
            spaceships[i].image = best_fitness_img    # set the best one to green
        elif spaceships[i].fitness > second_highest_fitness and highest_fitness_index != i: # and ... prevents the same one from being both the best and 2nd best
            second_highest_fitness = spaceships[i].fitness
            if second_highest_fitness_index != -150:   # change the last one to normal colour
                spaceships[second_highest_fitness_index].image = spaceship_img

            second_highest_fitness_index = i
            spaceships[i].image = best_fitness_img  # set the second best one to green
    # finished looping through all the individuals

    label1.text = "Best Fitness This Generation: " + str(round(highest_fitness))
    label2.text = "Current Generation: " + str(generation)
    label3.text = "Alive Individuals: " + str(alive_individuals) + "/" + str(population_size)
    label4.text = "Shortest Time Without Reward: " + str(round(shortest_time_without_reward))
    label5.text = "Population Restarts: " + str(restarts)
    label6.text = "Avg. Fitness Best Generation: " + str(avg_fitness_last_generation)
    label7.text = "Pop. Rollbacks Current Generation: " + str(population_rollbacks)

    if all_dead:
        pyglet.clock.unschedule(update)  # unschedule until all reset is done
        reset()
        pyglet.clock.schedule_interval(update, 1 / 60.0)



fps_display = pyglet.window.FPSDisplay(game_window)

@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()
    text_batch.draw()
    fps_display.draw()


game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()


# TODO: code review of changed on 26th November, double check the avg_fitness reset algorithm
# TODO: research which evolutionary algorithm you should be using (eg. change individual weights or whole layers?) (look at how the car algorithm is implemented)
# TODO: maybe make it so that anyone can breed, but the higher your fitness the higher the odds?
