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


class Map:
    def set_virtual_walls(self, arena: list) -> None:
        """
        Pads virtual wall around obstacles and the surrounding of the area

        :param arena: 2D list of the arena
        :return: None
        """
        self._set_virtual_wall_around_arena(arena)
        self._set_virtual_walls_around_obstacles(arena)

    def _set_virtual_wall_around_arena(self, arena: list) -> None:
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

    def _set_virtual_walls_around_obstacles(self, arena: list) -> None:
        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                if arena[x][y] == constants.OBSTACLE:
                    self._pad_obstacle_surrounding_with_virtual_wall(arena, x, y)

    def _pad_obstacle_surrounding_with_virtual_wall(self, arena: list, x: int, y: int) -> None:
        # north
        if self._is_within_arena_range(x - 1, y) and arena[x - 1][y] == 0:
            arena[x - 1][y] = 2
        # south
        if self._is_within_arena_range(x + 1, y) and arena[x + 1][y] == 0:
            arena[x + 1][y] = 2
        # east
        if self._is_within_arena_range(x, y + 1) and arena[x][y + 1] == 0:
            arena[x][y + 1] = 2
        # west
        if self._is_within_arena_range(x, y - 1) and arena[x][y - 1] == 0:
            arena[x][y - 1] = 2
        # north east
        if self._is_within_arena_range(x - 1, y + 1) and arena[x - 1][y + 1] == 0:
            arena[x - 1][y + 1] = 2
        # north west
        if self._is_within_arena_range(x - 1, y - 1) and arena[x - 1][y - 1] == 0:
            arena[x - 1][y - 1] = 2
        # south east
        if self._is_within_arena_range(x + 1, y + 1) and arena[x + 1][y + 1] == 0:
            arena[x + 1][y + 1] = 2
        # south west
        if self._is_within_arena_range(x + 1, y - 1) and arena[x + 1][y - 1] == 0:
            arena[x + 1][y - 1] = 2

    def _is_within_arena_range(self, x: int, y: int) -> bool:
        """
        Checks if the coordinate of the cell in the arena is within the range (20 X 15)
        :param x: x coordinate of the current cell in the arena
        :param y: y coordinate of the current cell in the arena
        :return: True if the coordinates are with in the range of the arena, else False
        """
        return (0 <= x < constants.ARENA_HEIGHT) and (0 <= y < constants.ARENA_WIDTH)

    def load_map_from_disk(self):
        # might not need this for now I guess?
        raise NotImplementedError

    def generate_map_descriptor(self):
        raise NotImplementedError

    def decode_map_descriptor(self):
        raise NotImplementedError

    def reset_map(self):
        raise NotImplementedError


if __name__ == "__main__":
    map = Map()
    map.set_virtual_walls(SAMPLE_ARENA)
    for row in SAMPLE_ARENA:
        print(row)
