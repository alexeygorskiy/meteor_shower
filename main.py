import pyglet
from utils import utils
from objects import spaceshipobject, meteorobject
import os
import neat
import multiprocessing
import statistics

pyglet.resource.path = ['resources/']
pyglet.resource.reindex()
spaceship_img = pyglet.resource.image("spaceship.png")
meteor_img = pyglet.resource.image("meteor.png")
utils.center_img(spaceship_img)
utils.center_img(meteor_img)

game_window = pyglet.window.Window(800, 950, caption="Meteor Shower", visible=False)
game_window.set_location(900, 25)
spaceship = spaceshipobject.SpaceshipObject(termination_fitness=90000, img=spaceship_img, subpixel=True)
meteor = meteorobject.MeteorObject(img=meteor_img, subpixel=True)

runs_per_net = 5

def eval_genome(genome, config):
    net = neat.nn.RecurrentNetwork.create(genome, config)

    fitnesses = []

    for runs in range(runs_per_net):
        meteor = meteorobject.MeteorObject(img=meteor_img, subpixel=True)
        spaceship = spaceshipobject.SpaceshipObject(img=spaceship_img, subpixel=True)

        while not spaceship.dead:
            if (meteor.left <= spaceship.corner_points[1][0] and
                    meteor.right >= spaceship.corner_points[0][0] and
                    meteor.bottom <= spaceship.corner_points[1][1] and
                    meteor.top >= spaceship.corner_points[0][1]):
                meteor.eaten = True
                spaceship.update_fitness()

            inputs = [utils.normalize(meteor.x), utils.normalize(spaceship.x), utils.normalize(meteor.y),
                      utils.normalize(spaceship.y)]

            action = net.activate(inputs)
            spaceship.update(action=action)

            if meteor.eaten:
                meteor.update()
        # out of while loop (1 simulation ended)

        fitnesses.append(spaceship.fitness)

    return statistics.mean(fitnesses)

@game_window.event
def on_draw():
    global spaceship
    global meteor
    game_window.clear()
    meteor.draw()
    spaceship.draw()

def update(dt, net):
    global meteor
    global spaceship

    if spaceship.dead:
        spaceship.reset()
        meteor.reset()

    if (meteor.left <= spaceship.corner_points[1][0] and
            meteor.right >= spaceship.corner_points[0][0] and
            meteor.bottom <= spaceship.corner_points[1][1] and
            meteor.top >= spaceship.corner_points[0][1]):
        meteor.eaten = True
        spaceship.update_fitness()

    inputs = [utils.normalize(meteor.x), utils.normalize(spaceship.x), utils.normalize(meteor.y),
              utils.normalize(spaceship.y)]
    action = net.activate(inputs)
    spaceship.update(action=action)

    if meteor.eaten:
        meteor.update()

def run():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)

    winner = pop.run(pe.evaluate, 1000)

    print(winner)

    winner_net = neat.nn.RecurrentNetwork.create(winner, config)
    game_window.set_visible()
    pyglet.clock.schedule_interval(update, 1 / 60.0, winner_net)
    pyglet.app.run()

if __name__ == '__main__':
    run()

