from collections import deque
from time import perf_counter
from typing import Callable, List, Union

from algorithms.fastest_path_solver import AStarAlgorithm, Node
from map import is_within_arena_range
from utils import constants
from utils.enums import Cell, Direction, Movement

MIN_STEPS_WITHOUT_CALIBRATION = 3


def _get_current_time():
    return perf_counter()


class Exploration:
    def __init__(self,
                 robot,
                 explored_map: list,
                 obstacle_map: list,
                 on_update_map: Callable = None,
                 on_calibrate: Callable = None,
                 coverage_limit: float = 1,
                 time_limit: float = 6):
        """
        Initialises the exploration algorithm to explore the arena.

        :param robot: The robot that will perform the exploration
        :param explored_map: The reference to keep track of the status of the exploration in the arena
        :param obstacle_map: The reference to keep track of the obstacles detected by the robot in the arena
        :param on_update_map: The callback function to update the map (Mainly used in simulator)
        :param on_calibrate: The callback function after calibrating the robot
        :param coverage_limit: The coverage limit for the robot to explore in the arena
        :param time_limit: The time limit for the robot to explore in the arena
        """
        self.robot = robot
        self.entered_goal = False
        self.previous_point = None
        self.explored_map = explored_map
        self.obstacle_map = obstacle_map
        self.start_time = _get_current_time()
        self.coverage_limit = coverage_limit
        self.is_running = True
        self.time_limit = time_limit
        self.queue = deque([])
        self.steps_without_calibration = 0
        self.on_update_map = on_update_map if on_update_map is not None else lambda: None
        self.on_calibrate = on_calibrate if on_calibrate is not None else lambda: None

    @property
    def coverage(self) -> float:
        """
        Determines the percentage of the arena explored by the robot.

        :return: The coverage percentage in normalized form
        """
        no_of_unexplored_cells = sum(row.count(Cell.UNEXPLORED) for row in self.explored_map)

        return 1 - no_of_unexplored_cells / (constants.ARENA_WIDTH * constants.ARENA_HEIGHT)

    @property
    def time_elapsed(self) -> float:
        """
        The amount of time passed since the start of the exploration

        :return: The elapsed time since the start of the exploration
        """
        return _get_current_time() - self.start_time

    def __time_taken_to_return_to_start_point(self) -> float:
        """
        The time taken to return back to the start area

        :return: The time taken to reach the start area from the robot's current position
        """
        return (AStarAlgorithm.get_h_cost(self.robot, Node(constants.ROBOT_START_POINT))) / self.robot.speed

    @property
    def limit_has_exceeded(self) -> bool:
        """
        Determines if the robot has reached the specified coverage limit or exceeded the time limit specified.

        NOTE: Time limit is NOT ACCOUNTED for at the moment. Will be included in future
        :return: True if either coverage or time limit has exceeded
        """
        coverage_limit_has_exceeded = self.coverage_limit is not None and self.coverage_limit < self.coverage
        # time_limit_has_exceeded = self.time_limit is not None and \
        #                           self.time_limit < self.time_elapsed + self.__time_taken_to_return_to_start_point()

        # return not self.is_running or coverage_limit_has_exceeded or time_limit_has_exceeded
        return not self.is_running or coverage_limit_has_exceeded

    def get_surrounding_offsets(self, movement: 'Movement') -> List[List[int]]:
        """
        Gets the offsets of the neighbouring cells of the robot.

        :param movement: The moving direction of the robot
        :return: List of neighbouring position offsets of the robot
        """
        robot_current_direction = self.robot.direction

        if movement == Movement.RIGHT:
            robot_current_direction = Direction.get_clockwise_direction(robot_current_direction)

        elif movement == Movement.LEFT:
            robot_current_direction = Direction.get_anti_clockwise_direction(robot_current_direction)

        elif movement == Movement.BACKWARD:
            # Flip twice
            robot_current_direction = Direction.get_clockwise_direction(robot_current_direction)
            robot_current_direction = Direction.get_clockwise_direction(robot_current_direction)

        if robot_current_direction == Direction.NORTH:
            # Inverted from referred code
            # TODO: Swap x and y if index out of range error in map
            return [[-2, 0], [-2, -1], [-2, 1]]

        if robot_current_direction == Direction.EAST:
            # Inverted from referred code
            # TODO: Swap x and y if index out of range error in map
            return [[0, 2], [-1, 2], [1, 2]]

        if robot_current_direction == Direction.SOUTH:
            # Inverted from referred code
            # TODO: Swap x and y if index out of range error in map
            return [[2, 0], [2, -1], [2, 1]]

        # West direction
        # Inverted from referred code
        # TODO: Swap x and y if index out of range error in map
        return [[0, -2], [1, -2], [-1, -2]]

    def neighbouring_cells_do_not_have_obstacles(self, movement: 'Movement') -> bool:
        """
        Determines if the neighbouring cell is an obstacle or free area.

        :param movement: The moving direction of the robot
        :return: True if the neighbouring cell is not an obstacle. Else False
        """
        robot_current_point = self.robot.point
        for x, y in self.get_surrounding_offsets(movement):
            robot_right_point_x = robot_current_point[0] + x
            robot_right_point_y = robot_current_point[1] + y

            if not is_within_arena_range(robot_right_point_x, robot_right_point_y) or \
                    self.obstacle_map[robot_right_point_x][robot_right_point_y] == Cell.OBSTACLE:
                return False

        return True

    def right_of_robot_is_free(self) -> bool:
        """
        Determines if the right of the robot contains obstacles

        :return: True if the right of the robot does not have obstacles. Else False
        """
        return self.neighbouring_cells_do_not_have_obstacles(Movement.RIGHT)

    def front_of_robot_is_free(self) -> bool:
        """
        Determines if the front of the robot contains obstacles

        :return: True if the front of the robot does not have obstacles. Else False
        """
        return self.neighbouring_cells_do_not_have_obstacles(Movement.FORWARD)

    def left_of_robot_is_free(self) -> bool:
        """
        Determines if the left of the robot contains obstacles

        :return: True if the left of the robot does not have obstacles. Else False
        """
        is_not_an_obstacle = self.neighbouring_cells_do_not_have_obstacles(Movement.LEFT)

        # Move the condition below if changing to right wall hugging
        if is_not_an_obstacle and self.previous_point != self.find_left_point_of_robot():
            return True

        return False

    def find_left_point_of_robot(self) -> List[int]:
        """
        Determines the left position of the robot.

        :return: The coordinates of the left position of the robot. Format: [x, y]
        """
        robot_left_direction = Direction.get_anti_clockwise_direction(self.robot.direction)
        direction_offset = Direction.get_direction_offset(robot_left_direction)

        new_point_x = self.robot.point[0] + direction_offset[0]
        new_point_y = self.robot.point[1] + direction_offset[1]

        return [new_point_x, new_point_y]

    def is_safe_point_to_explore(self, point: List[int], consider_unexplored: bool = True) -> bool:
        """
        Determines if the neighbouring cell is safe to explore.
        Unsure of the usage of this function currently. Meant for fastest path to the unexplored cell in the arena

        :param point: The current position of the robot. Format: [x, y]
        :param consider_unexplored: The boolean flag to consider if the cell is unexplored.
        :return:
        """
        x, y = point

        if not (1 <= x <= 18) and not (1 <= y <= 13):
            return False

        for row in range(x - 1, x + 2):
            for col in range(y - 1, y + 2):
                if self.obstacle_map[row][col] == Cell.OBSTACLE or \
                        (consider_unexplored and self.explored_map[row][col] == Cell.UNEXPLORED):
                    return False

        return True

    def determine_possible_cell_point_and_direction(self, destination_point: list) -> set:
        # TODO: Implement this after finishing the hugging algo
        raise NotImplementedError

    def find_possible_unexplored_cells(self):
        # TODO: Implement this after finishing the hugging algo
        raise NotImplementedError

    def explore_unexplored_cells(self):
        # TODO: Implement this after finishing the hugging algo
        raise NotImplementedError

    def run_fastest_path_to_start_point(self):
        # TODO: Implement this after finishing the hugging algo
        raise NotImplementedError

    def sense_and_repaint_canvas(self, sensor_values: List[Union[int, None]] = None) -> None:
        """
        Determine if the neighbouring cells of the robot are explored, free area or obstacles and updates the arena

        :param sensor_values: The actual sensors readings from the RPI module
        """
        if sensor_values is None:
            sensor_values = self.robot.sense()

        for i in range(len(sensor_values)):
            obstacle_distance_from_the_sensor = sensor_values[i]

            if obstacle_distance_from_the_sensor == -1:
                continue

            sensor = self.robot.sensor_offset_points[i]
            direction_offset = Direction.get_direction_offset(sensor.get_current_direction(self.robot.direction))
            current_sensor_point = sensor.get_current_point(self.robot)
            sensor_range = sensor.get_sensor_range()

            # TODO: Consider if we want to mark area sensed by robot as explored
            if obstacle_distance_from_the_sensor is None:
                self.mark_cell_as_explored(current_sensor_point, direction_offset, sensor_range)

            else:
                upper_loop_bound = min(sensor_range[1], obstacle_distance_from_the_sensor + 1)
                updated_sensor_range = [sensor_range[0], upper_loop_bound]

                self.mark_cell_as_explored(current_sensor_point, direction_offset, updated_sensor_range,
                                           obstacle_distance_from_the_sensor)

        # Update canvas here
        # self.on_update_map()

    def mark_cell_as_explored(self,
                              current_sensor_point: List[int],
                              direction_offset: List[int],
                              sensor_range: List[int],
                              obstacle_distance_from_the_sensor: Union[None, int] = None) -> None:
        """
        Marks the cell explored from the sensors of the robot on the explored arena reference

        :param current_sensor_point: current sensor coordinate relative to the robot's direction
        :param direction_offset: Offset coordinate of the sensor's direction'
        :param sensor_range: The range of the sensor
        :param obstacle_distance_from_the_sensor:
        """
        for j in range(sensor_range[0], sensor_range[1]):
            cell_point_to_mark = [current_sensor_point[0] + j * direction_offset[0],
                                  current_sensor_point[1] + j * direction_offset[1]]

            if not (0 <= cell_point_to_mark[0] < constants.ARENA_HEIGHT) or \
                    not (0 <= cell_point_to_mark[1] < constants.ARENA_WIDTH):
                continue

            self.explored_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.EXPLORED.value

            if obstacle_distance_from_the_sensor is None or j != obstacle_distance_from_the_sensor:
                continue

            self.obstacle_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.OBSTACLE.value

    def mark_robot_area_as_explored(self, x: int, y: int) -> None:
        """
        Marks the area of the robot as explored

        :param x: The current x coordinate of the robot
        :param y: The current y coordinate of the robot
        """
        for row_index in range(x - 1, x + 2):
            for column_index in range(y - 1, y + 2):
                self.explored_map[row_index][column_index] = Cell.EXPLORED.value

    def start_exploration(self) -> None:
        """
        Runs the exploration algorithm

        """
        self.start_time = _get_current_time()
        self.sense_and_repaint_canvas()
        self.mark_robot_area_as_explored(self.robot.point[0], self.robot.point[1])
        self.left_hug()
        print('Done left hug')
        # TODO: Add code to explore remaining unexplored area
        # TODO: Add code to find fastest path back to start point

    def move(self, movement: 'Movement', is_real_run: bool = False) -> None:
        """
        Moves the robot, updates it's position in the simulator and marks the area of the robot as explored

        :param movement: The movement direction to be made by the robot
        :param is_real_run: Have no purpose currently. Might be removed in the future
        """
        self.queue.append(movement)

        # TODO: Might change to fixed length queue in the future
        if len(self.queue) > 6:
            self.queue.popleft()

        if not isinstance(movement, Movement) or movement == Movement.FORWARD or movement == Movement.BACKWARD:
            self.previous_point = self.robot.point

        sensor_values = self.robot.move(movement)

        # if is_real_run:
        #     self.sense_and_repaint_canvas(sensor_values)
        self.sense_and_repaint_canvas(sensor_values)

        robot_x_point = self.robot.point[0]
        robot_y_point = self.robot.point[1]

        self.mark_robot_area_as_explored(robot_x_point, robot_y_point)

        # self.calibrate(is_real_run)
        self.steps_without_calibration += 1

    def left_hug(self) -> None:
        """
        Left hug the wall in the arena and move around it
        """
        while not (self.limit_has_exceeded or
                   (self.entered_goal and self.robot.point == constants.ROBOT_START_POINT)):

            if self.robot.point == constants.ROBOT_END_POINT:
                self.entered_goal = True

            # handle case where stuck in loop

            if self.left_of_robot_is_free():
                self.move(Movement.LEFT)
                continue

            if self.front_of_robot_is_free():
                self.move(Movement.FORWARD)
                continue

            if self.right_of_robot_is_free():
                self.move(Movement.RIGHT)
                continue

            # Turn to the opposite direction to find alternative route
            self.move(Movement.RIGHT)
            self.move(Movement.RIGHT)

    def calibrate(self, is_real_run: bool) -> None:
        # I have no idea what this calibration is for...
        # Copy pasted and inverted for fun, joy and laughter till we know what its doing
        is_calibrated = False
        current_robot_direction = self.robot.direction
        robot_left_direction = Direction.get_anti_clockwise_direction(current_robot_direction)
        current_direction_offset = Direction.get_direction_offset(current_robot_direction)
        left_direction_offset = Direction.get_direction_offset(robot_left_direction)

        can_calibrate_front = False
        for i in range(-1, 2):
            row_index = self.robot.point[0] + 2 * current_direction_offset[0] + i * left_direction_offset[0]
            column_index = self.robot.point[1] + 2 * current_direction_offset[1] + i * left_direction_offset[1]

            if (not (0 <= row_index < constants.ARENA_HEIGHT) and not (0 <= column_index < constants.ARENA_WIDTH)) or \
                    self.explored_map[row_index][column_index] == Cell.OBSTACLE:
                can_calibrate_front = True
                break

        if can_calibrate_front:
            self.on_calibrate(is_front=True)
            is_calibrated = True

        if self.steps_without_calibration >= MIN_STEPS_WITHOUT_CALIBRATION:
            can_calibrate_left = True

            for i in [-1, 1]:
                row_index = self.robot.point[0] + i * current_direction_offset[0] + 2 * left_direction_offset[0]
                column_index = self.robot.point[1] + i * current_direction_offset[1] + 2 * left_direction_offset[1]

                if 0 <= row_index < constants.ARENA_HEIGHT and \
                        0 <= column_index < constants.ARENA_WIDTH and \
                        self.explored_map[row_index][column_index] != Cell.OBSTACLE:
                    can_calibrate_left = False

            if can_calibrate_left:
                self.on_calibrate(is_front=False)
                self.steps_without_calibration = 0
                is_calibrated = True

        if is_calibrated and is_real_run:
            self.sense_and_repaint_canvas()


if __name__ == '__main__':
    from map import Map
    from robots.robot import SimulatorBot

    test_map = Map()

    exp_area = test_map.explored_map
    obs_arena = test_map.obstacle_map
    sample_arena = test_map.sample_arena

    bot = SimulatorBot(constants.ROBOT_START_POINT,
                       sample_arena,
                       Direction.NORTH,
                       lambda m: None)

    exploration_algo = Exploration(bot, exp_area, obs_arena)
    exploration_algo.start_exploration()
    print(exploration_algo.explored_map)
    print(exploration_algo.obstacle_map)
