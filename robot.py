from time import sleep
from typing import Callable, List, Union, Tuple, Optional

from utils.constants import ARENA_HEIGHT, ARENA_WIDTH, ROBOT_START_POINT
from utils.enums import Cell, Direction, Movement


class Robot:
    """
    The base class for the MDP Robot. Contains the main functionality of the robot.
    """

    def __init__(self, point: List[int], direction: 'Direction', on_move: Callable = None):
        """
        Initialises the robot class to perform functions related to the robot in MDP.

        This class relies on Sensor class to detect obstacles on the map.

        The sensor offsets in this class must match the position of the sensor placements in the actual robot.
        Changes to the sensor offset values MUST be made to this class ONLY.

        :param point: Position of the robot in the arena
        :param direction: Direction of the robot in the arena
        :param on_move: Callback function to send the movement to RPI after the moving the robot (No use for simulation)
        """
        self.point = point
        self.direction = direction
        self.on_move = on_move if on_move is not None else lambda: None
        # ASSUMPTION of the current sensor and their positions
        # Base on the check list, I presume we have 7 sensors, 6 short range (SR) and 1 long range (LR)
        #
        # SR1 | SR2 | SR3/4
        # LR1 |     |
        #     |     | SR5
        #
        # Change the sensor offset and directions will do.
        # Modifications to the Sensor class are not required as it could mess up the entire exploration.
        self.sensor_offset_points: List['Sensor'] = [
            Sensor(True, [1, -1], Direction.NORTH),
            Sensor(True, [1, 0], Direction.NORTH),
            Sensor(True, [1, 1], Direction.NORTH),
            Sensor(False, [1, -1], Direction.WEST),
            Sensor(True, [1, 1], Direction.EAST),
            Sensor(True, [-1, 1], Direction.EAST)
        ]

    @property
    def speed(self):
        raise NotImplementedError

    def move(self, movement: Union['Movement', 'Direction'], invoke_callback: bool = True) -> Optional[List[int]]:
        """
        Moves the robot in the specified direction.

        :param movement: The direction or movement that the robot will make
        :param invoke_callback: A boolean flag to run the callback function on_move. (Mainly used in the actual run)
        """
        if isinstance(movement, Direction):
            if self.direction == Direction.NORTH:
                self.point = [self.point[0] - movement, self.point[1]]
            elif self.direction == Direction.EAST:
                self.point = [self.point[0], self.point[1] + movement]
            elif self.direction == Direction.SOUTH:
                self.point = [self.point[0] + movement, self.point[1]]
            elif self.direction == Direction.WEST:
                self.point = [self.point[0], self.point[1] - movement]

        elif movement == Movement.FORWARD:
            if self.direction == Direction.NORTH:
                self.point = [self.point[0] - 1, self.point[1]]
            elif self.direction == Direction.EAST:
                self.point = [self.point[0], self.point[1] + 1]
            elif self.direction == Direction.SOUTH:
                self.point = [self.point[0] + 1, self.point[1]]
            elif self.direction == Direction.WEST:
                self.point = [self.point[0], self.point[1] - 1]

        elif movement == Movement.BACKWARD:
            if self.direction == Direction.NORTH:
                self.point = [self.point[0] + 1, self.point[1]]
            elif self.direction == Direction.EAST:
                self.point = [self.point[0], self.point[1] - 1]
            elif self.direction == Direction.SOUTH:
                self.point = [self.point[0] - 1, self.point[1]]
            elif self.direction == Direction.WEST:
                self.point = [self.point[0], self.point[1] + 1]

        elif movement == Movement.RIGHT:
            self.direction = Direction(Direction.get_clockwise_direction(self.direction))

        elif movement == Movement.LEFT:
            self.direction = Direction(Direction.get_anti_clockwise_direction(self.direction))

        if not invoke_callback:
            return

        return self.on_move(movement)


class RealRobot(Robot):
    """
    An extension of the base robot class.
    The robot that represents the actual robot in MDP.
    """

    def __init__(self, point: List[int], direction: 'Direction', on_move: Callable, get_sensor_values: Callable):
        """
        Initialises the robot that represents the actual robot.

        :param point: The initial coordinates of the robot in the simulator. Format: [x, y]
        :param direction: The initial direction of the robot
        :param on_move: Callback function to send the movement to RPI after the moving the robot
        :param get_sensor_values: Callback function to get sensor values from the RPI module
        """
        super(RealRobot, self).__init__(point, direction, on_move)

        self.get_sensor_values = get_sensor_values

    @property
    def speed(self) -> int:
        """
        The speed of the robot.

        :return: The speed of the robot lmao.
        """
        return 2

    def sense(self) -> List[float]:
        """
        Gets the sensor values from the RPI module.

        :return: The list of sensor values from the RPI module
        """
        return self.get_sensor_values()


