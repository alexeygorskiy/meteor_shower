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
white_pixel_img = pyglet.resource.image("white_pixel.png")
car_green_img = pyglet.resource.image("car_green.png")

center_img(car_img)
center_img(wall_img)
center_img(white_pixel_img)
center_img(car_green_img)

car_obj = physicalobject.PhysicalObject(img=car_img, x=50, y=50, batch=main_batch)
#TODO: only draw the walls once as their position won't change
wall_obj = pyglet.sprite.Sprite(img=wall_img, x=400, y=400, batch=main_batch)

#white_pixel1 = physicalobject.PhysicalObject(img=white_pixel_img, ray=True, x=100, y=100, batch=main_batch)

label = pyglet.text.Label(text='Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=400, y=400,
                          anchor_x='center', anchor_y='center', batch=main_batch)


def update(dt):
    car_obj.update(dt=dt)
    label.text = str(car_obj.fitness)

    """
    if car_obj.is_dead():
        car_obj.opacity = 100
    else:
        car_obj.opacity = 255
    
    for collision in car_obj.ray_point_collision():
        if collision:
            car_obj.image = car_green_img
            break
        else:
            car_obj.image = car_img
    """


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

game_window.push_handlers(car_obj.key_handler)

game_window.set_visible()

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()

