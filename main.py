import pyglet
from objects import spaceshipobject, meteorobject
from utils import utils, quadtree
import time

model_paths = []
model_gens = [0,5,10,15,20,50]
model_fitness = [92,136,167,263,572,1053]
model_index = 0
for i in range(len(model_gens)):
    model_paths.append("saved_models/gen" + str(model_gens[i]) + "_fitness" + str(model_fitness[i]))


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
for img in spaceship_pts_imgs:
    utils.center_img(img)

game_window = pyglet.window.Window(800, 950, caption="Meteor Shower", visible=False)
fps_display = pyglet.window.FPSDisplay(game_window)


game_window.set_location(900, 25)
meteors_batch = pyglet.graphics.Batch()
spaceships_batch = pyglet.graphics.Batch()
text_batch = pyglet.graphics.Batch()

# stats and settings
population_size = 1
number_of_parents = 8
generation = 0
restarts = 0
avg_fitness_last_generation = -99999
avg_weight_sum_last_generation = -99999
highest_fitness = 0
population_rollbacks = 0
num_meteors = 25

spaceships = []
alive_spaceship_coords = []
for i in range(population_size):
    spaceships.append(spaceshipobject.SpaceshipObject(img=spaceship_img, batch=spaceships_batch, model_filepath=model_paths[model_index], subpixel=True))
    alive_spaceship_coords.append([spaceships[i].x, spaceships[i].y])

# HUMAN_CONTROL: spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch, human_controlled=True))
last_generation_spaceships = spaceships

meteors = [meteorobject.MeteorObject(target_coords=alive_spaceship_coords, img=meteor_img, batch=meteors_batch, subpixel=True) for i in range(num_meteors)]

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
    global restarts
    global population_rollbacks
    global highest_fitness
    global alive_spaceship_coords
    global model_index
    global model_paths
    global model_gens
    global model_fitness

    highest_fitness = 0
    model_index += 1
    if model_index == len(model_gens):
        model_index = len(model_gens)-1

    spaceships[0].brain.load_saved_brain(model_paths[model_index])
    spaceships[0].reset()
    alive_spaceship_coords = [[spaceships[0].x, spaceships[0].y]]

    generation = model_gens[model_index]

    for meteor in meteors:
        meteor.reset(target_coords=alive_spaceship_coords)

"""
    updates all the individuals and checks if everyone is dead
"""
def update(dt):
    global highest_fitness
    global alive_spaceship_coords
    alive_individuals = 0

    for meteor in meteors:
        meteor.update(dt=dt, target_coords=alive_spaceship_coords)
    tree = quadtree.QuadTree(meteors, bounding_rect=(0, 0, 800, 800))

    alive_spaceship_coords = []

    for spaceship in spaceships:
        if spaceship.dead:
            continue

        if tree.hit(spaceship.corner_points[0], spaceship.corner_points[1]):
            spaceship.dead = True
            spaceship.visible = False
            continue

        colliding = []
        collision_detected = False
        for i in range(0, len(spaceship.ray_points)):
            ray_pt = [spaceship.ray_points[i][0], spaceship.ray_points[i][1]]
            if tree.hit(left_bottom_corner=ray_pt, right_top_corner=ray_pt) or utils.is_outside_map(ray_pt[0], ray_pt[1]):
                colliding.append(1)
                spaceship.image = spaceship_pts_imgs[i]
                collision_detected = True
            else:
                colliding.append(0)

        spaceship.last_collisions = spaceship.collisions
        spaceship.collisions = colliding

        if not collision_detected:
            spaceship.image = spaceship_img

        spaceship.update(dt=dt)
        alive_individuals += 1
        alive_spaceship_coords.append([spaceship.x, spaceship.y])
        if spaceship.fitness > highest_fitness:
            highest_fitness = spaceship.fitness
    # done looping through all the spaceships

    labels[0].text = "FPS: " + str(fps_display.label.text)
    labels[1].text = "Best of Generation: " + str(generation)
    labels[2].text = "Fitness Achieved: " + str(model_fitness[model_index])
    labels[3].text = "Current Fitness: " + str(round(highest_fitness))

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


