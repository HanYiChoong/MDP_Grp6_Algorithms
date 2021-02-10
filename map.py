from utils import constants

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

def _pad_obstacle_surrounding_with_virtual_wall(arena: list, x: int, y: int) -> None:
    # north
    if _is_within_arena_range(x - 1, y) and arena[x - 1][y] == 0:
        arena[x - 1][y] = 2
    # south
    if _is_within_arena_range(x + 1, y) and arena[x + 1][y] == 0:
        arena[x + 1][y] = 2
    # east
    if _is_within_arena_range(x, y + 1) and arena[x][y + 1] == 0:
        arena[x][y + 1] = 2
    # west
    if _is_within_arena_range(x, y - 1) and arena[x][y - 1] == 0:
        arena[x][y - 1] = 2
    # north east
    if _is_within_arena_range(x - 1, y + 1) and arena[x - 1][y + 1] == 0:
        arena[x - 1][y + 1] = 2
    # north west
    if _is_within_arena_range(x - 1, y - 1) and arena[x - 1][y - 1] == 0:
        arena[x - 1][y - 1] = 2
    # south east
    if _is_within_arena_range(x + 1, y + 1) and arena[x + 1][y + 1] == 0:
        arena[x + 1][y + 1] = 2
    # south west
    if _is_within_arena_range(x + 1, y - 1) and arena[x + 1][y - 1] == 0:
        arena[x + 1][y - 1] = 2


def _is_within_arena_range(x: int, y: int) -> bool:
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
        self.fastest_path_map_original = SAMPLE_ARENA
        self.fastest_path_map_with_virtual_wall = SAMPLE_ARENA

    def load_map_from_disk(self, filename):
        raise NotImplementedError

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
                if self.fastest_path_map_with_virtual_wall[x][y] == constants.OBSTACLE:
                    _pad_obstacle_surrounding_with_virtual_wall(self.fastest_path_map_with_virtual_wall, x, y)

    def _pad_obstacle_surrounding_with_virtual_wall(self, x: int, y: int) -> None:
        # north
        if _is_within_arena_range(x - 1, y) and self.fastest_path_map_with_virtual_wall[x - 1][y] == 0:
            self.fastest_path_map_with_virtual_wall[x - 1][y] = 2
        # south
        if _is_within_arena_range(x + 1, y) and self.fastest_path_map_with_virtual_wall[x + 1][y] == 0:
            self.fastest_path_map_with_virtual_wall[x + 1][y] = 2
        # east
        if _is_within_arena_range(x, y + 1) and self.fastest_path_map_with_virtual_wall[x][y + 1] == 0:
            self.fastest_path_map_with_virtual_wall[x][y + 1] = 2
        # west
        if _is_within_arena_range(x, y - 1) and self.fastest_path_map_with_virtual_wall[x][y - 1] == 0:
            self.fastest_path_map_with_virtual_wall[x][y - 1] = 2
        # north east
        if _is_within_arena_range(x - 1, y + 1) and self.fastest_path_map_with_virtual_wall[x - 1][y + 1] == 0:
            self.fastest_path_map_with_virtual_wall[x - 1][y + 1] = 2
        # north west
        if _is_within_arena_range(x - 1, y - 1) and self.fastest_path_map_with_virtual_wall[x - 1][y - 1] == 0:
            self.fastest_path_map_with_virtual_wall[x - 1][y - 1] = 2
        # south east
        if _is_within_arena_range(x + 1, y + 1) and self.fastest_path_map_with_virtual_wall[x + 1][y + 1] == 0:
            self.fastest_path_map_with_virtual_wall[x + 1][y + 1] = 2
        # south west
        if _is_within_arena_range(x + 1, y - 1) and self.fastest_path_map_with_virtual_wall[x + 1][y - 1] == 0:
            self.fastest_path_map_with_virtual_wall[x + 1][y - 1] = 2

    def generate_map_descriptor(self):
        reversed_explored_map = list(reversed(self.explored_map))

        p1 = self._get_p1_hex_string(reversed_explored_map)

        obstacles_str_list = self._find_obstacles_in_arena_and_fill_in_obstacle_list(reversed_explored_map)
        self._pad_obstacles_string_list_if_not_full_length(obstacles_str_list)

        obstacles_hex_list = self._convert_obstacle_string_list_to_hex_list(obstacles_str_list)
        p2 = ''.join(obstacles_hex_list)

        return p1.upper(), p2.upper()

    def _get_p1_hex_string(self, reversed_explored_map):
        p1 = '11'
        explored_hex_str = [str(i) for sub in reversed_explored_map for i in sub]
        explored_hex_str.append('1')
        explored_hex_str.append('1')
        p1 += "".join(explored_hex_str)

        return hex(int(p1, 2))[2:]

    def _find_obstacles_in_arena_and_fill_in_obstacle_list(self, reversed_explored_map):
        # find obstacles in the explored map
        obstacles_str_list = []

        reversed_obstacle_list = list(reversed(self.obstacle_map))
        # P2
        # find obstacles in the explored map
        for y, row in enumerate(reversed_explored_map):
            for x, val in enumerate(row):
                if val:
                    obstacles_str_list.append(str(reversed_obstacle_list[y][x]))

        return obstacles_str_list

    def _pad_obstacles_string_list_if_not_full_length(self, obstacles_str_list):
        # determine if obstacles are of full length (multiples of 8 bits)
        padding_len = 8 - (len(obstacles_str_list) % 8)
        obstacles_str_list.extend(['0' for _ in range(padding_len)])

    def _convert_obstacle_string_list_to_hex_list(self, obstacles_str_list):
        obstacles_hex_list = []
        # convert binary to hex (in batches, 1 hex = 4 bit str)
        # will there be a chance that the number of bit string are less than 4?
        for i in range(0, len(obstacles_str_list) - 4, 4):
            obstacle_bit_string = ''.join(obstacles_str_list[i:i + 4])
            hex_value = hex(int(obstacle_bit_string, 2))[2:]

            obstacles_hex_list.append(hex_value)

        return obstacles_hex_list

    def decode_map_descriptor_for_fastest_path_task(self, obstacle_hex_string):
        map_binary = self._convert_hex_string_to_binary_list(obstacle_hex_string)

        processed_map = self._reshape_binary_list_to_2d_matrix(map_binary, constants.ARENA_HEIGHT,
                                                               constants.ARENA_WIDTH)

        self.fastest_path_map_original = processed_map

    def _convert_hex_string_to_binary_list(self, obstacle_hex_string):
        map_binary = []
        # convert hex string to binary string
        for hex_value in obstacle_hex_string:
            binary_from_hex = bin(int(hex_value, 16))[2:] \
                .zfill(4)  # prepends 0 if in front of binary
            map_binary.extend(binary_from_hex)

        # convert each bit string to int
        map_binary = [int(x) for x in map_binary]

        return map_binary

    def _reshape_binary_list_to_2d_matrix(self, map_binary, height, width):
        reversed_map_binary_list = list(reversed(map_binary))
        # convert binary to 2d map
        processed_map = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(reversed_map_binary_list[y * width + x])

            reversed_row = list(reversed(row))
            processed_map.append(reversed_row)

        return processed_map


if __name__ == "__main__":
    test_map = Map()

    test_map.decode_map_descriptor_for_fastest_path_task(
        '0700000000000001C0000200040008001020204040800100020004000038000000002000420')
