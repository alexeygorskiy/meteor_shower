import spaceshipobject
import meteorobject
import random

"""
    :returns an array of all the raypoints at the current object coordinates
"""
def get_raypoints(object):
    hw = (object.width / 2)
    hh = (object.height / 2)

    pt1 = [object.x - hw - object.sight, object.y]
    pt2 = [pt1[0], pt1[1] + hh + object.sight]

    pt3 = [object.x, object.y + hh + object.sight]
    pt4 = [pt3[0] + hw + object.sight, pt3[1]]

    pt5 = [object.x + hw + object.sight, object.y]
    pt6 = [pt5[0], pt5[1] - hh - object.sight]

    pt7 = [object.x, object.y - hh - object.sight]
    pt8 = [pt7[0] - hw - object.sight, pt7[1]]

    return [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]

def is_outside_map(x, y):
    return not (0 <= x <= 800 and 0 <= y <= 800)

"""
    :returns [bottom_left corner, top_right corner]
"""
def get_corner_points(object):
    bottom_left = [object.x - (object.width / 2), object.y - (object.height) / 2]
    top_right = [object.x + (object.width / 2), object.y + (object.height) / 2]

    return [bottom_left, top_right]

def get_spawn_coords(object):
    # meteor spawn logic
    if isinstance(object, meteorobject.MeteorObject):
        area = random.randint(0, 3)
        if area == 0:
            return random.randint(5, 795), 795
        elif area == 1:
            return 795, random.randint(5, 795)
        elif area == 2:
            return random.randint(5, 795), 5
        else:
            return 5, random.randint(5, 795)

    # spaceship spawn logic
    elif isinstance(object, spaceshipobject.SpaceshipObject):
        return random.randint(60, 740), random.randint(60, 740)

    # if object is none of the above raise an exception
    else:
        raise Exception("get_spawn_coords: invalid input object")

"""
    Sets an image's anchor point to its center
"""
def center_img(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2


"""
    returns the weights and indices of the best individuals from the population equal to the number_of_parents variable 
    :returns (array of best weights, array of best indices)
"""
def find_best_parent_weights(spaceships, number_of_parents):
    spaceships_dict = {}

    for i in range(len(spaceships)):
        spaceships_dict[i] = spaceships[i].fitness

    # sort by fitness in descending order
    spaceships_dict = sorted(spaceships_dict.items(), key=lambda x: x[1], reverse=True)

    best_weights = []
    best_spaceship_indices = []
    # only loop through from the first element and up to the number_of_parents variable
    for key_val_pair in spaceships_dict[:number_of_parents]:
        # key_val_pair[0]: index in the spaceships array, key_val_pair[1]: fitness of that spaceship
        best_weights.append(spaceships[key_val_pair[0]].brain.model.get_weights())
        best_spaceship_indices.append(key_val_pair[0])

    # returns a tuple
    return best_weights, best_spaceship_indices


