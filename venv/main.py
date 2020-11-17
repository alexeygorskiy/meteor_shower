import pyglet
import physicalobject
from pyglet import shapes

def center_img(img):
    """Sets an image's anchor point to its center"""
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

game_window = pyglet.window.Window(800, 800, caption="Meteor Shower", visible=False)
main_batch = pyglet.graphics.Batch()

spaceship_img = pyglet.resource.image("car.png")
meteor_img = pyglet.resource.image("wall.png")

center_img(spaceship_img)
center_img(meteor_img)

spaceship_1 = physicalobject.PhysicalObject(human_controlled = True, img=spaceship_img, x=50, y=50, batch=main_batch)
spaceship_2 = physicalobject.PhysicalObject(img=spaceship_img, x=50, y=50, batch=main_batch)

#TODO: only draw the walls once as their position won't change
meteor = pyglet.sprite.Sprite(img=meteor_img, x=400, y=400, batch=main_batch)

label = pyglet.text.Label(text='Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=770, y=770,
                          anchor_x='center', anchor_y='center', batch=main_batch)

spaceships = [spaceship_1, spaceship_2]

def reset():
    for spaceship in spaceships:
        spaceship.reset()


def update(dt):
    highest_fitness = -150
    all_dead = True

    for spaceship in spaceships:
        spaceship.update(dt=dt)

        if not spaceship.dead:
            all_dead = False

        if spaceship.fitness > highest_fitness:
            highest_fitness = spaceship.fitness

    #label.text = str(highest_fitness)
    label.text = str(int(spaceship_1.time_since_reward))

    if all_dead:
        reset()


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

game_window.push_handlers(spaceship_1.key_handler)

game_window.set_visible()

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()

