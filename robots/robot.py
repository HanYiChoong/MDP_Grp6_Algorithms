from map import Map
from utils.constants import BEARING


class Robot:
    def __init__(self, initial_x, initial_y):
        self.x = initial_x
        self.y = initial_y
        self.direction = BEARING['north']
        self.map_manager = Map()
        self.exploration_solver = None

    def move(self):
        raise NotImplementedError
