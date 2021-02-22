from typing import Callable, List, Union, Tuple

from map import is_within_arena_range
from algorithms.exploration import Exploration, get_current_time_in_seconds
from utils import constants
from utils.enums import Cell, Direction, Movement
from utils.logger import print_general_log


class ImageRecognitionExploration(Exploration):
    def __init__(self,
                 robot,
                 explored_map: list,
                 obstacle_map: list,
                 on_update_map: Callable = None,
                 on_calibrate: Callable = None,
                 on_take_photo: Callable = None,
                 coverage_limit: float = 1,
                 time_limit: float = 6):
        super().__init__(robot, explored_map, obstacle_map, on_update_map, on_calibrate, coverage_limit, time_limit)

        self.obstacles_table = {}
        self.on_take_photo = on_take_photo if on_take_photo is not None else lambda obstacles: None

    def start_exploration(self) -> None:
        self.start_time = get_current_time_in_seconds()
        self.sense_and_repaint_canvas()
        self.right_hug()
        self.hug_middle_obstacles()
        print_general_log('Done hugging. Checking for unexplored cells now...')

        self.explore_unexplored_cells()
        print_general_log('Done exploring unexplored cells. Returning home now...')
        self.go_home()
        print_general_log('Reached home!')

    def mark_cell_as_explored(self,
                              current_sensor_point: List[int],
                              direction_offset: List[int],
                              sensor_range: List[int],
                              obstacle_distance_from_the_sensor: Union[None, int] = None) -> None:
        """
        **OVERRIDES the parent exploration's method**

        Marks the cell explored from the sensors of the robot on the explored arena reference \n
        Marks the obstacle on the obstacle arena reference as well. \n

        :param current_sensor_point: Current sensor coordinate relative to the robot's direction
        :param direction_offset: Offset coordinate of the sensor's direction'
        :param sensor_range: The range of the sensor
        :param obstacle_distance_from_the_sensor: The distance from the sensor on the robot to obstacle
        """
        for j in range(sensor_range[0], sensor_range[1]):
            cell_point_to_mark = (current_sensor_point[0] + j * direction_offset[0],
                                  current_sensor_point[1] + j * direction_offset[1])

            if not is_within_arena_range(cell_point_to_mark[0], cell_point_to_mark[1]):
                continue

            self.explored_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.EXPLORED.value

            if obstacle_distance_from_the_sensor is None or j != obstacle_distance_from_the_sensor:
                continue

            self.obstacle_map[cell_point_to_mark[0]][cell_point_to_mark[1]] = Cell.OBSTACLE.value

            if cell_point_to_mark not in self.obstacles_table:
                self.obstacles_table[cell_point_to_mark] = {0, 1, 2, 3}  # TODO: Confirm if it is movements or direction
                self.remove_obstacle_side(cell_point_to_mark)

    def remove_obstacle_side(self, cell_point_to_mark: Tuple[int, int]) -> None:
        raise NotImplementedError

    def hug_middle_obstacles(self) -> None:
        # Find obstacles to hug
        # Use fastest path solver to go to the obstacle
        # if explored, then right hug obstacles
        raise NotImplementedError

    def find_obstacles_to_hug(self) -> dict:
        raise NotImplementedError

    def right_hug_obstacles(self, initial_robot_position: List[int]) -> None:
        raise NotImplementedError

    def move(self, movement: 'Movement') -> None:
        """
        **OVERRIDES the parent exploration's method**

        Moves the robot, updates it's position in the simulator and marks the area of the robot as explored \n
        *(Additional feature)* Sends command to RPI to take a photo of the surrounding area of the robot.

        :param movement: The movement direction to be made by the robot
        """
        super().move(movement)
        self.snap_to_obstacle_side()

    def snap_to_obstacle_side(self):
        raise NotImplementedError

    def check_obstacle_side(self, robot_point, robot_direction: 'Direction') -> list:
        raise NotImplementedError

    def check_if_contains_corners(self, list_of_obstacles: list, robot_direction: 'Direction') -> bool:
        raise NotImplementedError


if __name__ == '__main__':
    from map import Map
    from robot import SimulatorBot

    test_map = Map()

    exp_arena = test_map.explored_map
    obs_arena = test_map.obstacle_map
    sample_arena = test_map.sample_arena

    bot = SimulatorBot(constants.ROBOT_START_POINT,
                       sample_arena,
                       Direction.EAST,
                       lambda m: None)

    img_rec_exploration = ImageRecognitionExploration(bot,
                                                      exp_arena,
                                                      obs_arena)

    img_rec_exploration.start_exploration()