class SimulatorBot(Robot):
    """
    An extension of the base robot class.
    The robot that only lives in the simulator. It's sole purpose is to explore the arena in the simulator.
    """

    def __init__(self,
                 point: list,
                 arena_info: list,
                 direction: 'Direction',
                 on_move: Callable = None,
                 time_interval: float = 0.2,
                 update_interval: float = 0.2):
        """
        Initialises the robot in the simulator

        :param point: The initial coordinates of the robot in the simulator. Format: [x, y]
        :param arena_info: The arena to run the robot
        :param direction: The initial direction of the robot
        :param on_move: Callback function to send the movement to RPI after the moving the robot (No use for simulation)
        :param time_interval: Used to determine the speed of the robot in the simulator
        :param update_interval: Used to control the interval to redraw the robot in the simulator
        """
        super(SimulatorBot, self).__init__(point, direction, on_move)

        self.time_interval = time_interval
        self.reference_map = arena_info
        self.update_interval = update_interval

    @property
    def speed(self) -> float:
        """
        The getter method for the speed of the robot.
        The speed is inversely proportional to the time interval given in the creation of the robot object

        :return: The current speed of the robot
        """
        return 1 / self.time_interval

    @speed.setter
    def speed(self, speed: float) -> None:
        """
        The setter method for the speed of the robot.
        The speed is inversely proportional to the time interval given in the creation of the robot object

        :param speed: The new speed of the robot
        """
        self.time_interval = 1 / speed

    @property
    def sleep_interval(self) -> float:
        """
        The getter method of the interval to update the robot's movement in the simulator.

        :return: The current speed of the robot
        """
        return self.update_interval * 0.5

    @sleep_interval.setter
    def sleep_interval(self, speed: float) -> None:
        """
        The setter method of the interval to update the robot's movement in the simulator.
        The higher the speed, the faster the update interval
        :param speed: The new speed of the robot
        """
        self.update_interval = 0.5 / speed

    # Temporary not in use. May use it when integrating with the GUI
    def move(self, movement: Union['Movement', 'Direction'], invoke_callback: bool = True) -> None:
        """
        Moves the robot in the specified direction.

        :param movement: The direction or movement that the robot will make
        :param invoke_callback: A boolean flag to run the callback function on_move. (Mainly used in the actual run)
        """

        sleep(self.update_interval)
        super().move(movement, invoke_callback)

    def sense(self) -> List[Union[None, int]]:
        """
        Determines if obstacles are present around the perimeter of the robot using the robot's sensors.

        :return: List of neighbouring points from the robot that can be explored or contains obstacles
        """
        may_contain_obstacles = []

        for sensor in self.sensor_offset_points:
            direction_vector = Direction.get_direction_offset(sensor.get_current_direction(self.direction))
            sensor_point = sensor.get_current_point(self.point, self.direction)
            sensor_range = sensor.get_sensor_range()

            for i in range(1, sensor_range[1]):
                point_to_check = [sensor_point[0] + i * direction_vector[0], sensor_point[1] + i * direction_vector[1]]

                if not (0 <= point_to_check[0] < ARENA_HEIGHT) or \
                        not (0 <= point_to_check[1] < ARENA_WIDTH) or \
                        self.reference_map[point_to_check[0]][point_to_check[1]] == Cell.OBSTACLE:
                    if i < sensor_range[0]:
                        # If the sensor detection is not within the sensor range
                        may_contain_obstacles.append(-1)
                    else:
                        # Adds the distance from the sensor to the robot to the list. The distance starts from 1
                        may_contain_obstacles.append(i)
                    break

            else:  # Appends None nothing occurs during the iteration of the for loop
                may_contain_obstacles.append(None)

        return may_contain_obstacles


class Sensor:
    """
    The sensors attached to the robot. Has a dependency with Robot class.
    DO NOT modify this class unless you know what you are doing.
    """

    # Shared variables across initialised sensor objects
    # Range is inclusive at lower bound, exclusive at upper bound
    SR_RANGE = [1, 2]
    LR_RANGE = [1, 7]

    def __init__(self, is_short_range: bool, point: list, direction: 'Direction'):
        """
        :param is_short_range: True if sensor is a short range type. Else False if it is a long range type
        :param point: The initial offset coordinates of the sensor.
                      The coordinates are relative to the robot's position Format: [x, y]
        :param direction: The direction of the sensor placed on the robot
        """
        self.is_short_range = is_short_range
        self.point = point
        self.direction = direction

    def get_sensor_range(self) -> List[int]:
        """
        Gets the range that the sensor can detect

        :return: The range of the sensor. Range is inclusive at lower bound, exclusive at upper bound
        """
        if self.is_short_range:
            return Sensor.SR_RANGE

        return Sensor.LR_RANGE

    def get_current_direction(self, robot_direction: 'Direction') -> 'Direction':
        """
        Determines the current direction of the sensor relative to the robot's direction.

        :param robot_direction: The current direction of the robot
        :return:
        """
        return Direction((robot_direction + self.direction - Direction.NORTH) % 8)

    def get_current_point(self, point: List[int], direction: 'Direction') -> Tuple[int, int]:
        """
        Returns the current offset coordinates of the sensor relative to the robot's direction.

        :param point: The point of the robot or any object that uses the sensors
        :param direction: Direction of the robot or any object that uses the sensors
        :return: List of offset coordinates of the sensor relative to the robot's direction: Format [x,y]
        """
        if direction == Direction.NORTH:
            return point[0] - self.point[0], point[1] + self.point[1]
        elif direction == Direction.EAST:
            return point[0] + self.point[1], point[1] + self.point[0]
        elif direction == Direction.SOUTH:
            return point[0] + self.point[0], point[1] - self.point[1]
        else:  # Direction.WEST
            return point[0] - self.point[1], point[1] - self.point[0]


if __name__ == '__main__':
    from map import Map

    map_object = Map()
    sample_map = map_object.sample_arena

    sim_bot = SimulatorBot(ROBOT_START_POINT, sample_map, Direction.EAST, lambda m: None)
    sensor_sensed_result = sim_bot.sense()
    print(sensor_sensed_result)
