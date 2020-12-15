import pyglet
from objects import spaceshipobject, meteorobject
from utils import utils, quadtree
import time

begin_time = time.time()
pyglet.resource.path = ['resources/']
pyglet.resource.reindex()
spaceship_img = pyglet.resource.image("spaceship.png")
meteor_img = pyglet.resource.image("meteor.png")
border_img = pyglet.resource.image("border.png")
utils.center_img(spaceship_img)
utils.center_img(meteor_img)
utils.center_img(border_img)

spaceship_pts_imgs = [pyglet.resource.image("spaceship_pt" + str(i) + ".png") for i in range(0, 8)]
spaceship_pts_imgs_purple = [pyglet.resource.image("spaceship_pt" + str(i) + "_purple.png") for i in range(0, 8)]

for i in range(len(spaceship_pts_imgs)):
    utils.center_img(spaceship_pts_imgs[i])
    utils.center_img(spaceship_pts_imgs_purple[i])

game_window = pyglet.window.Window(800, 950, caption="Meteor Shower", visible=False)
fps_display = pyglet.window.FPSDisplay(game_window)


game_window.set_location(900, 25)
meteors_batch = pyglet.graphics.Batch()
spaceships_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

# stats and settings
population_size = 100
number_of_parents = 8
generation = 0
avg_fitness_last_generation = -99999
avg_weight_sum_last_generation = -99999
highest_fitness = 0
population_rollbacks = 0
num_meteors = 25

spaceships = []
for i in range(population_size):
    spaceships.append(spaceshipobject.SpaceshipObject(img=spaceship_img, batch=spaceships_batch, subpixel=True))

# HUMAN_CONTROL: spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch, human_controlled=True))
last_generation_spaceships = spaceships

meteors = [meteorobject.MeteorObject(img=meteor_img, batch=meteors_batch, subpixel=True) for i in range(num_meteors)]
tree = quadtree.QuadTree(meteors, bounding_rect=(0, 0, 800, 800))

# labels
number_of_labels = 12
labels = []
for i in range(number_of_labels):
    if i < 5:
        labels.append(pyglet.text.Label(x=25, y=920 - 20 * i, batch=text_batch))
    else:
        labels.append(pyglet.text.Label(x=350, y=920 - 20 * (i-5), batch=text_batch))
labels.append(pyglet.sprite.Sprite(x=400, y=805, batch=text_batch, img=border_img))

"""
    when everyone is dead, "evolves" the population and resets the simulation
"""
def reset():
    global generation
    global last_generation_spaceships
    global avg_fitness_last_generation
    global avg_weight_sum_last_generation
    global spaceships
    global population_rollbacks
    global highest_fitness

    avg_fitness_this_generation = 0
    avg_weight_sum_this_generation = 0

    for spaceship in spaceships:
        avg_fitness_this_generation += spaceship.fitness
        avg_weight_sum_this_generation += spaceship.weight_sum
        if generation % 5 == 0 and spaceship.fitness == highest_fitness:
            spaceship.brain.save_current_brain(path="saved_models/gen" + str(generation) + "_fitness" + str(round(highest_fitness)))


    avg_fitness_this_generation /= len(spaceships)
    avg_weight_sum_this_generation /= len(spaceships)

    # the fitness of this generation will be displayed as the fitness of the last
    # generation when the next generation begins
    labels[7].text = "Avg. Fitness Last Generation: " + str(round(avg_fitness_this_generation))
    labels[9].text = "Avg. Weight Sum Last Generation: " + str(round(avg_weight_sum_this_generation,3))

    if avg_fitness_this_generation <= avg_fitness_last_generation:    # last generation was better, reset to last
        spaceships = last_generation_spaceships     # last gen pre-evolution and pre-reset
        population_rollbacks += 1
    else:   # if current generation is better than last, keep them and update them to the best
        avg_fitness_last_generation = avg_fitness_this_generation
        avg_weight_sum_last_generation = avg_weight_sum_this_generation
        last_generation_spaceships = spaceships     # pre-evolution and pre-reset
        population_rollbacks = 0

    # case 1: restart to last generation, will pick best parents from last generation and evolve again
    # case 2: current generation better than last, will evolve the current generation
    best_parent_weights = utils.find_best_parent_weights(spaceships, number_of_parents, avg_weight_sum_this_generation)
    for i in range(population_size):
        spaceships[i].brain.evolve(best_parent_weights[0])
        spaceships[i].reset()

    generation += 1
    highest_fitness = 0

    for meteor in meteors:
        meteor.reset()


