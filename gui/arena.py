import tkinter as tk

# from map import load_map_from_disk  # filler import
from robots.robot import Robot
from utils import constants

_CANVAS_WIDTH = constants.WINDOW_WIDTH_IN_PIXELS // 1.69
_GRID_CELL_SIZE = 30
_GRID_STARTING_X = _CANVAS_WIDTH // 5
_GRID_STARTING_Y = 50
_ROBOT_BODY_SIZE_OFFSET_TOP_LEFT = 20
_ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT = _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT * 2


class Arena(tk.Frame):
    # TODO: Get the map from left sidebar and create arena in canvas
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.arena_grid = []
        self.arena_map = None
        self._way_point = None
        self.canvas_robot_header = None
        self.canvas_robot_body = None
        self.robot = Robot(constants.START_POSITION_X, constants.START_POSITION_Y)

        self.arena_grid_canvas = tk.Canvas(self, width=_CANVAS_WIDTH, height=constants.WINDOW_HEIGHT_IN_PIXELS,
                                           bg='white')
        self._generate_arena_map_on_canvas()
        self.arena_grid_canvas.grid(row=0, column=1)

    def _generate_arena_map_on_canvas(self):
        if not self.arena_map:
            # default map
            self.arena_map = self.robot.map_manager.sample_arena
            self.robot.map_manager.set_virtual_walls_on_map(self.arena_map)

        for y in range(constants.ARENA_WIDTH):
            arena_row = []

            for x in range(constants.ARENA_HEIGHT):
                colour = self._get_cell_colour(x, y)

                x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X
                y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y
                x2 = x1 + _GRID_CELL_SIZE
                y2 = y1 + _GRID_CELL_SIZE
                rectangle_reference = self.arena_grid_canvas.create_rectangle(x1, y1, x2, y2, fill=colour)

                arena_row.append(rectangle_reference)

            self.arena_grid.append(arena_row)

        self._set_robot_starting_position()

    def _set_robot_starting_position(self):
        self._draw_robot_in_arena(18, 1, constants.BEARING['north'])  # Robot starting position

    def _draw_robot_in_arena(self, x, y, direction_facing):
        self._draw_robot_body(x, y)

        x1, y1, x2, y2 = self._get_circle_points_base_on_direction(x, y, direction_facing)
        self.canvas_robot_header = self.arena_grid_canvas.create_oval(x1,
                                                                      y1,
                                                                      x2,
                                                                      y2,
                                                                      fill=constants.ROBOT_HEADER_COLOUR)

    def _get_circle_points_base_on_direction(self, x, y, direction_facing):
        if direction_facing == constants.BEARING['north']:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X + 10
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y - 15
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2
        if direction_facing == constants.BEARING['south']:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X + 10
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y + 35
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == constants.BEARING['west']:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X - 15
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y + 13
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == constants.BEARING['east']:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X + 35
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y + 10
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

    def _draw_robot_body(self, x, y):
        x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X - _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT
        y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y - _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT
        x2 = x1 + _GRID_CELL_SIZE + _ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT
        y2 = y1 + _GRID_CELL_SIZE + _ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT
        self.canvas_robot_body = self.arena_grid_canvas.create_oval(x1,
                                                                    y1,
                                                                    x2,
                                                                    y2,
                                                                    fill=constants.ROBOT_BODY_COLOUR)

    def _get_cell_colour(self, x, y):
        if self._is_start_area(x, y) or self._is_goal_area(x, y):
            colour = constants.START_GOAL_NODE_COLOUR

        elif self.arena_map[x][y] == constants.FREE_AREA:
            colour = constants.FREE_AREA_NODE_COLOUR

        elif self.arena_map[x][y] == constants.OBSTACLE:
            colour = constants.OBSTACLE_NODE_COLOUR

        elif self.arena_map[x][y] == constants.VIRTUAL_WALL:
            colour = constants.VIRTUAL_WALL_NODE_COLOUR

        else:
            colour = constants.FREE_AREA_NODE_COLOUR

        return colour

    def _is_start_area(self, x, y):
        start_x_upper_bound = constants.ARENA_HEIGHT - 1
        start_x_lower_bound = start_x_upper_bound - 2

        return (0 <= y <= 2) and (start_x_lower_bound <= x <= start_x_upper_bound)

    def _is_goal_area(self, x, y):
        start_y_upper_bound = constants.ARENA_WIDTH - 1
        start_y_lower_bound = start_y_upper_bound - 2

        return (0 <= x <= 2) and (start_y_lower_bound <= y <= start_y_upper_bound)

    def _is_way_point(self, x, y):
        return x == self._way_point[0] and y == self._way_point[1]

    def update_cell_on_map(self, node):
        x, y = node.point

        self.arena_grid_canvas.delete(self.canvas_robot_header)
        self.arena_grid_canvas.delete(self.canvas_robot_body)
        self._draw_robot_in_arena(x, y, node.direction_facing)

    def _get_direction_name_from_bearing_value(self, bearing):
        return constants.BEARING_KEYS[constants.BEARING_VALUES.index(bearing)]

    def set_way_point(self, way_point):
        colour = constants.WAYPOINT_NODE_COLOUR

        x, y = way_point
        self._way_point = way_point

        self.arena_grid_canvas.itemconfig(self.arena_grid[y][x], fill=colour)

    def _get_grid_coordinates_on_arena_canvas(self, x, y):
        return self.arena_grid_canvas.coords(self.arena_grid[y][x])

    def reset_map(self):
        for y in range(constants.ARENA_WIDTH):
            for x in range(constants.ARENA_HEIGHT):
                colour = self._get_cell_colour(x, y)
                self.arena_grid_canvas.itemconfig(self.arena_grid[y][x], fill=colour)

        self.arena_grid_canvas.delete(self.canvas_robot_header)
        self.arena_grid_canvas.delete(self.canvas_robot_body)
        self._set_robot_starting_position()
