# Arena related constants
ARENA_WIDTH = 15
ARENA_HEIGHT = 20

FREE_AREA = 0
OBSTACLE = 1
VIRTUAL_WALL = 2

# Robot bearings
bearing = {
    'north': 0,
    'east': 2,
    'south': 4,
    'west': 6,
    'north_east': 1,
    'south_east': 3,
    'south_west': 5,
    'north_west': 7
}

NORTH_POSITION = (-1, 0)
SOUTH_POSITION = (1, 0)
EAST_POSITION = (0, 1)
WEST_POSITION = (0, -1)
NORTH_EAST_POSITION = (-1, 1)
SOUTH_EAST_POSITION = (1, 1)
SOUTH_WEST_POSITION = (1, -1)
NORTH_WEST_POSITION = (-1, -1)

NEIGHBOURING_POSITIONS = [
    NORTH_POSITION, SOUTH_POSITION, EAST_POSITION, WEST_POSITION
]

NEIGHBOURING_POSITIONS_WITH_DIAGONALS = [
    NORTH_POSITION, SOUTH_POSITION, EAST_POSITION, WEST_POSITION, NORTH_EAST_POSITION, SOUTH_EAST_POSITION,
    SOUTH_WEST_POSITION, NORTH_WEST_POSITION
]
