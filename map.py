from math import ceil

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

# _EXPLORED_MAP = [
#     [0 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
# ]

_EXPLORED_MAP = [
    [1 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
]

# _OBSTACLE_MAP = [
#     [0 for _ in range(constants.ARENA_WIDTH)] for _ in range(constants.ARENA_HEIGHT)
# ]

_OBSTACLE_MAP = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
]


def is_within_arena_range(x: int, y: int) -> bool:
    """
    Checks if the coordinate of the cell in the arena is within the range (20 X 15)
    :param x: x coordinate of the current cell in the arena
    :param y: y coordinate of the current cell in the arena
    :return: True if the coordinates are with in the range of the arena, else False
    """
    return (0 <= x < constants.ARENA_HEIGHT) and (0 <= y < constants.ARENA_WIDTH)


class Map:
    def __init__(self):
        self.explored_map = _EXPLORED_MAP  # 2D list
        self.obstacle_map = _OBSTACLE_MAP  # 2D list
        self.sample_arena = SAMPLE_ARENA

    def load_map_from_disk(self, filename: str) -> list:
        """
        Loads the map descriptor file from disk. Used for fastest path

        :param filename: File path directory of the arena
        :return: The P2 string descriptor of the arena
        """
        # TODO: Determine if need to handle IO error if the file was not found. Keep in mind with the integration
        #  with the GUI
        with open(filename, 'r') as file_reader_handler:
            string_descriptors = file_reader_handler.readline()

        return string_descriptors.split('|')

    def set_virtual_walls_on_map(self, arena):
        """
        Pads virtual wall around obstacles and the surrounding of the area.
        Used for fastest path

        :return: None
        """
        self._set_virtual_wall_around_arena(arena)
        self._set_virtual_walls_around_obstacles(arena)

    def _set_virtual_wall_around_arena(self, arena) -> None:
        for x in range(constants.ARENA_WIDTH):
            if arena[0][x] != 1:
                arena[0][x] = constants.VIRTUAL_WALL
            if arena[constants.ARENA_HEIGHT - 1][x] != 1:
                arena[constants.ARENA_HEIGHT - 1][x] = constants.VIRTUAL_WALL

        for y in range(constants.ARENA_HEIGHT):
            if arena[y][0] != 1:
                arena[y][0] = constants.VIRTUAL_WALL
            if arena[y][constants.ARENA_WIDTH - 1] != 1:
                arena[y][constants.ARENA_WIDTH - 1] = constants.VIRTUAL_WALL

    def _set_virtual_walls_around_obstacles(self, arena) -> None:
        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                if arena[x][y] == constants.OBSTACLE:
                    self._pad_obstacle_surrounding_with_virtual_wall(arena, x, y)

    def _pad_obstacle_surrounding_with_virtual_wall(self, arena: list, x: int, y: int) -> None:
        # north
        if is_within_arena_range(x - 1, y) and arena[x - 1][y] == 0:
            arena[x - 1][y] = 2
        # south
        if is_within_arena_range(x + 1, y) and arena[x + 1][y] == 0:
            arena[x + 1][y] = 2
        # east
        if is_within_arena_range(x, y + 1) and arena[x][y + 1] == 0:
            arena[x][y + 1] = 2
        # west
        if is_within_arena_range(x, y - 1) and arena[x][y - 1] == 0:
            arena[x][y - 1] = 2
        # north east
        if is_within_arena_range(x - 1, y + 1) and arena[x - 1][y + 1] == 0:
            arena[x - 1][y + 1] = 2
        # north west
        if is_within_arena_range(x - 1, y - 1) and arena[x - 1][y - 1] == 0:
            arena[x - 1][y - 1] = 2
        # south east
        if is_within_arena_range(x + 1, y + 1) and arena[x + 1][y + 1] == 0:
            arena[x + 1][y + 1] = 2
        # south west
        if is_within_arena_range(x + 1, y - 1) and arena[x + 1][y - 1] == 0:
            arena[x + 1][y - 1] = 2

    def generate_map_descriptor(self, explored_map, obstacle_map):
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

    def _convert_binary_string_to_hex(self, binary_string):
        """
        Converts the binary string to hex string
        :param binary_string:
        :return:
        """
        hex_string = f'{int(binary_string, 2):X}'  # :X is used to format the f-string in hexadecimal upper case
        padding_length = ceil(len(binary_string) / 4) - len(hex_string)

        return '0' * padding_length + hex_string

    def _convert_hex_to_binary(self, hex_string):
        binary_string = f"{int(hex_string, 16):b}"
        padding_length = len(hex_string) * 4 - len(binary_string)

        return '0' * padding_length + binary_string

    def decode_map_descriptor_for_fastest_path_task(self, explored_hex_string, obstacle_hex_string):
        arena = []

        explored_binary_string = self._convert_hex_to_binary(explored_hex_string)
        obstacle_binary_string = self._convert_hex_to_binary(obstacle_hex_string)
        explored_count = 2
        obstacle_count = 0

        for x in range(constants.ARENA_HEIGHT):
            row = []

            for y in range(constants.ARENA_WIDTH):
                is_explored = explored_binary_string[explored_count] == '1'
                explored_count += 1

                if is_explored:
                    is_obstacle = obstacle_binary_string[obstacle_count] == '1'
                    row.append(Cell.OBSTACLE.value if is_obstacle else Cell.FREE_AREA.value)
                    obstacle_count += 1

                else:
                    row.append(Cell.FREE_AREA.value)

            arena.append(row)

        return list(reversed(arena))


if __name__ == "__main__":
    test_map = Map()

    explored_arena_descriptor, obstacle_arena_descriptor = test_map.load_map_from_disk('./maps/sample_arena_0.txt')
    full_arena = test_map.decode_map_descriptor_for_fastest_path_task(explored_arena_descriptor,
                                                                      obstacle_arena_descriptor)

    print('Arena:')
    for row in full_arena:
        print(row)

    test_explored = test_map.explored_map
    print('\nDescriptor')
    p1, p2 = test_map.generate_map_descriptor(test_explored, full_arena)
    print(p1)
    print(p1 == explored_arena_descriptor)

    print(p2)
    print(p2 == obstacle_arena_descriptor)
