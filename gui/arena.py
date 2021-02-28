import tkinter as tk
from os import curdir
from os.path import abspath

from configs import gui_config
from map import Map
from utils import constants
from utils.enums import Direction, Cell

_CANVAS_WIDTH = gui_config.WINDOW_WIDTH_IN_PIXELS // 1.69
_GRID_CELL_SIZE = 30
_GRID_STARTING_X = _CANVAS_WIDTH // 5
_GRID_STARTING_Y = 50
_ROBOT_BODY_SIZE_OFFSET_TOP_LEFT = 20
_ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT = _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT * 2


class Arena(tk.Frame):
    def __init__(self, parent, robot, map_reference, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.canvas_arena_cell_reference = []
        self.arena_map = None
        self.map_reference = map_reference
        self.robot = robot
        self._way_point = None
        self.canvas_robot_header = None
        self.canvas_robot_body = None
        self.canvas_repaint_delay_in_ms = None

        self.canvas = tk.Canvas(self,
                                width=_CANVAS_WIDTH,
                                height=gui_config.WINDOW_HEIGHT_IN_PIXELS,
                                bg='white')
        self.generate_arena_on_canvas()
        self.canvas.grid(row=0, column=1)

    def generate_arena_on_canvas(self, loaded_arena=None):
        if loaded_arena is None:
            self.arena_map = self.map_reference.sample_arena
        else:
            self.arena_map = loaded_arena

        if len(self.canvas_arena_cell_reference) > 0:
            self.canvas_arena_cell_reference = []

        Map.set_virtual_walls_on_map(self.arena_map)

        for x in range(constants.ARENA_HEIGHT):
            arena_row = []

            for y in range(constants.ARENA_WIDTH):
                colour = self._get_cell_colour(x, y)

                x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X
                y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y
                x2 = x1 + _GRID_CELL_SIZE
                y2 = y1 + _GRID_CELL_SIZE
                rectangle_reference = self.canvas.create_rectangle(x1, y1,
                                                                   x2, y2,
                                                                   width=3,
                                                                   fill=colour,
                                                                   outline=gui_config.RECTANGLE_OUTLINE)

                arena_row.append(rectangle_reference)

            self.canvas_arena_cell_reference.append(arena_row)

        if self.robot is None:
            self.set_robot_starting_position()
        else:
            self.set_robot_starting_position(self.robot.point, self.robot.direction)

    def set_robot_starting_position(self, point: list = None, direction: 'Direction' = None):
        if point is None:
            x, y = constants.ROBOT_START_POINT
        else:
            x, y = point

        if direction is None:
            initial_direction = Direction.NORTH
        else:
            initial_direction = direction

        self._draw_robot_in_arena(x, y, initial_direction)

    def _draw_robot_in_arena(self, x, y, direction_facing):
        self._draw_robot_body(x, y)

        x1, y1, x2, y2 = self._get_circle_points_base_on_direction(x, y, direction_facing)
        self.canvas_robot_header = self.canvas.create_oval(x1, y1,
                                                           x2, y2,
                                                           fill=gui_config.ROBOT_HEADER_COLOUR)

    def _get_circle_points_base_on_direction(self, x, y, direction_facing):
        if direction_facing == Direction.NORTH:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X + 10
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y - 15
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2
        if direction_facing == Direction.SOUTH:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X + 10
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y + 35
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == Direction.WEST:
            x1 = y * _GRID_CELL_SIZE + _GRID_STARTING_X - 15
            y1 = x * _GRID_CELL_SIZE + _GRID_STARTING_Y + 13
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == Direction.EAST:
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
        self.canvas_robot_body = self.canvas.create_oval(x1, y1,
                                                         x2, y2,
                                                         fill=gui_config.ROBOT_BODY_COLOUR)

    def _get_cell_colour(self, x, y):
        if self._is_start_area(x, y) or self._is_goal_area(x, y):
            colour = gui_config.START_GOAL_NODE_COLOUR

        elif self.arena_map[x][y] == Cell.OBSTACLE:
            colour = gui_config.OBSTACLE_NODE_COLOUR

        else:
            colour = gui_config.FREE_AREA_NODE_COLOUR

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

        self._move_robot_in_simulator(node.direction_facing, x, y)

    def _move_robot_in_simulator(self, direction, x, y):
        self.canvas.delete(self.canvas_robot_header)
        self.canvas.delete(self.canvas_robot_body)

        self._draw_robot_in_arena(x, y, direction)

    def set_way_point(self, way_point):
        colour = gui_config.WAYPOINT_NODE_COLOUR

        x, y = way_point
        self._way_point = way_point

        self.canvas.itemconfig(self.canvas_arena_cell_reference[x][y], fill=colour)

    def reset_map(self):
        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                colour = self._get_cell_colour(x, y)
                self.canvas.itemconfig(self.canvas_arena_cell_reference[x][y], fill=colour)

        self.canvas.delete(self.canvas_robot_header)
        self.canvas.delete(self.canvas_robot_body)

        self.set_robot_starting_position()
        self.map_reference.reset_exploration_maps()

    def load_map_from_disk(self, filename):
        filename_with_extension = f'{filename}.txt'
        root_project_directory = f'{abspath(curdir)}\\maps'
        file_path = f'{root_project_directory}\\{filename_with_extension}'

        p1, p2 = self.map_reference.load_map_from_disk(file_path)
        generated_arena = self.map_reference.decode_map_descriptor_for_fastest_path_task(p1, p2)
        self.generate_arena_on_canvas(generated_arena)
        self.map_reference.sample_arena = generated_arena

        return generated_arena

    def update_robot_position_on_map(self):
        x, y = self.robot.point
        direction = self.robot.direction
        self._move_robot_in_simulator(direction, x, y)

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                self.mark_sensed_area_as_explored_on_map([i, j])

    def mark_sensed_area_as_explored_on_map(self, point):
        x, y = point

        if self._is_start_area(x, y) or self._is_goal_area(x, y):
            colour = gui_config.START_GOAL_NODE_COLOUR
        elif self.map_reference.obstacle_map[x][y] == Cell.OBSTACLE:
            colour = gui_config.OBSTACLE_NODE_COLOUR
        else:
            colour = gui_config.FREE_AREA_NODE_COLOUR

        self.canvas.itemconfig(self.canvas_arena_cell_reference[x][y], fill=colour)

    def set_unexplored_arena_map(self):
        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                if self._is_start_area(x, y) or self._is_goal_area(x, y):
                    continue

                unexplored_cell_colour = gui_config.UNEXPLORED_NODE_COLOUR
                self.canvas.itemconfig(self.canvas_arena_cell_reference[x][y], fill=unexplored_cell_colour)
