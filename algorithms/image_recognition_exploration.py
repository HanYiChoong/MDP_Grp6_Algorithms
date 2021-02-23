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

        self.obstacle_direction_to_take_photo = {}
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

            if cell_point_to_mark not in self.obstacle_direction_to_take_photo:
                self.obstacle_direction_to_take_photo[cell_point_to_mark] = {Direction.NORTH,
                                                                             Direction.EAST,
                                                                             Direction.SOUTH,
                                                                             Direction.WEST}
                self.remove_obstacle_side(cell_point_to_mark)

    def remove_obstacle_side(self, obstacle_cell_point: Tuple[int, int]) -> None:
        """
        Determine if obstacles are grouped together.
        Excludes these directions from the photo taking phase of the exploration

        :param obstacle_cell_point: The coordinate of the obstacle in the arena
        """
        for i in range(1, 4):
            right_point_of_obstacle: Tuple[int, int] = (obstacle_cell_point[0], obstacle_cell_point[1] + i)
            self.check_if_right_of_obstacle_is_obstacle(obstacle_cell_point, right_point_of_obstacle)

            left_point_of_obstacle: Tuple[int, int] = (obstacle_cell_point[0], obstacle_cell_point[1] - i)
            self.check_if_left_of_obstacle_is_obstacle(obstacle_cell_point, left_point_of_obstacle)

            top_point_of_obstacle: Tuple[int, int] = (obstacle_cell_point[0] - 1, obstacle_cell_point[1])
            self.check_if_top_of_obstacle_is_obstacle(obstacle_cell_point, top_point_of_obstacle)

            bottom_point_of_obstacle: Tuple[int, int] = (obstacle_cell_point[0] + 1, obstacle_cell_point[1])
            self.check_if_bottom_of_obstacle_is_obstacle(obstacle_cell_point, bottom_point_of_obstacle)

    def check_if_right_of_obstacle_is_obstacle(self,
                                               obstacle_cell_point: Tuple[int, int],
                                               right_point_of_obstacle: Tuple[int, int]) -> None:
        # if right_point_of_obstacle in self.obstacle_direction_to_take_photo:
        #     if Direction.EAST in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
        #         self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.EAST)
        #
        #     if Direction.WEST in self.obstacle_direction_to_take_photo[right_point_of_obstacle]:
        #         self.obstacle_direction_to_take_photo[right_point_of_obstacle].remove(Direction.EAST)
        self.check_if_neighbour_of_obstacle_is_obstacle(obstacle_cell_point,
                                                        right_point_of_obstacle,
                                                        Direction.EAST)
        if right_point_of_obstacle[1] > 14 \
                and Direction.EAST in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
            # If the obstacle is at the edge of the arena
            self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.EAST)

    def check_if_left_of_obstacle_is_obstacle(self,
                                              obstacle_cell_point: Tuple[int, int],
                                              left_point_of_obstacle: Tuple[int, int]) -> None:
        # if left_point_of_obstacle in self.obstacle_direction_to_take_photo:
        #     if Direction.WEST in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
        #         self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.WEST)
        #     if Direction.EAST in self.obstacle_direction_to_take_photo[left_point_of_obstacle]:
        #         self.obstacle_direction_to_take_photo[left_point_of_obstacle].remove(Direction.EAST)
        self.check_if_neighbour_of_obstacle_is_obstacle(obstacle_cell_point,
                                                        left_point_of_obstacle,
                                                        Direction.WEST)
        if left_point_of_obstacle[1] < 0 and \
                Direction.WEST in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
            self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.WEST)

    def check_if_top_of_obstacle_is_obstacle(self,
                                             obstacle_cell_point: Tuple[int, int],
                                             top_point_of_obstacle: Tuple[int, int]) -> None:
        """

        :param obstacle_cell_point:
        :param top_point_of_obstacle:
        :return:
        """
        self.check_if_neighbour_of_obstacle_is_obstacle(obstacle_cell_point,
                                                        top_point_of_obstacle,
                                                        Direction.NORTH)

        if top_point_of_obstacle[0] > 19 and \
                Direction.NORTH in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
            self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.NORTH)

    def check_if_bottom_of_obstacle_is_obstacle(self,
                                                obstacle_cell_point: Tuple[int, int],
                                                bottom_point_of_obstacle: Tuple[int, int]) -> None:
        """

        :param obstacle_cell_point:
        :param bottom_point_of_obstacle:
        :return:
        """
        self.check_if_neighbour_of_obstacle_is_obstacle(obstacle_cell_point,
                                                        bottom_point_of_obstacle,
                                                        Direction.SOUTH)

        if bottom_point_of_obstacle[0] < 0 and \
                Direction.SOUTH in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
            self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(Direction.SOUTH)

    def check_if_neighbour_of_obstacle_is_obstacle(self,
                                                   obstacle_cell_point: Tuple[int, int],
                                                   neighbour_cell_point: Tuple[int, int],
                                                   direction: 'Direction'):
        # Removes the direction of east and west from grouped horizontal obstacles
        # E.g. |O1|O2| -> Remove the east of O1 and the west of O2 as they are grouped together
        opposite_direction = Direction.get_opposite_direction(direction)

        if neighbour_cell_point in self.obstacle_direction_to_take_photo:
            if direction in self.obstacle_direction_to_take_photo[obstacle_cell_point]:
                self.obstacle_direction_to_take_photo[obstacle_cell_point].remove(direction)

            if opposite_direction in self.obstacle_direction_to_take_photo[neighbour_cell_point]:
                self.obstacle_direction_to_take_photo[neighbour_cell_point].remove(opposite_direction)

    def get_obstacles_in_direction(self, direction: 'Direction', robot_point: List[int]) -> list:
        obstacles = self.find_neighbouring_obstacle_cells_two_blocks_away(direction, robot_point)

        if direction == Direction.NORTH:
            # for i in range(-1, 2):
            #     # Assume camera range is 2 cm away from the edge of the robot
            #     north_north_point_from_robot = (robot_point[0] - 3, robot_point[1] + i)
            #     # if obstacles are present 2 cm away from the north of the robot and the can reach the
            #     # obstacle from the south direction, add to obstacle list
            #     if north_north_point_from_robot in self.obstacle_direction_to_take_photo and \
            #             Direction.SOUTH in self.obstacle_direction_to_take_photo[north_north_point_from_robot]:
            #         obstacles.append(north_north_point_from_robot)

            north_point_from_robot = (robot_point[0] + 2, robot_point[1])
            if north_point_from_robot in self.obstacle_direction_to_take_photo and \
                    Direction.SOUTH in self.obstacle_direction_to_take_photo[north_point_from_robot]:
                obstacles.append(north_point_from_robot)

            return obstacles

        if direction == Direction.EAST:
            # for i in range(-1, 2):
            #     east_east_point_from_robot = (robot_point[0] + i, robot_point[1] + 3)
            #     # if obstacles are present 2 cm away from the east of the robot and the can reach the
            #     # obstacle from the west direction, add to obstacle list
            #     if east_east_point_from_robot in self.obstacle_direction_to_take_photo and \
            #             Direction.WEST in self.obstacle_direction_to_take_photo[east_east_point_from_robot]:
            #         obstacles.append(east_east_point_from_robot)

            east_point_from_robot = (robot_point[0], robot_point[1] + 2)
            if east_point_from_robot in self.obstacle_direction_to_take_photo and \
                    Direction.WEST in self.obstacle_direction_to_take_photo[east_point_from_robot]:
                obstacles.append(east_point_from_robot)

            return obstacles

        if direction == Direction.SOUTH:
            # for i in range(-1, 2):
            #     south_south_point_from_robot = (robot_point[0] + 3, robot_point[1] + i)
            #
            #     if south_south_point_from_robot in self.obstacle_direction_to_take_photo and \
            #             Direction.NORTH in self.obstacle_direction_to_take_photo[south_south_point_from_robot]:
            #         obstacles.append(south_south_point_from_robot)

            south_point_from_robot = (robot_point[0] + 2, robot_point[1])
            if south_point_from_robot in self.obstacle_direction_to_take_photo and \
                    Direction.NORTH in self.obstacle_direction_to_take_photo[south_point_from_robot]:
                obstacles.append(south_point_from_robot)

            return obstacles

        if direction == Direction.WEST:
            # for i in range(-1, 2):
            #     west_west_point_from_robot = (robot_point[0] + i, robot_point[1] - 3)
            #
            #     if west_west_point_from_robot in self.obstacle_direction_to_take_photo and \
            #             Direction.EAST in self.obstacle_direction_to_take_photo[west_west_point_from_robot]:
            #         obstacles.append(west_west_point_from_robot)

            west_point_from_robot = (robot_point[0], robot_point[1] - 2)
            if west_point_from_robot in self.obstacle_direction_to_take_photo and \
                    Direction.EAST in self.obstacle_direction_to_take_photo[west_point_from_robot]:
                obstacles.append(west_point_from_robot)

            return obstacles

    def find_neighbouring_obstacle_cells_two_blocks_away(self,
                                                         direction: 'Direction',
                                                         robot_point: List[int]) -> List[Tuple[int, int]]:
        """
        E.g if direction is north

        O | O | O  <- find obstacles here
          |   |
        x | x | x
        x | x | x  <- from center of robot
        x | x | x

        :param direction:
        :param robot_point:
        :return:
        """
        obstacles = []

        for i in range(-1, 2):
            opposite_direction = Direction.get_opposite_direction(direction)

            if direction == Direction.NORTH:
                neighbour_neighbour_point_from_robot = (robot_point[0] - 3, robot_point[1] + i)

            elif direction == Direction.EAST:
                neighbour_neighbour_point_from_robot = (robot_point[0] + i, robot_point[1] + 3)

            elif direction == Direction.SOUTH:
                neighbour_neighbour_point_from_robot = (robot_point[0] + 3, robot_point[1] + i)

            else:  # West direction
                neighbour_neighbour_point_from_robot = (robot_point[0] + i, robot_point[1] - 3)

            if neighbour_neighbour_point_from_robot in self.obstacle_direction_to_take_photo and \
                    opposite_direction in self.obstacle_direction_to_take_photo[neighbour_neighbour_point_from_robot]:
                obstacles.append(neighbour_neighbour_point_from_robot)

        return obstacles

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
