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
main_batch = pyglet.graphics.Batch()

generation = 0
population_size = 100
spaceships = []
# generates a population of PhysicalObjects equal to population_size
for i in range(0, population_size):
    spaceships.append(physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch))

# TODO: only draw the walls once as their position won't change
meteor = pyglet.sprite.Sprite(img=meteor_img, x=400, y=400, batch=main_batch)
label = pyglet.text.Label(text='Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=770, y=770,
                          anchor_x='center', anchor_y='center', batch=main_batch)



highest_fitness = -150
highest_fitness_index = -150
second_highest_fitness = -150
second_highest_fitness_index = -150

"""
    when everyone is dead, "evolves" the population and resets the simulation
"""
def reset():
    global highest_fitness
    global highest_fitness_index
    global second_highest_fitness
    global second_highest_fitness_index
    global generation

    for i in range(0, len(spaceships)):
        if i!=highest_fitness_index and i!=second_highest_fitness_index and generation!=0:  # generation 0 is a bit buggy, so wait till next one to start evolving
            spaceships[i].brain.evolve(spaceships[highest_fitness_index], spaceships[second_highest_fitness_index])
        spaceships[i].reset()

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

    all_dead = True

    for i in range(0, len(spaceships)):
        spaceships[i].update(dt=dt)

        if not spaceships[i].dead:
            all_dead = False

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

    label.text = str(round(highest_fitness))

    if all_dead:
        reset()


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

game_window.set_visible()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()

