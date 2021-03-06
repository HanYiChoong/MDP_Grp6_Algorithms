# Arena related constants

ARENA_WIDTH = 15
ARENA_HEIGHT = 20

ROBOT_START_POINT = [18, 1]
ROBOT_END_POINT = [1, 13]

NORTH_POSITION = (-1, 0)
SOUTH_POSITION = (1, 0)
EAST_POSITION = (0, 1)
WEST_POSITION = (0, -1)

NEIGHBOURING_POSITIONS = [
    NORTH_POSITION, SOUTH_POSITION, EAST_POSITION, WEST_POSITION
]

MOVE_COST = 1
NO_TURN_COST = 0
TURN_COST_PERPENDICULAR = 2
TURN_COST_OPPOSITE_DIRECTION = 4

DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES = 2048
