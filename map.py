from copy import deepcopy
from math import ceil
from typing import List, Tuple

from utils import constants
from utils.enums import Cell

SAMPLE_ARENA = [
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

_EXPLORED_MAP = [
    [0 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
]

_EXPLORED_FULL_MAP = [
    [1 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
]

_OBSTACLE_MAP = [
    [0 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
]


# _OBSTACLE_MAP = [
#     [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
# ]


def is_within_arena_range(row: int, column: int) -> bool:
    """
    Checks if the coordinate of the cell in the arena is within the range (20 x 15)

    :param row: row coordinate of the current cell in the arena
    :param column: column coordinate of the current cell in the arena
    :return: True if the coordinates are with in the range of the arena, else False
    """
    return (0 <= row < constants.ARENA_HEIGHT) and (0 <= column < constants.ARENA_WIDTH)


class Map:
    def __init__(self):
        self.explored_map = deepcopy(_EXPLORED_MAP)  # 2D list
        self.obstacle_map = deepcopy(_OBSTACLE_MAP)  # 2D list
        self.sample_arena = deepcopy(SAMPLE_ARENA)

    def load_map_from_disk(self, filename: str) -> list:
        """
        Loads the map descriptor file from disk. Used for fastest path

        :param filename: File path directory of the arena
        :return: The P2 string descriptor of the arena
        """
        with open(filename, 'r') as file_reader_handler:
            string_descriptors = file_reader_handler.readline()

        return string_descriptors.split('|')

    def reset_exploration_maps(self) -> None:
        """
        Resets the exploration and obstacle map

        """
        self.explored_map = deepcopy(_EXPLORED_MAP)
        self.obstacle_map = deepcopy(_OBSTACLE_MAP)

    @staticmethod
    def set_virtual_walls_on_map(virtual_arena: List[int], explored_arena: List[int] = None) -> None:
        """
        Pads virtual wall around obstacles and the surrounding of the area.
        Used for fastest path
        """
        Map._set_virtual_wall_around_arena(virtual_arena)
        Map._set_virtual_walls_around_obstacles(virtual_arena)

        if explored_arena is None:
            return

        Map._set_unexplored_cell_as_virtual_wall(virtual_arena, explored_arena)

    @staticmethod
    def _set_virtual_wall_around_arena(arena: List[int]) -> None:
        """
        Pads the virtual wall around the arena

        :param arena: The arena to pad virtual wall
        """
        for x in range(constants.ARENA_WIDTH):
            if arena[0][x] != 1:
                arena[0][x] = Cell.VIRTUAL_WALL.value

            if arena[constants.ARENA_HEIGHT - 1][x] != 1:
                arena[constants.ARENA_HEIGHT - 1][x] = Cell.VIRTUAL_WALL.value

        for y in range(constants.ARENA_HEIGHT):
            if arena[y][0] != 1:
                arena[y][0] = Cell.VIRTUAL_WALL.value

            if arena[y][constants.ARENA_WIDTH - 1] != 1:
                arena[y][constants.ARENA_WIDTH - 1] = Cell.VIRTUAL_WALL.value

    @staticmethod
    def _set_virtual_walls_around_obstacles(arena: List[int]) -> None:
        """
        Pads virtual walls around obstacles

        :param arena: The arena to pad virtual wall
        """
        for row in range(constants.ARENA_HEIGHT):
            for column in range(constants.ARENA_WIDTH):
                if arena[row][column] == Cell.OBSTACLE:
                    Map._pad_obstacle_surrounding_with_virtual_wall(arena, row, column)

    @staticmethod
    def _pad_obstacle_surrounding_with_virtual_wall(arena: List[int], row: int, column: int) -> None:
        # north
        if is_within_arena_range(row - 1, column) and arena[row - 1][column] == 0:
            arena[row - 1][column] = Cell.VIRTUAL_WALL.value
        # south
        if is_within_arena_range(row + 1, column) and arena[row + 1][column] == 0:
            arena[row + 1][column] = Cell.VIRTUAL_WALL.value
        # east
        if is_within_arena_range(row, column + 1) and arena[row][column + 1] == 0:
            arena[row][column + 1] = Cell.VIRTUAL_WALL.value
        # west
        if is_within_arena_range(row, column - 1) and arena[row][column - 1] == 0:
            arena[row][column - 1] = Cell.VIRTUAL_WALL.value
        # north east
        if is_within_arena_range(row - 1, column + 1) and arena[row - 1][column + 1] == 0:
            arena[row - 1][column + 1] = Cell.VIRTUAL_WALL.value
        # north west
        if is_within_arena_range(row - 1, column - 1) and arena[row - 1][column - 1] == 0:
            arena[row - 1][column - 1] = Cell.VIRTUAL_WALL.value
        # south east
        if is_within_arena_range(row + 1, column + 1) and arena[row + 1][column + 1] == 0:
            arena[row + 1][column + 1] = Cell.VIRTUAL_WALL.value
        # south west
        if is_within_arena_range(row + 1, column - 1) and arena[row + 1][column - 1] == 0:
            arena[row + 1][column - 1] = Cell.VIRTUAL_WALL.value

    @staticmethod
    def _set_unexplored_cell_as_virtual_wall(virtual_arena, explored_arena) -> None:
        """
        Pads the unexplored area in the arena with virtual wall

        :param virtual_arena: The obstacle arena
        :param explored_arena: The explored arena
        :return:
        """
        for row in range(constants.ARENA_HEIGHT):
            for column in range(constants.ARENA_WIDTH):
                if explored_arena[row][column] != Cell.UNEXPLORED:
                    continue

                virtual_arena[row][column] = Cell.VIRTUAL_WALL.value

    @staticmethod
    def point_is_not_free_area(arena: List[int], point_to_check: List[int]) -> bool:
        """
        Checks if the cell in the arena is a free area

        :param arena: The arena to check
        :param point_to_check: The coordinate point to check
        :return: True if the coordinate point is a not a free area, False otherwise
        """
        row, column = point_to_check
        return arena[row][column] != Cell.FREE_AREA

    def generate_map_descriptor(self, explored_map: List[int], obstacle_map: List[int]) -> Tuple[str, str]:
        """
        Generates the map descriptor

        :param explored_map: The exploration map
        :param obstacle_map: The obstacle map
        :return: A tuple of p1 and p2 map descriptor
        """
        reversed_explored_map = list(reversed(explored_map))
        reversed_obstacle_map = list(reversed(obstacle_map))

        explored_binary_string = '11'
        obstacle_binary_string = ''

        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                explored_cell = reversed_explored_map[x][y]
                obstacle_cell = reversed_obstacle_map[x][y]

                if explored_cell == Cell.EXPLORED:
                    explored_binary_string += '1'
                    obstacle_binary_string += str(obstacle_cell)

                else:
                    explored_binary_string += '0'

        explored_binary_string += '11'

        if len(obstacle_binary_string) % 8 != 0:
            padding_length = 8 - len(obstacle_binary_string) % 8
            obstacle_binary_string += '0' * padding_length

        p1 = self._convert_binary_string_to_hex(explored_binary_string)
        p2 = self._convert_binary_string_to_hex(obstacle_binary_string)

        return p1, p2

    def _convert_binary_string_to_hex(self, binary_string) -> str:
        """
        Converts the binary string to hex string

        :param binary_string: Binary string of the map
        :return: The hex string representation of the binary string
        """
        hex_string = f'{int(binary_string, 2):X}'  # :X is used to format the f-string in hexadecimal upper case
        padding_length = ceil(len(binary_string) / 4) - len(hex_string)

        return '0' * padding_length + hex_string

    def _convert_hex_to_binary(self, hex_string) -> str:
        """
        Converts the hex string to binary string

        :param hex_string: Hex string of the map
        :return: The binary string representation of the binary string
        """
        binary_string = f"{int(hex_string, 16):b}"
        padding_length = len(hex_string) * 4 - len(binary_string)

        return '0' * padding_length + binary_string

    def decode_map_descriptor_for_fastest_path_task(self, explored_hex_string, obstacle_hex_string) -> list:
        """
        Decodes the MDF map descriptor to a 2D list arena

        :param explored_hex_string: The MDF string p1
        :param obstacle_hex_string: The MDP string p2
        :return: The decoded arena
        """
        arena = []

        explored_binary_string = self._convert_hex_to_binary(explored_hex_string)
        obstacle_binary_string = self._convert_hex_to_binary(obstacle_hex_string)
        explored_count = 2
        obstacle_count = 0

        for row in range(constants.ARENA_HEIGHT):
            row_cells = []

            for column in range(constants.ARENA_WIDTH):
                is_explored = explored_binary_string[explored_count] == '1'
                explored_count += 1

                if is_explored:
                    is_obstacle = obstacle_binary_string[obstacle_count] == '1'
                    row_cells.append(Cell.OBSTACLE.value if is_obstacle else Cell.FREE_AREA.value)
                    obstacle_count += 1

                else:
                    row_cells.append(Cell.FREE_AREA.value)

            arena.append(row_cells)

        return list(reversed(arena))


if __name__ == "__main__":
    test_map = Map()

    # testing = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0]]
    #
    fully_explored_map = _EXPLORED_FULL_MAP
    # p1, p2 = test_map.generate_map_descriptor(fully_explored_map, testing)
    # print(p1)
    # print(p2)

    explored_arena_descriptor, obstacle_arena_descriptor = test_map.load_map_from_disk('./maps/test_1.txt')
    full_arena = test_map.decode_map_descriptor_for_fastest_path_task(explored_arena_descriptor,
                                                                      obstacle_arena_descriptor)
    # p1, p2 = test_map.generate_map_descriptor(fully_explored_map, test_map.sample_arena)
    # print(p2)
    #
    for row in full_arena:
        print(row)
