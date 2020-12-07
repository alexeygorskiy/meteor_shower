import pyglet
import spaceshipobject
import meteorobject
import utils
import quadtree

pyglet.resource.path = ['resources/']
pyglet.resource.reindex()
spaceship_img = pyglet.resource.image("car.png")
best_fitness_img = pyglet.resource.image("car_green.png")
meteor_img = pyglet.resource.image("meteor.png")
border_img = pyglet.resource.image("border.png")
utils.center_img(spaceship_img)
utils.center_img(best_fitness_img)
utils.center_img(meteor_img)
utils.center_img(border_img)
game_window = pyglet.window.Window(800, 1000, caption="Meteor Shower", visible=False)
fps_display = pyglet.window.FPSDisplay(game_window)

game_window.set_location(900, 25)
meteors_batch = pyglet.graphics.Batch()
spaceships_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

# stats and settings
population_size = 200
number_of_parents = 10
generation = 0
restarts = 0
avg_fitness_last_generation = -99999
highest_fitness = 0
population_rollbacks = 0
num_meteors = 50

spaceships = [spaceshipobject.SpaceshipObject(img=spaceship_img, batch=spaceships_batch) for i in range(population_size)]
# HUMAN_CONTROL: spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch, human_controlled=True))
last_generation_spaceships = spaceships
meteors = [meteorobject.MeteorObject(img=meteor_img, batch=meteors_batch) for i in range(num_meteors)]

# labels
number_of_labels = 8
labels = []
for i in range(number_of_labels):
    labels.append(pyglet.text.Label(x=25, y=970-20*i, batch=text_batch))
labels.append(pyglet.sprite.Sprite(x=400, y=805, batch=text_batch, img=border_img))

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
    global highest_fitness

    avg_fitness_this_generation = 0

    for spaceship in spaceships:
        avg_fitness_this_generation += spaceship.fitness
    avg_fitness_this_generation /= len(spaceships)

    # the fitness of this generation will be displayed as the fitness of the last
    # generation when the next generation begins
    labels[7].text = "Avg. Fitness Last Generation: " + str(round(avg_fitness_this_generation))

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
    best_parent_weights = utils.find_best_parent_weights(spaceships, number_of_parents)
    for spaceship in spaceships:
        spaceship.brain.evolve(best_parent_weights[0])
        spaceship.reset()

    generation += 1
    highest_fitness = 0

    for meteor in meteors:
        meteor.reset()


"""
    updates all the individuals and checks if everyone is dead
"""
def update(dt):
    global highest_fitness
    alive_individuals = 0

    for meteor in meteors:
        meteor.update(dt=dt)
    tree = quadtree.QuadTree(meteors, bounding_rect=(0, 0, 800, 800))

    for spaceship in spaceships:
        if spaceship.dead:
            continue

        if len(tree.hit(spaceship.corner_points[0], spaceship.corner_points[1])) > 0:
            spaceship.dead = True
            spaceship.visible = False
            continue

        colliding = []
        for pt in spaceship.ray_points:
            colliding.append(1 if len(tree.hit([pt[0], pt[1]], [pt[0], pt[1]])) > 0 or utils.is_outside_map(pt[0], pt[1]) else 0)

        spaceship.last_collisions = spaceship.collisions
        spaceship.collisions = colliding

        spaceship.update(dt=dt)
        alive_individuals += 1
        if spaceship.fitness > highest_fitness:
            highest_fitness = spaceship.fitness

    labels[0].text = "FPS: " + str(fps_display.label.text)
    labels[1].text = "Best Fitness This Generation: " + str(round(highest_fitness))
    labels[2].text = "Current Generation: " + str(generation)
    labels[3].text = "Alive Individuals: " + str(alive_individuals) + "/" + str(population_size)
    labels[4].text = "Population Restarts: " + str(restarts)
    labels[5].text = "Avg. Fitness Best Generation: " + str(round(avg_fitness_last_generation))
    labels[6].text = "Pop. Rollbacks Current Generation: " + str(population_rollbacks)
    # labels[6] is used to display the "Avg. Fitness Last Generation"


    if alive_individuals <= int(population_size/4):
        pyglet.clock.unschedule(update)  # unschedule until the reset is done
        reset()
        pyglet.clock.schedule_interval(update, 1 / 60.0)


@game_window.event
def on_draw():
    game_window.clear()
    spaceships_batch.draw()
    meteors_batch.draw()
    text_batch.draw()   # draw the text after main_batch so it ends up on top

# HUMAN_CONTROL: game_window.push_handlers(spaceships[-1].key_handler)
game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()



# TODO: take diversity into account
# TODO: change their speeds. the spaceships HAVE TO BE FASTER (always)
# TODO: see if you can optimise quadtree or anything else
# TODO: improve quadtree implementation to not return everything, just return as soon as len(hits)>0
# TODO: read through the quadtree page and see about the optimisation