from collections import deque
from copy import deepcopy
from time import perf_counter
from typing import Callable, Dict, List, Tuple, Union

from algorithms.fastest_path_solver import AStarAlgorithm, Node
from map import is_within_arena_range, Map
from utils import constants
from utils.enums import Cell, Direction, Movement
from utils.logger import print_general_log, print_error_log

_MAX_QUEUE_LENGTH = 6
_STUCK_IN_LOOP_MOVEMENT_BEHAVIOUR = [Movement.FORWARD, Movement.RIGHT, Movement.FORWARD, Movement.RIGHT,
                                     Movement.FORWARD, Movement.RIGHT]


def get_current_time_in_seconds() -> float:
    return perf_counter()


def get_default_exploration_duration() -> float:
    default_time_in_minutes = 6

    return default_time_in_minutes * 60


class Exploration:
    def __init__(self,
                 robot,
                 explored_map: list,
                 obstacle_map: list,
                 on_update_map: Callable = None,
                 on_calibrate: Callable = None,
                 coverage_limit: float = 1,
                 time_limit: float = get_default_exploration_duration()):
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
        self.coverage_limit = coverage_limit
        self.time_limit = time_limit
        self.is_running = True
        self.fastest_path_solver = AStarAlgorithm(obstacle_map)
        self.start_time = get_current_time_in_seconds()
        self.queue = deque(maxlen=_MAX_QUEUE_LENGTH)  # Keeps a history of movements made by the robot
        self.on_update_map = on_update_map if on_update_map is not None else lambda t: None
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
        return get_current_time_in_seconds() - self.start_time

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

        :return: True if either coverage or time limit has exceeded
        """
        coverage_limit_has_exceeded = self.coverage_limit is not None and self.coverage_limit < self.coverage
        time_limit_has_exceeded = self.time_limit is not None and \
                                  self.time_limit < self.time_elapsed + self.__time_taken_to_return_to_start_point()

        return not self.is_running or coverage_limit_has_exceeded or time_limit_has_exceeded
        # return not self.is_running or coverage_limit_has_exceeded

    def start_exploration(self) -> None:
        """
        Runs the exploration algorithm
        """
        self.start_time = get_current_time_in_seconds()
        self.sense_and_repaint_canvas()
        self.mark_robot_area_as_explored(self.robot.point[0], self.robot.point[1])
        self.right_hug()
        print_general_log('Done right hug. Checking for unexplored cells now...')

        self.explore_unexplored_cells()
        print_general_log('Done exploring unexplored cells. Returning home now...')

        self.go_home()
        print_general_log('Reached home!')

    def sense_and_repaint_canvas(self, sensor_values: List[Union[int, None]] = None) -> None:
        """
        Determine if the neighbouring cells of the robot are explored, free area or obstacles and updates the arena

        :param sensor_values: The actual sensors readings from the RPI module
        """
        if sensor_values is None:  # This condition is true when running the simulation
            sensor_values = self.robot.sense()

        for i in range(len(sensor_values)):
            obstacle_distance_from_the_sensor = sensor_values[i]

            if obstacle_distance_from_the_sensor == -1:
                continue

            sensor = self.robot.sensor_offset_points[i]
            direction_offset = Direction.get_direction_offset(sensor.get_current_direction(self.robot.direction))
            current_sensor_point = sensor.get_current_point(self.robot.point, self.robot.direction)
            sensor_range = sensor.get_sensor_range()

            if obstacle_distance_from_the_sensor is None:
                self.mark_cell_as_explored(current_sensor_point, direction_offset, sensor_range)

            else:
                upper_loop_bound = min(sensor_range[1], obstacle_distance_from_the_sensor + 1)
                updated_sensor_range = [sensor_range[0], upper_loop_bound]

                self.mark_cell_as_explored(current_sensor_point, direction_offset, updated_sensor_range,
                                           obstacle_distance_from_the_sensor)

    def mark_cell_as_explored(self,
                              current_sensor_point: Tuple[int],
                              direction_offset: List[int],
                              sensor_range: List[int],
                              obstacle_distance_from_the_sensor: Union[None, int] = None) -> None:
        """
        Marks the cell explored from the sensors of the robot on the explored arena reference \n
        Marks the obstacle on the obstacle arena reference as well.

        :param current_sensor_point: Current sensor coordinate relative to the robot's direction
        :param direction_offset: Offset coordinate of the sensor's direction'
        :param sensor_range: The range of the sensor
        :param obstacle_distance_from_the_sensor: The distance from the sensor on the robot to obstacle
        """
        for j in range(sensor_range[0], sensor_range[1]):
            cell_point_to_mark = [current_sensor_point[0] + j * direction_offset[0],
                                  current_sensor_point[1] + j * direction_offset[1]]

            if not is_within_arena_range(cell_point_to_mark[0], cell_point_to_mark[1]):
                continue

            self.explored_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.EXPLORED.value
            self.on_update_map(cell_point_to_mark)

            if obstacle_distance_from_the_sensor is None or j != obstacle_distance_from_the_sensor:
                continue

            self.obstacle_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.OBSTACLE.value

            self.on_update_map(cell_point_to_mark)

    def right_hug(self) -> None:
        """
        Left hug the wall in the arena and move around it
        """
        while not (self.limit_has_exceeded or
                   (self.entered_goal and self.robot.point == constants.ROBOT_START_POINT)):

            if self.robot.point == constants.ROBOT_END_POINT:
                self.entered_goal = True

            # TODO: Check movement queue to see if the robot is stuck in a loop
            if self.is_stuck_in_a_loop():
                self.move(Movement.RIGHT)
                self.move(Movement.RIGHT)
                continue

            if self.right_of_robot_is_free():
                self.move(Movement.RIGHT)
                continue

            if self.front_of_robot_is_free():
                self.move(Movement.FORWARD)
                continue

            if self.left_of_robot_is_free():
                self.move(Movement.LEFT)
                continue

            # Turn to the opposite direction to find alternative route
            self.move(Movement.RIGHT)
            self.move(Movement.RIGHT)

    def is_stuck_in_a_loop(self):
        return list(self.queue) == _STUCK_IN_LOOP_MOVEMENT_BEHAVIOUR

    def right_of_robot_is_free(self) -> bool:
        """
        Determines if the right of the robot contains obstacles

        :return: True if the right of the robot does not have obstacles. Else False
        """
        is_not_an_obstacle = self.neighbouring_cells_do_not_have_obstacles(Movement.RIGHT)

        # Move the condition below if changing to right wall hugging
        if is_not_an_obstacle and self.previous_point != self.find_right_point_of_robot():
            return True

        return False

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
        return self.neighbouring_cells_do_not_have_obstacles(Movement.LEFT)

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

    def find_right_point_of_robot(self) -> List[int]:
        """
        Determines the left position of the robot.

        :return: The coordinates of the left position of the robot. Format: [x, y]
        """
        robot_right_direction = Direction.get_clockwise_direction(self.robot.direction)
        direction_offset = Direction.get_direction_offset(robot_right_direction)

        new_point_x = self.robot.point[0] + direction_offset[0]
        new_point_y = self.robot.point[1] + direction_offset[1]

        return [new_point_x, new_point_y]

    def move(self, movement: 'Movement') -> None:
        """
        Moves the robot, updates it's position in the simulator and marks the area of the robot as explored

        :param movement: The movement direction to be made by the robot
        """
        self.queue.append(movement)

        if not isinstance(movement, Movement) or movement == Movement.FORWARD or movement == Movement.BACKWARD:
            self.previous_point = self.robot.point

        sensor_values = self.robot.move(movement)

        self.sense_and_repaint_canvas(sensor_values)

        robot_x_point = self.robot.point[0]
        robot_y_point = self.robot.point[1]

        self.mark_robot_area_as_explored(robot_x_point, robot_y_point)

    def mark_robot_area_as_explored(self, x: int, y: int) -> None:
        """
        Marks the area of the robot as explored

        :param x: The current x coordinate of the robot
        :param y: The current y coordinate of the robot
        """
        for row_index in range(x - 1, x + 2):
            for column_index in range(y - 1, y + 2):
                self.explored_map[row_index][column_index] = Cell.EXPLORED.value

    def explore_unexplored_cells(self) -> None:
        """
        Checks for unexplored cells in the arena and explore them
        """
        while True:
            if self.limit_has_exceeded:
                return

            neighbours_of_unexplored_cells = self.find_neighbours_of_all_unexplored_cells()
            is_explored = self.move_to_best_path_of_nearest_unexplored_cell(neighbours_of_unexplored_cells)

            if not is_explored:
                return

    def find_neighbours_of_all_unexplored_cells(self) -> Dict[tuple, 'Direction']:
        """
        Determines neighbouring coordinates and the direction to face in order to reach the unexplored node

        :return: A dictionary of all possible neighbouring coordinates and robot facing direction
        """
        points_to_check = {}

        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                if self.explored_map[x][y] == Cell.UNEXPLORED:
                    for point, direction in self.determine_possible_cell_point_and_direction([x, y]):
                        points_to_check[point] = direction

        return points_to_check

    def determine_possible_cell_point_and_direction(self, destination_point: List[int]) -> set:
        """
        Determine the neighbouring cell of the unexplored cell is safe to enter and the direction to face in order to
        reach the unexplored node

        :param destination_point: The point of the unexplored cell in the arena
        :return: A set of neighbouring points and the robot facing direction to reach the unexplored cell.
        """
        set_of_possible_cells = set()

        x, y = destination_point
        neighbour_cell_offsets = [(0, -2), (-1, -2), (1, -2), (0, 2), (-1, 2), (1, 2), (2, 0), (2, -1), (2, 1),
                                  (-2, 0), (-2, 1), (-2, -1)]

        for offset_point in neighbour_cell_offsets:
            neighbour_point = (x + offset_point[0], y + offset_point[1])

            if self.is_safe_point_to_explore(neighbour_point) and \
                    not (neighbour_point[0] == self.robot.point[0] and neighbour_point[1] == self.robot.point[1]):
                if neighbour_point[0] - x == 2:
                    direction = Direction.NORTH
                elif neighbour_point[0] - x == -2:
                    direction = Direction.SOUTH
                elif neighbour_point[1] - y == 2:
                    direction = Direction.WEST
                elif neighbour_point[1] - y == -2:
                    direction = Direction.EAST

                else:
                    raise ValueError('Invalid direction given')

                set_of_possible_cells.add((neighbour_point, direction))

        return set_of_possible_cells

    def is_safe_point_to_explore(self,
                                 point_of_interest: Tuple[int, int],
                                 consider_unexplored_cells: bool = True) -> bool:
        """
        Determine if the neighbouring cell of the unexplored cell is safe to explore. \n
        The conditions for safe to explore are: \n
        > The neighbouring cell is not an obstacle \n
        > The neighbouring cell is explored previously during the hugging

        :param point_of_interest: The neighbouring cell coordinates
        :param consider_unexplored_cells: True if considering unexplored cells in the check. Else False
        :return: True if the neighbouring cell is safe to explore. Else False
        """
        x, y = point_of_interest

        # Not within the range of arena with virtual wall padded around it
        if not (1 <= x <= constants.ARENA_HEIGHT - 2) or not (1 <= y <= constants.ARENA_WIDTH - 2):
            return False

        for column_index in range(x - 1, x + 2):
            for row_index in range(y - 1, y + 2):
                if self.obstacle_map[column_index][row_index] == Cell.OBSTACLE or \
                        (consider_unexplored_cells and self.explored_map[column_index][row_index] == Cell.UNEXPLORED):
                    return False

        return True

    def move_to_best_path_of_nearest_unexplored_cell(self, unexplored_cells_to_check: Dict[tuple, 'Direction']) -> bool:
        """
        Determines the neighbour of the nearest unexplored cell and finds the best path to that neighbour cell.

        The nearest unexplored cell is determined by the manhattan distance from the robot's current position to the
        neighbour of the unexplored cell.

        :param unexplored_cells_to_check: A dictionary of all possible neighbouring coordinates and robot facing
                                          direction
        :return: True if the robot is able to explore the unexplored cell. Else False
        """
        if len(unexplored_cells_to_check) <= 0:
            return False

        robot_point = self.robot.point
        robot_facing_direction = self.robot.direction
        nearest_node_to_robot = min(unexplored_cells_to_check.keys(),
                                    key=lambda destination_point: AStarAlgorithm.get_h_cost(Node(robot_point),
                                                                                            Node(destination_point)))

        list_of_movements = self.find_fastest_path_to_node(robot_point, nearest_node_to_robot, robot_facing_direction)

        if list_of_movements is None:
            return False

        direction_to_face_nearest_node = unexplored_cells_to_check[nearest_node_to_robot]
        self.move_robot_to_destination_cell(list_of_movements, direction_to_face_nearest_node)

        return True

    def find_fastest_path_to_node(self, robot_point, destination_point, robot_facing_direction):
        """
        Determines the fastest path from the robot's position to the neighbour of the unexplored cell

        :param robot_point: The robot's current position
        :param destination_point: The neighbour coordinates of the unexplored cell
        :param robot_facing_direction: The robot's current facing
        :return: List of movements to the neighbour of the unexplored cell
        """
        # copy obstacle map
        obstacle_map_copy = deepcopy(self.obstacle_map)
        # add virtual wall to the current obstacle map
        Map.set_virtual_walls_on_map(obstacle_map_copy, self.explored_map)
        self.fastest_path_solver.arena = obstacle_map_copy
        path = self.fastest_path_solver.run_algorithm_for_exploration(robot_point,
                                                                      destination_point,
                                                                      robot_facing_direction)
        if path is None or len(path) <= 0:
            return

        return self.fastest_path_solver.convert_fastest_path_to_movements(path, robot_facing_direction)

    def move_robot_to_destination_cell(self,
                                       list_of_movements: List[Movement],
                                       direction_to_face_nearest_node: Direction) -> None:
        """
        Directs the robot to the target cell

        :param list_of_movements: The list of movements to the neighbour of the unexplored cell
        :param direction_to_face_nearest_node: The facing direction required to reach the unexplored cell
        """
        for movement in list_of_movements:
            if not self.is_running:
                return

            self.move(movement)

        robot_facing_direction = self.robot.direction
        no_of_right_rotations = Direction.get_no_of_right_rotations_to_destination_cell(robot_facing_direction,
                                                                                        direction_to_face_nearest_node)
        if no_of_right_rotations == 2:
            self.move(Movement.RIGHT)

        elif no_of_right_rotations == 4:
            self.move(Movement.RIGHT)
            self.move(Movement.RIGHT)

        elif no_of_right_rotations == 6:
            self.move(Movement.LEFT)

    def go_home(self) -> None:
        robot_point = self.robot.point
        robot_facing_direction = self.robot.direction

        list_of_movements = self.find_fastest_path_to_node(robot_point,
                                                           constants.ROBOT_START_POINT,
                                                           robot_facing_direction)

        if list_of_movements is None or len(list_of_movements) <= 0:
            print_error_log('No path home! :(')
            return

        self.move_robot_to_destination_cell(list_of_movements, Direction.EAST)


if __name__ == '__main__':
    from robot import SimulatorBot

    test_map = Map()

    exp_area = test_map.explored_map
    obs_arena = test_map.obstacle_map

    p1, p2 = test_map.load_map_from_disk('../maps/sample_arena_0.txt')
    sample_arena = test_map.decode_map_descriptor_for_fastest_path_task(p1, p2)

    bot = SimulatorBot(constants.ROBOT_START_POINT,
                       sample_arena,
                       Direction.EAST,
                       lambda m: None)

    coverage_lim = 1
    time_lim = get_default_exploration_duration()

    exploration_algo = Exploration(bot,
                                   exp_area,
                                   obs_arena,
                                   coverage_limit=coverage_lim,
                                   time_limit=time_lim)
    exploration_algo.start_exploration()

    print('\nExploration:')
    for row in exploration_algo.explored_map:
        print(row)

    print('\nObstacles:')
    for row in exploration_algo.obstacle_map:
        print(row)
