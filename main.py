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
best_fitness_img = pyglet.resource.image("car_green.png")
meteor_img = pyglet.resource.image("meteor.png")
center_img(spaceship_img)
center_img(best_fitness_img)
center_img(meteor_img)

game_window = pyglet.window.Window(800, 800, caption="Meteor Shower", visible=False)
game_window.set_location(1100, 150)
spaceships_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

generation = 0
population_size = 100
number_of_parents = 10
restarts = 0
population_rollbacks = 0
# generates a population of PhysicalObjects equal to population_size
spaceships = [spaceshipobject.SpaceshipObject(img=spaceship_img, batch=spaceships_batch) for i in range(population_size)]
# HUMAN_CONTROL: spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch, human_controlled=True))

# these two variables are in reality best_generation_spaceships and best_fitness_overall, but these fit as well
last_generation_spaceships = spaceships
avg_fitness_last_generation = -99999


num_meteors = 50
meteors_batch = pyglet.graphics.Batch()
meteors = [meteorobject.MeteorObject(img=meteor_img, batch=meteors_batch) for i in range(num_meteors)]

# labels
number_of_labels = 7
labels = []
for i in range(number_of_labels):
    labels.append(pyglet.text.Label(x=400, y=400-20*i, batch=text_batch))


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
    labels[6].text = "Avg. Fitness Last Generation: " + str(round(avg_fitness_this_generation))

    if avg_fitness_this_generation <= avg_fitness_last_generation:    # last generation was better, reset to last
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

    generation += 1

    for meteor in meteors:
        meteor.reset()


"""
    https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
"""
def collision_detected(meteor, spaceship):
    return (meteor.x < spaceship.x + spaceship.width and
            meteor.x + meteor.width > spaceship.x and
            meteor.y < spaceship.y + spaceship.height and
            meteor.y + meteor.height > spaceship.y)

"""
    https://www.geeksforgeeks.org/check-if-a-point-lies-on-or-inside-a-rectangle-set-2/#:~:text=A%20point%20lies%20inside%20or,right%20and%20top%2Dleft%20coordinates.
"""
def point_colliding(pt, meteor):
    # corner_points[0]: bottom left corner
    # corner_points[1]: top right corner
    return (meteor.corner_points[0][0] < pt[0] < meteor.corner_points[1][0] and
            meteor.corner_points[0][1] < pt[1] < meteor.corner_points[1][1])

def point_out_of_bounds(pt):
    # corner_points[0]: bottom left corner
    # corner_points[1]: top right corner

    return not (0<=pt[0]<=800 and 0<=pt[1]<=800)




"""
    updates all the individuals and checks if everyone is dead
"""
def update(dt):
    highest_fitness = 0
    alive_individuals = 0

    for meteor in meteors:
        meteor.update(dt=dt)

    for spaceship in spaceships:
        if spaceship.dead:
            continue

        for meteor in meteors:
            if collision_detected(meteor, spaceship):
                spaceship.dead = True
                spaceship.visible = False
                break

            colliding = []
            for pt in spaceship.ray_points:
                colliding.append(1 if point_colliding(pt, meteor) or point_out_of_bounds(pt) else 0)

            spaceship.last_collisions = spaceship.collisions
            spaceship.collisions = colliding

        if not spaceship.dead:
            spaceship.update(dt=dt)
            alive_individuals += 1
            if spaceship.fitness > highest_fitness:
                highest_fitness = spaceship.fitness

    labels[0].text = "Best Fitness This Generation: " + str(round(highest_fitness))
    labels[1].text = "Current Generation: " + str(generation)
    labels[2].text = "Alive Individuals: " + str(alive_individuals) + "/" + str(population_size)
    labels[3].text = "Population Restarts: " + str(restarts)
    labels[4].text = "Avg. Fitness Best Generation: " + str(round(avg_fitness_last_generation))
    labels[5].text = "Pop. Rollbacks Current Generation: " + str(population_rollbacks)
    # labels[6] is used to display the "Avg. Fitness Last Generation"

    if alive_individuals <= int(population_size/4):
        pyglet.clock.unschedule(update)  # unschedule until the reset is done
        reset()
        pyglet.clock.schedule_interval(update, 1 / 60.0)



fps_display = pyglet.window.FPSDisplay(game_window)

@game_window.event
def on_draw():
    game_window.clear()
    spaceships_batch.draw()
    meteors_batch.draw()
    text_batch.draw()   # draw the text after main_batch so it ends up on top
    fps_display.draw()


# HUMAN_CONTROL: game_window.push_handlers(spaceships[-1].key_handler)
game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()