"""
    updates all the individuals and checks if everyone is dead
"""
def update(dt):
    global highest_fitness
    global tree

    alive_individuals = 0
    eaten_meteors = []
    shortest_time_without_reward = 99999

    for spaceship in spaceships:
        if spaceship.dead:
            continue

        hits = tree.hit(spaceship.corner_points[0], spaceship.corner_points[1])
        if len(hits) > 0:
            for meteor in hits:
                meteor.eaten = True
                eaten_meteors.append(meteor)
            spaceship.update_fitness()

        colliding = []
        collision_detected = False
        for i in range(0, len(spaceship.ray_points)):
            ray_pt = [spaceship.ray_points[i][0], spaceship.ray_points[i][1]]
            if tree.hit(left_bottom_corner=ray_pt, right_top_corner=ray_pt):
                colliding.append(1)
                spaceship.image = spaceship_pts_imgs[i]
                collision_detected = True
            elif utils.is_outside_map(ray_pt[0], ray_pt[1]):
                colliding.append(-1)
                spaceship.image = spaceship_pts_imgs_purple[i]
                collision_detected = True
            else:
                colliding.append(0)

        spaceship.last_collisions = spaceship.collisions
        spaceship.collisions = colliding

        if not collision_detected:
            spaceship.image = spaceship_img

        spaceship.update(dt=dt)
        alive_individuals += 1
        if spaceship.fitness > highest_fitness:
            highest_fitness = spaceship.fitness

        if spaceship.time_since_reward < shortest_time_without_reward:
            shortest_time_without_reward = spaceship.time_since_reward
    # done looping through all the spaceships

    # if any meteors have been eaten, respawn them and make a new tree
    if len(eaten_meteors) > 0:
        for meteor in eaten_meteors:
            meteor.update(dt=dt)

    tree = quadtree.QuadTree(meteors, bounding_rect=(0, 0, 800, 800))

    labels[0].text = "FPS: " + str(fps_display.label.text)
    labels[1].text = "Simulation Time: " + str(int(time.time() - begin_time)) + " s."
    labels[2].text = "Current Generation: " + str(generation)
    labels[3].text = "Alive Individuals: " + str(alive_individuals) + "/" + str(population_size)
    labels[4].text = "Pop. Rollbacks Current Generation: " + str(population_rollbacks)

    labels[5].text = "Best Fitness This Generation: " + str(round(highest_fitness))
    labels[6].text = "Avg. Fitness Best Generation: " + str(round(avg_fitness_last_generation))
    # labels[7] is used to display the "Avg. Fitness Last Generation"
    labels[8].text = "Avg. Weight Sum Best Generation: " + str(round(avg_weight_sum_last_generation,3))
    # labels[9] is used to display the "Avg. Weight Sum Last Generation"
    labels[10].text = "Shortest Time Without Reward: " + str(shortest_time_without_reward)

    if alive_individuals == 0:
        pyglet.clock.unschedule(update)  # unschedule until the reset is done
        reset()
        pyglet.clock.schedule_interval(update, 1 / 60.0)

@game_window.event
def on_draw():
    game_window.clear()
    text_batch.draw()
    spaceships_batch.draw()
    meteors_batch.draw()

# HUMAN_CONTROL: game_window.push_handlers(spaceships[-1].key_handler)
game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()


# TODO: as last the thing: review code
# TODO: (very long term or not at all) do a comparison with and without diversity
# TODO: (very long term or not at all) replace ray points with ray lines instead so they know the distance as well
# TODO: (very long term or not at all) evolve topology


