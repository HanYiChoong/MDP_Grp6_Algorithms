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
        # Set start area explored
        self._set_explored_on_map(self.robot.x, self.robot.y)

        self.start_time = self._get_current_time()
        self._start_left_hugging()

    def _start_left_hugging(self):
        # Left wall hugging algo
        while self._is_not_goal_position() and self._get_current_time() < self.end_time:
            # check left side free
            if self._left_direction_is_free():
                # turn robot
                self._turn_left()
                # check if front is free

            # else check front side free
            # else check right side free
            pass

    def _is_not_goal_position(self):
        x, y = self.robot_initial_position

        return self.robot.x != x and self.robot.y != y

    # def _determine_next_move(self):
    #     if self._left_direction_is_free():
    #         self._turn_left()
    #         self._move_forward()
    #
    #     elif self._forward_direction_is_free():
    #         self._move_forward()
    #
    #     elif self._right_direction_is_free():
    #         self._turn_right()
    #         self._move_forward()
    #
    def _left_direction_is_free(self):
        if self.robot.direction == _DIRECTIONS['north']:
            next_x = self.robot.x
            next_y = self.robot.y - 1

            if self._west_direction_has_obstacle(next_x, next_y):
                return False

            return True

        if self.robot.direction == _DIRECTIONS['east']:
            next_x = self.robot.x + 1
            next_y = self.robot.y
            if self._north_direction_is_obstacle(next_x, next_y):
                return False

            return True

        if self.robot.direction == _DIRECTIONS['south']:
            next_x = self.robot.x
            next_y = self.robot.y + 1
            if self._east_direction_is_obstacle(next_x, next_y):
                return False

            return True

        if self.robot.direction == _DIRECTIONS['west']:
            next_x = self.robot.x + 1
            next_y = self.robot.y
            if self._south_direction_is_obstacle(next_x, next_y):
                return False

            return True

    # def _forward_direction_is_free(self):
    #     if self.current_facing_direction == _DIRECTIONS['north']:
    #         if self._north_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['east']:
    #         if self._east_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['south']:
    #         if self._south_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['west']:
    #         if self._west_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    # def _right_direction_is_free(self):
    #     if self.current_facing_direction == _DIRECTIONS['north']:
    #         if self._east_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['east']:
    #         if self._south_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['south']:
    #         if self._west_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    #     if self.current_facing_direction == _DIRECTIONS['west']:
    #         if self._north_direction_is_obstacle():
    #             return False
    #
    #         return True
    #
    def _north_direction_is_obstacle(self, x, y):
        # update obstacle map and return boolean flag
        has_obstacles = False
        sample_arena = self.map_object_reference.SAMPLE_ARENA
        next_x = x + 1

        if next_x >= constants.ARENA_HEIGHT:
            return has_obstacles

        if sample_arena[next_x][y - 1] == constants.OBSTACLE:
            self.obstacle_map[next_x][y - 1] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[next_x][y] == constants.OBSTACLE:
            self.obstacle_map[next_x][y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[next_x][y + 1] == constants.OBSTACLE:
            self.obstacle_map[next_x][y + 1] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _south_direction_is_obstacle(self, x, y):
        # update obstacle map and return boolean flag
        has_obstacles = False
        sample_arena = self.map_object_reference.SAMPLE_ARENA
        next_x = x - 1

        if next_x < 0:
            return has_obstacles

        if sample_arena[next_x][y - 1] == constants.OBSTACLE:
            self.obstacle_map[next_x][y - 1] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[next_x][y] == constants.OBSTACLE:
            self.obstacle_map[next_x][y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[next_x][y + 1] == constants.OBSTACLE:
            self.obstacle_map[next_x][y + 1] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _east_direction_is_obstacle(self, x, y):
        # update obstacle map and return boolean flag
        has_obstacles = False
        sample_arena = self.map_object_reference.SAMPLE_ARENA
        next_y = y + 1

        if next_y >= constants.ARENA_WIDTH:
            return has_obstacles

        if sample_arena[x + 1][next_y] == constants.OBSTACLE:
            self.obstacle_map[x + 1][next_y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[x][next_y] == constants.OBSTACLE:
            self.obstacle_map[x - 1][next_y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[x + 1][next_y] == constants.OBSTACLE:
            self.obstacle_map[x - 2][next_y] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _west_direction_has_obstacle(self, x, y):
        # update obstacle map and return boolean flag
        has_obstacles = False
        sample_arena = self.map_object_reference.SAMPLE_ARENA
        next_y = y - 2

        if next_y < 0:
            return has_obstacles

        if sample_arena[x + 1][next_y] == constants.OBSTACLE:
            self.obstacle_map[x + 1][next_y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[x][next_y] == constants.OBSTACLE:
            self.obstacle_map[x - 1][next_y] = constants.OBSTACLE
            has_obstacles = True

        if sample_arena[x + 1][next_y] == constants.OBSTACLE:
            self.obstacle_map[x - 2][next_y] = constants.OBSTACLE
            has_obstacles = True

        return has_obstacles

    def _turn_left(self):
        turn_direction = (self.robot.direction + 6) % 8
        self.robot.direction = turn_direction

    # def _turn_right(self):
    #     turn_direction = (self.current_facing_direction + 1) % 8
    #     self.current_facing_direction = _DIRECTIONS[turn_direction]
    #
    # def _move_forward(self):
    #     if self.current_facing_direction == _DIRECTIONS['north']:
    #         self.x -= 1
    #         self._set_explored_on_map(self.x, self.y)
    #
    #     if self.current_facing_direction == _DIRECTIONS['south']:
    #         self.x += 1
    #         self._set_explored_on_map(self.x, self.y)
    #
    #     if self.current_facing_direction == _DIRECTIONS['east']:
    #         self.y += 1
    #         self._set_explored_on_map(self.x, self.y)
    #
    #     if self.current_facing_direction == _DIRECTIONS['west']:
    #         self.y -= 1
    #         self._set_explored_on_map(self.x, self.y)
    #
    def _set_explored_on_map(self, x, y):
        for i in range(3):
            for j in range(3):
                if self.explored_map[x + i - 1][y + j - 1] == constants.UNEXPLORED_CELL:
                    self.explored_map[x + i - 1][y + j - 1] = constants.EXPLORED_CELL

    def _get_current_time(self):
        return perf_counter()

    def _get_elapsed_time(self):
        return perf_counter() - self.start_time
    #
    # def left_wall_hugging(self):
    #     raise NotImplementedError
