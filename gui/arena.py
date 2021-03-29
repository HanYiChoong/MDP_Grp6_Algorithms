import tkinter as tk
from os import curdir
from os.path import abspath
from typing import List, Tuple

from algorithms.fastest_path_solver import Node
from configs import gui_config
from map import Map
from utils import constants
from utils.enums import Direction, Cell

_CANVAS_WIDTH = gui_config.WINDOW_WIDTH_IN_PIXELS // 1.69
_GRID_CELL_SIZE = 30
_GRID_STARTING_ROW = _CANVAS_WIDTH // 5
_GRID_STARTING_COLUMN = 50
_ROBOT_BODY_SIZE_OFFSET_TOP_LEFT = 20
_ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT = _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT * 2


class Arena(tk.Frame):
    def __init__(self, parent, robot, map_reference, **kwargs):
        """

        :param parent:
        :param robot:
        :param map_reference:
        :param kwargs:
        """
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

    def generate_arena_on_canvas(self, loaded_arena: List[int] = None) -> None:
        """
        Paints the arena and the robot position on the canvas

        :param loaded_arena: The arena to paint on the canvas
        """
        if loaded_arena is None:
            self.arena_map = self.map_reference.sample_arena
        else:
            self.arena_map = loaded_arena

        if len(self.canvas_arena_cell_reference) > 0:
            self.canvas_arena_cell_reference = []

        Map.set_virtual_walls_on_map(self.arena_map)

        for row in range(constants.ARENA_HEIGHT):
            arena_row = []

            for column in range(constants.ARENA_WIDTH):
                colour = self._get_cell_colour(row, column)

                x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW
                y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN
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

    def set_robot_starting_position(self, point: List[int] = None, direction: 'Direction' = None) -> None:
        """
        Sets the robot position and paints the robot on the canvas

        :param point: The coordinate position of the robot
        :param direction: The direction of the robot
        """
        if point is None:
            row, column = constants.ROBOT_START_POINT
        else:
            row, column = point

        if direction is None:
            initial_direction = Direction.NORTH
        else:
            initial_direction = direction

        self._draw_robot_in_arena(row, column, initial_direction)

    def _draw_robot_in_arena(self, row: int, column: int, direction_facing: 'Direction') -> None:
        """
        Draws the robot on the canvas

        :param row: The row coordinate of the robot in the arena
        :param column: The column coordinate of the robot in the arena
        :param direction_facing: The facing direction of the robot in the arena
        """
        self._draw_robot_body(row, column)

        x1, y1, x2, y2 = self._get_circle_points_base_on_direction(row, column, direction_facing)
        self.canvas_robot_header = self.canvas.create_oval(x1, y1,
                                                           x2, y2,
                                                           fill=gui_config.ROBOT_HEADER_COLOUR)

    def _get_circle_points_base_on_direction(self,
                                             row: int,
                                             column: int,
                                             direction_facing) -> Tuple[int, int, int, int]:
        """
        Get the coordinates of the robot direction to be drawn on the canvas

        :param row: The row coordinate of the robot
        :param column: The column coordinate of the robot
        :param direction_facing: The facing direction of the robot
        :return: A tuple of coordinates to draw the direction of the robot on the canvas
        """
        if direction_facing == Direction.NORTH:
            x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW + 10
            y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN - 15
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2
        if direction_facing == Direction.SOUTH:
            x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW + 10
            y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN + 35
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == Direction.WEST:
            x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW - 15
            y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN + 13
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

        if direction_facing == Direction.EAST:
            x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW + 35
            y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN + 10
            x2 = x1 + _GRID_CELL_SIZE - 20
            y2 = y1 + _GRID_CELL_SIZE - 20

            return x1, y1, x2, y2

    def _draw_robot_body(self, row: int, column: int) -> None:
        """
        Draws the robot on the canvas

        :param row: The row coordinate of the robot
        :param column: The column coordinate of the robot
        """
        x1 = column * _GRID_CELL_SIZE + _GRID_STARTING_ROW - _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT
        y1 = row * _GRID_CELL_SIZE + _GRID_STARTING_COLUMN - _ROBOT_BODY_SIZE_OFFSET_TOP_LEFT
        x2 = x1 + _GRID_CELL_SIZE + _ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT
        y2 = y1 + _GRID_CELL_SIZE + _ROBOT_BODY_SIZE_OFFSET_BOTTOM_RIGHT
        self.canvas_robot_body = self.canvas.create_oval(x1, y1,
                                                         x2, y2,
                                                         fill=gui_config.ROBOT_BODY_COLOUR)

    def _get_cell_colour(self, row: int, column: int) -> str:
        """
        Determine the colour of the cell in the arena based on the exploration, fastest path or obstacle map

        :param row: The row coordinate of the robot
        :param column: The column coordinate of the robot
        :return: The colour of the cell
        """
        if self._is_start_area(row, column) or self._is_goal_area(row, column):
            colour = gui_config.START_GOAL_NODE_COLOUR

        elif self.arena_map[row][column] == Cell.OBSTACLE:
            colour = gui_config.OBSTACLE_NODE_COLOUR

        else:
            colour = gui_config.FREE_AREA_NODE_COLOUR

        return colour

    def _is_start_area(self, row: int, column: int) -> None:
        """
        Determines if the row and column provided is within the arena range

        :param row: Row index
        :param column: Column index
        :return: True if the coordinate point provided is within the arena range. False otherwise
        """
        start_row_upper_bound = constants.ARENA_HEIGHT - 1
        start_row_lower_bound = start_row_upper_bound - 2

        return (0 <= column <= 2) and (start_row_lower_bound <= row <= start_row_upper_bound)

    def _is_goal_area(self, row: int, column: int) -> None:
        """
        Determines if the row and column provided is within the arena range

        :param row: Row index
        :param column: Column index
        :return: True if the coordinate point provided is within the arena range. False otherwise
        """
        start_column_upper_bound = constants.ARENA_WIDTH - 1
        start_column_lower_bound = start_column_upper_bound - 2

        return (0 <= row <= 2) and (start_column_lower_bound <= column <= start_column_upper_bound)

    def _is_way_point(self, row: int, column: int) -> bool:
        """
        Determines if the row and column provided is a waypoint

        :param row: Row index
        :param column: Column index
        :return: True if the coordinate point provided is within the arena range. False otherwise
        """
        return row == self._way_point[0] and column == self._way_point[1]

    def update_robot_point_on_map_with_node(self, node: 'Node') -> None:
        """
        Gets the node coordinate and updates the robot's position on the arena

        :param node: Node of the fastest path in the arena
        """
        row, column = node.point

        self._move_robot_in_simulator(node.direction_facing, row, column)

    def _move_robot_in_simulator(self, direction: 'Direction', row: int, column: int) -> None:
        """
        Updates the robot's position on the arena

        :param direction: The direction of the robot
        :param row: The row coordinate of the robot
        :param column: The column coordinate of the robot
        """
        self.canvas.delete(self.canvas_robot_header)
        self.canvas.delete(self.canvas_robot_body)

        self._draw_robot_in_arena(row, column, direction)

    def set_way_point_on_canvas(self, way_point: List[int]) -> None:
        """
        Sets the waypoint coordinate on the arena GUI

        :param way_point: Waypoint coordinate
        """
        colour = gui_config.WAYPOINT_NODE_COLOUR

        self._way_point = way_point

        self._colour_waypoint_on_canvas(way_point, colour)

    def remove_way_point_on_canvas(self, way_point: List[int]) -> None:
        colour = gui_config.FREE_AREA_NODE_COLOUR

        self._way_point = way_point

        self._colour_waypoint_on_canvas(way_point, colour)

    def _colour_waypoint_on_canvas(self, way_point: List[int], colour: 'str') -> None:
        """
        Sets the colour of the waypoint in the arena

        :param way_point: The coordinate of the waypoint
        :param colour: The colour of the waypoint
        :return:
        """
        row, column = way_point

        self.canvas.itemconfig(self.canvas_arena_cell_reference[row][column], fill=colour)

    def reset_map(self) -> None:
        """
        Resets the map on the GUI to its original state
        """
        for row in range(constants.ARENA_HEIGHT):
            for column in range(constants.ARENA_WIDTH):
                colour = self._get_cell_colour(row, column)
                self.canvas.itemconfig(self.canvas_arena_cell_reference[row][column], fill=colour)

        self.canvas.delete(self.canvas_robot_header)
        self.canvas.delete(self.canvas_robot_body)

        self.set_robot_starting_position()
        self.map_reference.reset_exploration_maps()

    def load_map_from_disk(self, filename: str) -> Tuple[List[int], str, str]:
        """
        Loads the map in the GUI from a text file

        :param filename: the filename of the text file
        :return: A tuple of the generated arena and the map descriptor from the text file
        """
        filename_with_extension = f'{filename}.txt'
        root_project_directory = f'{abspath(curdir)}\\maps'
        file_path = f'{root_project_directory}\\{filename_with_extension}'

        p1, p2 = self.map_reference.load_map_from_disk(file_path)
        generated_arena = self.map_reference.decode_map_descriptor_for_fastest_path_task(p1, p2)
        self.generate_arena_on_canvas(generated_arena)
        self.map_reference.sample_arena = generated_arena

        return generated_arena, p1, p2

    def update_robot_position_on_map(self):
        """
        Updates the robot position on the map
        """
        row, column = self.robot.point
        direction = self.robot.direction
        self._move_robot_in_simulator(direction, row, column)

        for i in range(row - 1, row + 2):
            for j in range(column - 1, column + 2):
                self.mark_sensed_area_as_explored_on_map([i, j])

    def mark_sensed_area_as_explored_on_map(self, point: List[int]) -> None:
        """
        Sets the colour of the cell in the arena GUI

        :param point: The coordinate point of the cell to mark
        """
        row, column = point

        if self._is_start_area(row, column) or self._is_goal_area(row, column):
            colour = gui_config.START_GOAL_NODE_COLOUR
        elif self.map_reference.obstacle_map[row][column] == Cell.OBSTACLE:
            colour = gui_config.OBSTACLE_NODE_COLOUR
        else:
            colour = gui_config.FREE_AREA_NODE_COLOUR

        self.canvas.itemconfig(self.canvas_arena_cell_reference[row][column], fill=colour)

    def set_unexplored_arena_map(self) -> None:
        """
        Sets the arena as unexplored on the GUI
        """

        for x in range(constants.ARENA_HEIGHT):
            for y in range(constants.ARENA_WIDTH):
                if self._is_start_area(x, y) or self._is_goal_area(x, y):
                    continue

                unexplored_cell_colour = gui_config.UNEXPLORED_NODE_COLOUR
                self.canvas.itemconfig(self.canvas_arena_cell_reference[x][y], fill=unexplored_cell_colour)
