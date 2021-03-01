from enum import IntEnum
from typing import List


class Cell(IntEnum):
    """
    The possible states of a node/cell in the arena
    """
    FREE_AREA = 0
    OBSTACLE = 1
    VIRTUAL_WALL = 2

    UNEXPLORED = 0
    EXPLORED = 1


class Direction(IntEnum):
    """
    The possible directions that an object can make in the arena
    """
    NORTH = 0
    EAST = 2
    SOUTH = 4
    WEST = 6

    # If we want to work with diagonals in the future
    NORTH_EAST = 1
    SOUTH_EAST = 3
    SOUTH_WEST = 5
    NORTH_WEST = 7

    @staticmethod
    def get_direction_offset(direction: 'Direction') -> List[int]:
        """
        Gets the offset to determine the coordinate position of the sensor
        Assumes the robot's default direction is NORTH

        :param direction: X and Y position coordinate
        :return: List offset values required to determine the sensor's coordinate position
        """
        if direction == Direction.NORTH:
            return [-1, 0]

        if direction == Direction.EAST:
            return [0, 1]

        if direction == Direction.SOUTH:
            return [1, 0]

        if direction == Direction.WEST:
            return [0, -1]

        raise ValueError('Invalid direction given!')

    @staticmethod
    def get_clockwise_direction(current_direction: 'Direction', includes_diagonal: bool = False) -> 'Direction':
        """
        Determines the next bearing from the current direction that the 'robot' is facing.
        For example, if the current bearing is 6 (West) and the algorithm does not account
        for diagonal directions, the next bearing will be 6 + 2 = 8.

        By taking the mod of the next bearing, 8, we will get North (0).

        :param current_direction: Current direction of the 'robot'
        :param includes_diagonal: To consider diagonal directions
        :return: The next bearing direction
        """
        if includes_diagonal:
            return Direction((current_direction + 1) % 8)

        return Direction((current_direction + 2) % 8)

    @staticmethod
    def get_anti_clockwise_direction(current_direction: 'Direction', includes_diagonal: bool = False) -> 'Direction':
        """
        Determines the previous bearing from the current direction that the 'robot' is facing.
        For example, if the current bearing is 6 (West) and the algorithm does not account
        for diagonal directions, the next bearing will be 6 + 6 = 12.

        By taking the mod of the next bearing, 8, we will get South (4).

        :param current_direction: Current direction of the 'robot'
        :param includes_diagonal: To consider diagonal directions
        :return: The previous bearing direction
        """
        if includes_diagonal:
            return Direction((current_direction + 7) % 8)

        return Direction((current_direction + 6) % 8)

    @staticmethod
    def get_opposite_direction(current_direction: 'Direction', includes_diagonal: bool = False) -> 'Direction':
        clockwise_direction = Direction.get_clockwise_direction(current_direction, includes_diagonal)

        return Direction.get_clockwise_direction(clockwise_direction, includes_diagonal)

    @staticmethod
    def get_no_of_right_rotations_to_destination_cell(current_direction, destination_direction):
        return (destination_direction - current_direction) % 8

    @staticmethod
    def to_string(direction: 'Direction') -> str:
        """
        Converts the enum representation of the current direction to string format

        :param direction: The enum representation of the current direction
        :return: The string representation of the direction given
        """
        if direction == Direction.NORTH:
            return 'N'

        if direction == Direction.EAST:
            return 'E'

        if direction == Direction.SOUTH:
            return 'S'

        if direction == Direction.WEST:
            return 'W'

        raise ValueError('Invalid direction given!')

    @staticmethod
    def from_string_to_direction(direction: str) -> 'Direction':
        """
        Converts the string representation of the direction to the enum format

        :param direction: The string representation of the current direction
        :return: The enum of the direction given
        """
        if direction == 'W':
            return Direction.NORTH

        if direction == 'D':
            return Direction.EAST

        if direction == 'S':
            return Direction.SOUTH

        if direction == 'A':
            return Direction.WEST

        raise ValueError('Invalid direction given!')


class Movement(IntEnum):
    """
    The possible movements that an object can make in the arena
    """

    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2
    LEFT = 3

    @staticmethod
    def to_string(movement: 'Movement') -> str:
        """
        Converts the enum representation of movement to string format

        :param movement: The enum representation of the current movement
        :return: The string representation of the current movement
        """
        if movement == Movement.FORWARD:
            return 'F'

        if movement == Movement.RIGHT:
            return 'R'

        if movement == Movement.BACKWARD:
            return 'B'

        if movement == Movement.LEFT:
            return 'L'

        raise ValueError('Invalid movement given!')


if __name__ == '__main__':
    print(Direction.get_direction_offset(Direction.NORTH))
    print(type(Direction.get_direction_offset(Direction.NORTH)))
