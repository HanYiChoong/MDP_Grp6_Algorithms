from time import perf_counter

# from map import Map
from utils import constants

_DIRECTIONS = constants.BEARING


# _map_reference = Map()
# _sample_arena = _map_reference.sample_arena


class Exploration:
    def __init__(self, map_object_reference):
        self.robot = None
        self.robot_initial_position = None
        self.map_object_reference = map_object_reference
        self.explored_map = map_object_reference.explored_map
        self.obstacle_map = map_object_reference.obstacle_map
        self.time_limit = None
        self.coverage = None
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.is_simulation = None
        self.has_explored_till_goal = None

    def run_algorithm(self,
                      robot,
                      coverage,
                      time_limit,
                      end_time,
                      is_simulation=True):
        # TODO: Include step and other etc base on requirements
        self.robot = robot
        self.robot_initial_position = [self.robot.x, self.robot.y]
        self.end_time = end_time
        self.coverage = coverage
        self.time_limit = time_limit
        self.is_simulation = is_simulation
        self.has_explored_till_goal = False

        # TODO: Add code to perform calibration if needed
        # TODO: Set start area explored

        self.start_time = self._get_current_time()
        self._start_left_hugging()

    def _start_left_hugging(self):
        # Left wall hugging algo
        while self._is_not_goal_position() and self._get_current_time() < self.end_time:
            # check left side free
            # if left is free (2 cases):
            #
            # if left has not been explored -> turn left and update explored map
            # -> check if obstacles are present -> no obstacles, move forward and mark as explored
            #                                   -> if obstacles are present, turn right (back to original position)
            #
            # if left was explored -> turn left and update explored map
            # -> move forward and mark as explored
            #
            # if not free, check in front of the robot
            #
            # if front not free, turn right
            # else check right side free
            pass

    def _is_not_goal_position(self):
        x, y = self.robot_initial_position

        return self.robot.x != x and self.robot.y != y

    def _set_area_explored(self):
        pass

    def _get_current_time(self):
        return perf_counter()

    def _get_elapsed_time(self):
        return perf_counter() - self.start_time
    #
    # def left_wall_hugging(self):
    #     raise NotImplementedError
