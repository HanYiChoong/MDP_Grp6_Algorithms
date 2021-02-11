from typing import Callable, Union

from utils.constants import ARENA_HEIGHT, ARENA_WIDTH
from utils.enums import Cell, Direction, Movement


class Robot:
    def __init__(self, point: list, direction: 'Direction', on_move: Callable = None):
        """

        :param point: Position of the robot in the arena
        :param direction: Direction of the robot in the arena
        :param on_move:
        """
        self.point = point
        self.direction = direction
        self.on_move = on_move if on_move is not None else lambda movement: None
        # ASSUMPTION of the current sensor and their positions
        # Base on the check list, I presume we have 7 sensors, 6 short range (SR) and 1 long range (LR)
        #
        # SR1 | LR1 | SR2
        # SR3 |     | SR4
        # SR5 |     | SR6
        #
        self.sensor_offset_points = [
            Sensor(False, [1, 0], Direction.NORTH),
            Sensor(True, [1, -1], Direction.WEST),
            Sensor(True, [1, 1], Direction.EAST),
            Sensor(True, [0, -1], Direction.WEST),
            Sensor(True, [0, 1], Direction.EAST),
            Sensor(True, [-1, -1], Direction.WEST),
            Sensor(True, [-1, 1], Direction.EAST)
        ]

    @property
    def speed(self):
        raise NotImplementedError

    def move(self, movement: Union['Movement', 'Direction']) -> None:
        # TODO: Modify direction for our use
        if not isinstance(movement, Movement):
            if self.direction == Direction.NORTH:
                self.pos = [self.pos[0], self.pos[1] + movement]
            elif self.direction == Direction.EAST:
                self.pos = (self.pos[0] + movement, self.pos[1])
            elif self.direction == Direction.SOUTH:
                self.pos = (self.pos[0], self.pos[1] - movement)
            elif self.direction == Direction.WEST:
                self.pos = (self.pos[0] - movement, self.pos[1])

        elif movement == Movement.FORWARD:
            if self.direction == Direction.NORTH:
                self.pos = (self.pos[0], self.pos[1] + 1)
            elif self.direction == Direction.EAST:
                self.pos = (self.pos[0] + 1, self.pos[1])
            elif self.direction == Direction.SOUTH:
                self.pos = (self.pos[0], self.pos[1] - 1)
            elif self.direction == Direction.WEST:
                self.pos = (self.pos[0] - 1, self.pos[1])

        elif movement == Movement.BACKWARD:
            if self.direction == Direction.NORTH:
                self.pos = (self.pos[0], self.pos[1] - 1)
            elif self.direction == Direction.EAST:
                self.pos = (self.pos[0] - 1, self.pos[1])
            elif self.direction == Direction.SOUTH:
                self.pos = (self.pos[0], self.pos[1] + 1)
            elif self.direction == Direction.WEST:
                self.pos = (self.pos[0] + 1, self.pos[1])

        elif movement == Movement.RIGHT:
            self.direction = Direction((self.direction + 1) % 4)

        elif movement == Movement.LEFT:
            self.direction = Direction((self.direction - 1) % 4)

        return self.on_move(movement)


class SimulatorBot(Robot):
    def __init__(self,
                 point: list,
                 explored_map: list,
                 obstacle_map: list,
                 direction: 'Direction',
                 on_move: Callable = None,
                 time_interval: float = 0.2):
        super(SimulatorBot, self).__init__(point, direction, on_move)

        self.time_interval = time_interval
        self.explored_map = explored_map
        self.obstacle_map = obstacle_map

    @property
    def speed(self):
        return 1 / self.time_interval

    @speed.setter
    def speed(self, speed):
        self.time_interval = 1 / speed

    def move(self, movement: Union['Movement', 'Direction']) -> None:
        # Maybe add delay to simulate move?
        super().move(movement)

    def sense(self) -> list:
        """
        Determines if the target direction are free to explore

        :return: List of neighbouring points that can be explored or contains obstacles
        """
        may_contain_obstacles = []

        # Simulates checking for obstacles ahead and side of the robot using the sensors
        for sensor in self.sensor_offset_points:
            direction_vector = Direction.get_direction_offset(sensor.get_current_direction(self.direction))
            sensor_pos = sensor.get_current_point(self)
            sensor_range = sensor.get_sensor_range()

            for i in range(1, sensor_range[1]):
                pos_to_check = (sensor_pos[0] + i * direction_vector[0], sensor_pos[1] + i * direction_vector[1])

                if not (0 <= pos_to_check[0] < ARENA_WIDTH) or \
                        not (0 <= pos_to_check[1] < ARENA_HEIGHT) or \
                        self.obstacle_map[pos_to_check[0]][pos_to_check[1]] == Cell.OBSTACLE:
                    if i < sensor_range[0]:
                        may_contain_obstacles.append(-1)
                    else:
                        may_contain_obstacles.append(i)
                    break

            else:  # appends None nothing occurs during the iteration of the for loop
                may_contain_obstacles.append(None)

        return may_contain_obstacles


class Sensor:
    # Inclusive at lower bound, exclusive at upper bound
    SR_RANGE = [1, 3]
    LR_RANGE = [1, 6]

    def __init__(self, is_short_range: bool, point: list, direction: 'Direction'):
        self.is_short_range = is_short_range
        self.point = point
        self.direction = direction

    def get_sensor_range(self) -> list:
        if self.is_short_range:
            return Sensor.SR_RANGE

        return Sensor.LR_RANGE

    def get_current_direction(self, robot_direction: 'Direction') -> 'Direction':
        return Direction((robot_direction + self.direction - Direction.NORTH) % 8)

    def get_current_point(self, robot: 'Robot') -> list:
        if robot.direction == Direction.NORTH:
            return [robot.point[0] - self.point[0], robot.point[1] + self.point[1]]
        elif robot.direction == Direction.EAST:
            return [robot.point[0] + self.point[1], robot.point[1] + self.point[0]]
        elif robot.direction == Direction.SOUTH:
            return [robot.point[0] + self.point[0], robot.point[1] - self.point[1]]
        else:  # Direction.WEST
            return [robot.point[0] - self.point[1], robot.point[1] - self.point[0]]

# if __name__ == '__main__':
#     from map import Map
#
#     map_object = Map()
#     explored_map = map_object.explored_map
#     obstacle_map = map_object.obstacle_map
#
#     sim_bot = SimulatorBot([18, 1], explored_map, obstacle_map, Direction.SOUTH)
#
#     may_contain_obstacles = []
#
#     for sensor in sim_bot.sensor_offset_points:
#         direction_vector = Direction.get_direction_offset(sensor.get_current_direction(sim_bot.direction))
#         position = sensor.get_current_point(sim_bot)
#         sensor_range = sensor.get_sensor_range()
#
#         for i in range(1, sensor_range[1]):
#             position_to_check = [position[0] + i * direction_vector[0], position[1] + i * direction_vector[1]]
#             if not (0 <= position_to_check[0] < ARENA_HEIGHT) or \
#                     not (0 <= position_to_check[1] < ARENA_WIDTH) or \
#                     sim_bot.obstacle_map[position_to_check[0]][position_to_check[1]] == Cell.OBSTACLE:
#                 if i < sensor_range[0]:
#                     may_contain_obstacles.append(-1)
#                 else:
#                     may_contain_obstacles.append(i)
#                 break
#
#         else:  # appends None nothing occurs during the iteration of the for loop
#             may_contain_obstacles.append(None)
#
#         print(may_contain_obstacles)
