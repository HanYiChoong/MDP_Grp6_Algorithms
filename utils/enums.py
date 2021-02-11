from enum import IntEnum


class Cell(IntEnum):
    FREE_AREA = 0
    UNEXPLORED = 0
    EXPLORED = 1
    OBSTACLE = 1
    VIRTUAL_WALL = 2


class Direction(IntEnum):
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
    def get_direction_offset(direction: 'Direction') -> list:
        """
        Gets the offset to determine the coordinate position of the sensor
        Assumes the robot's default direction is NORTH

        :param direction: X and Y position coordinate
        :return: The offset values required to determine the sensor coordinate position
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
    def to_string(direction: 'Direction') -> str:
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
        if direction == 'N':
            return Direction.NORTH

        if direction == 'E':
            return Direction.EAST

        if direction == 'S':
            return Direction.SOUTH

        if direction == 'W':
            return Direction.WEST

        raise ValueError('Invalid direction given!')


class Movement(IntEnum):
    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2
    LEFT = 3

    @staticmethod
    def to_string(movement: 'Movement') -> str:
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
