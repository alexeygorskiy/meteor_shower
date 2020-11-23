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
population_size = 100
# generates a population of PhysicalObjects equal to population_size
spaceships = [physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch) for i in range(population_size)]

meteor = pyglet.sprite.Sprite(img=meteor_img, x=400, y=400, batch=main_batch)


label1 = pyglet.text.Label(x=400, y=400, batch=text_batch)
label2 = pyglet.text.Label(x=400, y=380, batch=text_batch)
label3 = pyglet.text.Label(x=400, y=360, batch=text_batch)



# all below variables have to be reset at the start of a new generation
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
    global alive_individuals
    alive_individuals = 0

    all_dead = True

    for i in range(0, len(spaceships)):
        spaceships[i].update(dt=dt)

        if not spaceships[i].dead:
            all_dead = False
            alive_individuals+=1

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

    if all_dead:
        reset()


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


# TODO: have more parents for better genetic variation (look at how the car algorithm is implemented)
# TODO: research which evolutionary algorithm you should be using (eg. change individual weights or whole layers?)

