import pyglet
import spaceshipobject
import meteorobject

def center_img(img):
    """Sets an image's anchor point to its center"""
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

# finding and centering the images
pyglet.resource.path = ['resources/']
pyglet.resource.reindex()
spaceship_img = pyglet.resource.image("car.png")
#meteor_img = pyglet.resource.image("wall.png")
best_fitness_img = pyglet.resource.image("car_green.png")
center_img(spaceship_img)
#center_img(meteor_img)
center_img(best_fitness_img)


game_window = pyglet.window.Window(800, 800, caption="Meteor Shower", visible=False)
game_window.set_location(1100, 150)
main_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

generation = 0
population_size = 100
number_of_parents = 5
restarts = 0
population_rollbacks = 0
# generates a population of PhysicalObjects equal to population_size
spaceships = [spaceshipobject.SpaceshipObject(img=spaceship_img, batch=main_batch) for i in range(population_size)]
# HUMAN_CONTROL: spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch, human_controlled=True))

# these two variables are in reality best_generation_spaceships and best_fitness_overall, but these fit as well
last_generation_spaceships = spaceships
avg_fitness_last_generation = -99999


#meteor = pyglet.sprite.Sprite(img=meteor_img, x=400, y=400, batch=main_batch)
#meteor.visible = False

""""""

num_meteors = 50
meteors_batch = pyglet.graphics.Batch()
meteor_img = pyglet.resource.image("meteor.png")
center_img(meteor_img)
meteors = [meteorobject.MeteorObject(img=meteor_img, batch=meteors_batch) for i in range(num_meteors)]

""""""

# labels
number_of_labels = 8
labels = []
for i in range(number_of_labels):
    labels.append(pyglet.text.Label(x=400, y=400-20*i, batch=text_batch))

# all below variables have to be reset at the start of a new generation
highest_fitness = -150
highest_fitness_index = -150
second_highest_fitness = -150
second_highest_fitness_index = -150


"""
    returns the weights and indices of the best individuals from the population equal to the number_of_parents variable 
    :returns (array of best weights, array of best indices)
"""
def find_best_parent_weights():
    spaceships_dict = {}

    for i in range(len(spaceships)):
        spaceships_dict[i] = spaceships[i].fitness

    # sort by fitness in descending order
    spaceships_dict = sorted(spaceships_dict.items(), key=lambda x: x[1], reverse=True)

    best_weights = []
    best_spaceship_indices = []
    # only loop through from the first element and up to the number_of_parents variable
    for key_val_pair in spaceships_dict[:number_of_parents]:
        # key_val_pair[0]: index in the spaceships array, key_val_pair[1]: fitness of that spaceship
        best_weights.append(spaceships[key_val_pair[0]].brain.model.get_weights())
        best_spaceship_indices.append(key_val_pair[0])

    # returns a tuple
    return best_weights, best_spaceship_indices



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
    global spaceships
    global restarts
    global population_rollbacks

    avg_fitness_this_generation = 0

    for spaceship in spaceships:
        avg_fitness_this_generation += spaceship.fitness
    avg_fitness_this_generation /= len(spaceships)

    # the fitness of this generation will be displayed as the fitness of the last
    # generation when the next generation begins
    labels[7].text = "Avg. Fitness Last Generation: " + str(round(avg_fitness_this_generation))

    # if nobody got a single reward in the first generation there is no point evolving from this population,
    # so restart the whole population
    if generation == 0 and highest_fitness < (spaceships[0].gate_reward - spaceships[0].death_punishment):
        # but it's ok to get a reward and then die
        spaceships = [spaceship.SpaceshipObject(img=spaceship_img, x=50, y=50, batch=main_batch) for i in range(population_size)]
        restarts += 1
    elif avg_fitness_this_generation <= avg_fitness_last_generation:    # last generation was better, reset to last
        spaceships = last_generation_spaceships     # last gen pre-evolution and pre-reset
        population_rollbacks += 1
    else:   # if current generation is better than last, keep them and update them to the best
        avg_fitness_last_generation = avg_fitness_this_generation
        last_generation_spaceships = spaceships     # pre-evolution and pre-reset
        population_rollbacks = 0

    # case 1: everybody died without a single reward, will pick random parents and evolve randomly
    # case 2: restart to last generation, will pick best parents from last generation and evolve again
    # case 3: current generation better than last, will evolve the current generation
    best_parent_weights = find_best_parent_weights()
    for spaceship in spaceships:
        spaceship.brain.evolve(best_parent_weights[0])
        spaceship.reset()

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
    shortest_time_without_reward = 99

    for meteor in meteors:
        meteor.update(dt=dt)

    """for i in range(0, len(spaceships)):
        spaceships[i].update(dt=dt)

        if not spaceships[i].dead:
            alive_individuals += 1
            if spaceships[i].time_since_reward < shortest_time_without_reward:
                # keep track of the one that has longest time to left live
                shortest_time_without_reward = spaceships[i].time_since_reward

        if spaceships[i].fitness > highest_fitness:
            highest_fitness = spaceships[i].fitness
            if highest_fitness_index != -150:   # change the last one to normal colour
                spaceships[highest_fitness_index].image = spaceship_img

            highest_fitness_index = i
            spaceships[i].image = best_fitness_img    # set the best one to green

        # and ... prevents the same one from being both the best and 2nd best
        elif spaceships[i].fitness > second_highest_fitness and i != highest_fitness_index:
            second_highest_fitness = spaceships[i].fitness
            if second_highest_fitness_index != -150:   # change the last one to normal colour
                spaceships[second_highest_fitness_index].image = spaceship_img

            second_highest_fitness_index = i
            spaceships[i].image = best_fitness_img  # set the second best one to green
    # finished looping through all the individuals

    labels[0].text = "Best Fitness This Generation: " + str(round(highest_fitness))
    labels[1].text = "Current Generation: " + str(generation)
    labels[2].text = "Alive Individuals: " + str(alive_individuals) + "/" + str(population_size)
    labels[3].text = "Shortest Time Without Reward: " + str(round(shortest_time_without_reward))
    labels[4].text = "Population Restarts: " + str(restarts)
    labels[5].text = "Avg. Fitness Best Generation: " + str(round(avg_fitness_last_generation))
    labels[6].text = "Pop. Rollbacks Current Generation: " + str(population_rollbacks)
    # labels[7] is used to display the "Avg. Fitness Last Generation"

    if alive_individuals == 0:
        pyglet.clock.unschedule(update)  # unschedule until the reset is done
        reset()
        pyglet.clock.schedule_interval(update, 1 / 60.0)"""



fps_display = pyglet.window.FPSDisplay(game_window)

@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()
    meteors_batch.draw()
    text_batch.draw()   # draw the text after main_batch so it ends up on top
    fps_display.draw()


# HUMAN_CONTROL: game_window.push_handlers(spaceships[-1].key_handler)
game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()


