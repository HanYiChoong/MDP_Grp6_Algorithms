from collections import deque
from typing import Callable

from utils import constants
from utils.enums import Cell, Movement


class Exploration:
    def __init__(self,
                 robot,
                 explored_map: list,
                 on_update_map: Callable = None,
                 on_calibrate: Callable = None,
                 coverage_limit: int = 100,
                 time_limit: float = 6):
        self.robot = robot
        self.entered_goal = False
        self.previous_point = None
        self.explored_map = explored_map
        self.start_time = None
        self.coverage_limit = coverage_limit
        self.is_running = True
        self.time_limit = time_limit
        self.queue = deque([])
        self.on_update_map = on_update_map if on_update_map is not None else lambda: None
        self.on_calibrate = on_calibrate if on_calibrate is not None else lambda: None

    @property
    def coverage(self) -> float:
        no_of_unexplored_cells = sum(row.count(Cell.UNEXPLORED) for row in self.explored_map)

        return 1 - no_of_unexplored_cells / (constants.ARENA_WIDTH * constants.ARENA_HEIGHT)

    @property
    def limit_has_exceeded(self):
        coverage_limit_has_exceeded = self.coverage_limit is not None and self.coverage_limit < self.coverage
        # TODO: Add time limit check
        # time limit check, if current time does not exceed time limit + the manhattan distance between
        # robot current position to the start position
        return

    def start_exploring(self):
        raise NotImplementedError

    def find_left_position(self) -> list:
        raise NotImplementedError

    def check_surroundings(self, movement: 'Movement') -> list:
        raise NotImplementedError

    def check_right_of_robot(self) -> bool:
        raise NotImplementedError

    def check_front_of_robot(self) -> bool:
        raise NotImplementedError

    def check_left_of_robot(self) -> bool:
        raise NotImplementedError

    def is_safe_point_to_explore(self, point: list, consider_unexplored: bool = True) -> bool:
        raise NotImplementedError

    def find_possible_unexplored_cells(self):
        raise NotImplementedError

    def explore_unexplored_cells(self):
        raise NotImplementedError

    def run_fastest_path_to_start_point(self):
        raise NotImplementedError

    def move(self):
        raise NotImplementedError

    def sense(self):
        raise NotImplementedError

    def left_hug(self):
        raise NotImplementedError
