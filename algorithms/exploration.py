from time import perf_counter

from map import Map
from utils import constants

_DIRECTIONS = constants.BEARING
_map_reference = Map()
_sample_arena = _map_reference.sample_arena


class Exploration:
    def __init__(self, explored_map, obstacle_map, path_finder):
        # self.robot = robot
        self.explored_map = explored_map
        self.obstacle_map = obstacle_map
        self.path_finder = path_finder
        self.time_limit = None
        self.delay = None
        self.coverage = None
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.start_point = None
        self.area_explored = 0
        self.step = 1
        self.x = None  # temporary
        self.y = None  # temporary
        self.current_facing_direction = None
        self.is_simulation = None
        self.movements = []

    def run_algorithm(self,
                      delay,
                      coverage,
                      time_limit,
                      end_time,
                      start_point,
                      current_facing_direction,
                      step=1,
                      is_simulation=True):
        self.delay = delay
        self.end_time = end_time
        self.coverage = coverage
        self.time_limit = time_limit
        self.start_point = start_point
        self.current_facing_direction = current_facing_direction
        self.is_simulation = is_simulation
        self.step = step
        self.x = start_point[0]
        self.y = start_point[1]

        self.start_time = self._get_current_time()

    def _start_exploration(self):
        # ASSUMPTIONS: Sensors are placed at the end of the four corners of the robot
        # S1 | N | S2
        # W  |   | E
        # S3 | S | S4
        #
        # Left wall hugging algo
        while self.area_explored < self.coverage and self._get_elapsed_time() < self.time_limit:
            self._determine_next_move()

        if self._get_elapsed_time() >= self.end_time and self.area_explored < 300:
            # return home?
            pass

        if self.area_explored >= 300 and self._get_elapsed_time() < self.end_time:
            # perform fastest path back home
            pass

        else:  # if still have area unexplored
            # iterate explored map to find unexplored map, perform fastest path to the area?
            pass

    def _determine_next_move(self):
        if self._left_direction_is_free():
            self._turn_left()
            self._move_forward()

        elif self._forward_direction_is_free():
            self._move_forward()

        elif self._right_direction_is_free():
            self._turn_right()
            self._move_forward()

    def _left_direction_is_free(self):
        if self.current_facing_direction == _DIRECTIONS['north']:
            if self._west_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['east']:
            if self._north_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['south']:
            if self._east_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['west']:
            if self._south_direction_is_obstacle():
                return False

            return True

    def _forward_direction_is_free(self):
        if self.current_facing_direction == _DIRECTIONS['north']:
            if self._north_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['east']:
            if self._east_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['south']:
            if self._south_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['west']:
            if self._west_direction_is_obstacle():
                return False

            return True

    def _right_direction_is_free(self):
        if self.current_facing_direction == _DIRECTIONS['north']:
            if self._east_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['east']:
            if self._south_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['south']:
            if self._west_direction_is_obstacle():
                return False

            return True

        if self.current_facing_direction == _DIRECTIONS['west']:
            if self._north_direction_is_obstacle():
                return False

            return True

    def _north_direction_is_obstacle(self):
        has_obstacles = False

        if _sample_arena[self.x + 2][self.y - 1] == constants.OBSTACLE:
            self.obstacle_map[self.x + 2][self.y - 1] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x + 2][self.y] == constants.OBSTACLE:
            self.obstacle_map[self.x + 2][self.y] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x + 2][self.y + 1] == constants.OBSTACLE:
            self.obstacle_map[self.x + 2][self.y + 1] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _south_direction_is_obstacle(self):
        has_obstacles = False

        if _sample_arena[self.x - 2][self.y - 1] == constants.OBSTACLE:
            self.obstacle_map[self.x - 2][self.y - 1] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x - 2][self.y] == constants.OBSTACLE:
            self.obstacle_map[self.x - 2][self.y] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x - 2][self.y + 1] == constants.OBSTACLE:
            self.obstacle_map[self.x - 2][self.y + 1] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _east_direction_is_obstacle(self):
        has_obstacles = False

        if _sample_arena[self.x + 1][self.y + 2] == constants.OBSTACLE:
            self.obstacle_map[self.x + 1][self.y + 2] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x][self.y + 2] == constants.OBSTACLE:
            self.obstacle_map[self.x - 1][self.y + 2] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x + 1][self.y + 2] == constants.OBSTACLE:
            self.obstacle_map[self.x - 2][self.y + 1] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _west_direction_is_obstacle(self):
        has_obstacles = False

        if _sample_arena[self.x + 1][self.y - 2] == constants.OBSTACLE:
            self.obstacle_map[self.x + 1][self.y - 2] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x][self.y - 2] == constants.OBSTACLE:
            self.obstacle_map[self.x - 1][self.y - 2] = constants.OBSTACLE
            has_obstacles = True

        if _sample_arena[self.x + 1][self.y - 2] == constants.OBSTACLE:
            self.obstacle_map[self.x - 2][self.y - 2] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _turn_left(self):
        turn_direction = (self.current_facing_direction + 6) % 8
        self.current_facing_direction = _DIRECTIONS[turn_direction]

    def _turn_right(self):
        turn_direction = (self.current_facing_direction + 1) % 8
        self.current_facing_direction = _DIRECTIONS[turn_direction]

    def _move_forward(self):
        if self.current_facing_direction == _DIRECTIONS['north']:
            self.x -= 1
            self._set_explored_on_map(self.x, self.y)

        if self.current_facing_direction == _DIRECTIONS['south']:
            self.x += 1
            self._set_explored_on_map(self.x, self.y)

        if self.current_facing_direction == _DIRECTIONS['east']:
            self.y += 1
            self._set_explored_on_map(self.x, self.y)

        if self.current_facing_direction == _DIRECTIONS['west']:
            self.y -= 1
            self._set_explored_on_map(self.x, self.y)

    def _set_explored_on_map(self, x, y):
        for i in range(3):
            for j in range(3):
                if self.explored_map[x + i - 1][y + j - 1] == constants.UNEXPLORED_CELL:
                    self.explored_map[x + i - 1][y + j - 1] = constants.EXPLORED_CELL
                    self.area_explored += 1

    def _get_current_time(self):
        return perf_counter()

    def _get_elapsed_time(self):
        return perf_counter() - self.start_time

    def left_wall_hugging(self):
        raise NotImplementedError
