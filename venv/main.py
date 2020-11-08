import pyglet
import physicalobject

def center_img(img):
    """Sets an image's anchor point to its center"""
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

game_window = pyglet.window.Window(800, 600, caption="Car Environment", visible=False)
main_batch = pyglet.graphics.Batch()

car_img = pyglet.resource.image("car.png")
wall_img = pyglet.resource.image("wall.png")
white_pixel_img = pyglet.resource.image("white_pixel.png")

center_img(car_img)
center_img(wall_img)
center_img(white_pixel_img)

car_obj = physicalobject.PhysicalObject(img=car_img, x=400, y=300, batch=main_batch)
wall_obj = pyglet.sprite.Sprite(img=wall_img, x=600, y=200, batch=main_batch)

#white_pixel_1 = physicalobject.PhysicalObject(img=white_pixel_img, x=car_obj.position[0], y=car_obj.position[1], batch=main_batch)
#white_pixel_2 = physicalobject.PhysicalObject(img=white_pixel_img, x=wall_obj.position[0], y=wall_obj.position[1], batch=main_batch)



game_objects = [car_obj, wall_obj]

def update(dt):
    car_obj.update(dt=dt)

    if car_obj.collides_with(wall_obj):
        car_obj.handle_collision_with(wall_obj)
    else:
        car_obj.opacity = 255

"""
    for i in range(len(game_objects)):
        for j in range(i + 1, len(game_objects)):
            obj_1 = game_objects[i]
            obj_2 = game_objects[j]

            if obj_1.collides_with(obj_2):
                obj_1.handle_collision_with(obj_2)
                obj_2.handle_collision_with(obj_1)
"""

@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

game_window.push_handlers(car_obj.key_handler)
game_window.set_visible()

pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()

