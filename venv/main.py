import pyglet
import physicalobject
from pyglet import shapes

def center_img(img):
    """Sets an image's anchor point to its center"""
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

game_window = pyglet.window.Window(800, 800, caption="Car Environment", visible=False)
main_batch = pyglet.graphics.Batch()

car_img = pyglet.resource.image("car.png")
wall_img = pyglet.resource.image("wall.png")

center_img(car_img)
center_img(wall_img)

car_obj = physicalobject.PhysicalObject(human_controlled = True, img=car_img, x=50, y=50, batch=main_batch)
car_obj2 = physicalobject.PhysicalObject(img=car_img, x=50, y=50, batch=main_batch)

#TODO: only draw the walls once as their position won't change
wall_obj = pyglet.sprite.Sprite(img=wall_img, x=400, y=400, batch=main_batch)

label = pyglet.text.Label(text='Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=400, y=400,
                          anchor_x='center', anchor_y='center', batch=main_batch)

cars = [car_obj, car_obj2]

def reset():
    for car in cars:
        car.reset()


def update(dt):
    highest_fitness = -150
    all_dead = True

    for car in cars:
        car.update(dt=dt)

        if not car.dead:
            all_dead = False

        if car.fitness > highest_fitness:
            highest_fitness = car.fitness

    #label.text = str(highest_fitness)
    label.text = str(int(car_obj.time_since_reward))

    if all_dead:
        reset()


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

game_window.push_handlers(car_obj.key_handler)

game_window.set_visible()

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()

