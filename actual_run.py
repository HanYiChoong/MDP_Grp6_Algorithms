from re import match
from threading import Thread
from time import sleep
from typing import List

from algorithms.exploration import Exploration
from algorithms.fastest_path_solver import AStarAlgorithm
from algorithms.image_recognition_exploration import ImageRecognitionExploration
from configs.gui_config import GUI_TITLE
from gui import RealTimeGUI
from map import Map, is_within_arena_range
from robot import RealRobot
from rpi_service import RPIService
from utils.arguments_constructor import get_parser
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT
from utils.enums import Direction, Movement
from utils.logger import print_error_log

_GUI_REDRAW_INTERVAL = 0.0001
_DEFAULT_TIME_LIMIT_IN_SECONDS = 360
_ARENA_FILENAME = 'sample_arena_1'
_WAYPOINT_REGEX_PATTERN = r'\d+\s\d+'
_SLEEP_DELAY = 0.02


def _convert_to_android_coordinate_format(point_int: List[int]) -> List[str]:
    algo_x, algo_y = point_int

    x = algo_y
    y = abs(19 - algo_x)

    return [str(x), str(y)]


def _decode_android_coordinate_format(point_string: List[str]) -> List[int]:
    android_x, android_y = list(map(int, point_string))

    x = abs(19 - android_y)
    y = android_x
    return [x, y]


class ExplorationRun:
    def __init__(self):
        self.rpi_service = RPIService(self.on_quit)
        self.robot = RealRobot(ROBOT_START_POINT,
                               Direction.EAST,
                               on_move=self.on_move,
                               get_sensor_values=self.rpi_service.receive_sensor_values)
        self.exploration = None
        self.robot_updated_point = None
        self.robot_updated_direction = None

        self.gui = RealTimeGUI()
        self.gui.display_widgets.arena.robot = self.robot

    def on_move(self, movement: 'Movement'):
        sensor_values = self.rpi_service.send_movement_to_rpi_and_get_sensor_values(movement, self.robot)

        self.gui.display_widgets.arena.update_robot_position_on_map()

        return sensor_values

    def start_service(self) -> None:
        self.rpi_service.connect_to_rpi()

        Thread(target=self.interpret_rpi_messages, daemon=True).start()

        self.rpi_service.always_listen_for_instructions()

    def interpret_rpi_messages(self) -> None:
        while True:
            message_header_type, response_message = self.rpi_service.get_message_from_rpi_queue()

            if message_header_type == '' and response_message == '':
                continue

            if message_header_type == RPIService.EXPLORATION_HEADER:
                self.start_exploration_search()
                continue

            if message_header_type == RPIService.NEW_ROBOT_POSITION_HEADER:
                self.decode_and_set_robot_position(response_message)
                continue

            if message_header_type == RPIService.IMAGE_REC_HEADER:
                self.start_image_recognition_search()
                continue

            if message_header_type == RPIService.QUIT_HEADER:
                # TODO: Perform cleanup and close gui or smt idk
                print_error_log('RPI connection closed')
                return

            print_error_log('Invalid command received from RPI')

    def decode_and_set_robot_position(self, message: str) -> None:
        start_point_string: List[str] = self.validate_and_decode_point(message)

        if start_point_string is None:
            return

        start_point: List[int] = _decode_android_coordinate_format(start_point_string)

        self.robot_updated_point = start_point
        self.reset_robot_to_initial_state()

    def validate_and_decode_point(self, message: str):
        matched_pattern = match(_WAYPOINT_REGEX_PATTERN, message)

        if matched_pattern is None:
            print_error_log('Invalid waypoint given!')
            return

        return matched_pattern.group().split(' ')

    def start_exploration_search(self) -> None:
        exploration_arena, obstacle_arena = self._setup_exploration()

        exploration = Exploration(self.robot,
                                  exploration_arena,
                                  obstacle_arena,
                                  self.mark_sensed_area_as_explored,
                                  time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        exploration.start_exploration()
        # self.gui.display_widgets.arena.generate_map_descriptor(exploration_arena, obstacle_arena)
        # TODO: Figure out what to do here after exploration lmao

    def _setup_exploration(self):
        self.gui.display_widgets.arena.reset_exploration_maps()  # Get a fresh copy of map first

        exploration_arena = self.gui.display_widgets.arena.map_reference.explored_map
        obstacle_arena = self.gui.display_widgets.arena.map_reference.explored_map

        self.gui.display_widgets.arena.set_unexplored_arena_map()
        self.reset_robot_to_initial_state()

        return exploration_arena, obstacle_arena

    def mark_sensed_area_as_explored(self, point: List[int]):
        # TODO: maybe add a sleep here?
        self.gui.display_widgets.arena.mark_sensed_area_as_explored_on_map(point)

    def start_image_recognition_search(self):
        exploration_arena, obstacle_arena = self._setup_exploration()

        image_recognition_exploration = ImageRecognitionExploration(self.robot,
                                                                    exploration_arena,
                                                                    obstacle_arena,
                                                                    self.mark_sensed_area_as_explored,
                                                                    on_take_photo=self.on_take_photo,
                                                                    time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        image_recognition_exploration.start_exploration()

    def on_take_photo(self, obstacles: list):
        self.gui.display_widgets.log_area.insert_log_message(f'Taking photo of obstacles {obstacles}')

        self.rpi_service.take_photo(obstacles)

    def reset_robot_to_initial_state(self):
        if self.robot_updated_point is None:
            self.robot.point = ROBOT_START_POINT
        else:
            self.robot.point = self.robot_updated_point

        if self.robot_updated_direction is None:
            self.robot.direction = Direction.EAST
        else:
            self.robot.direction = self.robot_updated_direction

    def on_quit(self):
        if self.exploration is not None:
            self.exploration.is_running = False

    def start_gui(self) -> None:
        self.gui.title(f'{GUI_TITLE} EXPLORATION Run')
        self.gui.resizable(False, False)
        self.gui.mainloop()


class FastestPathRun:
    def __init__(self):
        self.rpi_service = RPIService()
        self.robot = RealRobot(ROBOT_START_POINT,
                               Direction.NORTH,
                               on_move=lambda: None,
                               get_sensor_values=lambda: None)

        self.waypoint = None
        self.robot_updated_point = None
        self.robot_updated_direction = None

        self.gui = RealTimeGUI()
        self.gui.display_widgets.arena.robot = self.robot
        self.canvas_repaint_delay_ms = 1500

        self.map = self.load_map_from_disk()
        self.p1 = None
        self.p2 = None

    def load_map_from_disk(self) -> List[int]:
        generated_arena, p1_descriptor, p2_descriptor = self.gui.display_widgets.arena.load_map_from_disk(
            _ARENA_FILENAME)
        Map.set_virtual_walls_on_map(generated_arena)

        self.p1 = p1_descriptor
        self.p2 = p2_descriptor

        return generated_arena

    def start_service(self) -> None:
        self.rpi_service.connect_to_rpi()

        Thread(target=self.interpret_rpi_messages, daemon=True).start()

        # send mdp string to Android
        self.send_mdf_string_to_android()

        self.rpi_service.always_listen_for_instructions()

    def interpret_rpi_messages(self) -> None:
        while True:
            message_header_type, response_message = self.rpi_service.get_message_from_rpi_queue()

            if message_header_type == '' and response_message == '':
                continue

            if message_header_type == RPIService.WAYPOINT_HEADER:
                self.decode_and_save_waypoint(response_message)
                continue

            if message_header_type == RPIService.NEW_ROBOT_POSITION_HEADER:
                self.decode_and_set_robot_position(response_message)
                continue

            if message_header_type == RPIService.ANDROID_FASTEST_PATH_HEADER:
                self.start_fastest_path_run()
                continue

            if message_header_type == RPIService.QUIT_HEADER:
                # TODO: Perform cleanup and close gui or smt idk
                print_error_log('RPI connection closed')
                return

            print_error_log('Invalid command received from RPI')

    def send_mdf_string_to_android(self):
        payload = f'{RPIService.ANDROID_MDF_STRING_HEADER} {self.p1} {self.p2}'
        self.rpi_service.send_message_with_header_type(RPIService.ANDROID_HEADER, payload)

    def decode_and_save_waypoint(self, message: str):
        waypoint_string: List[str] = self.validate_and_decode_point(message)

        if waypoint_string is None:
            return

        waypoint: List[int] = _decode_android_coordinate_format(waypoint_string)

        y, x = waypoint

        if not is_within_arena_range(x, y) and Map.point_is_not_free_area(self.map, waypoint):
            print_error_log('Waypoint is not within arena range, cannot be an obstacle or virtual wall!')
            return

        if self.waypoint is not None:  # clear old waypoint
            self.gui.display_widgets.arena.remove_way_point_on_canvas(self.waypoint)

        self.waypoint = waypoint

        self.gui.display_widgets.arena.set_way_point_on_canvas(waypoint)

    def validate_and_decode_point(self, message: str):
        matched_pattern = match(_WAYPOINT_REGEX_PATTERN, message)

        if matched_pattern is None:
            print_error_log('Invalid waypoint given!')
            return

        return matched_pattern.group().split(' ')

    def decode_and_set_robot_position(self, message: str):
        start_point_string: List[str] = self.validate_and_decode_point(message)

        if start_point_string is None:
            return

        start_point: List[int] = _decode_android_coordinate_format(start_point_string)

        x, y = start_point

        if not is_within_arena_range(x, y) and Map.point_is_not_free_area(self.map, start_point):
            print_error_log('Start point is not within the arena range, cannot be an obstacle or virtual wall!')
            return

        self.robot_updated_point = start_point
        self.reset_robot_to_initial_state()

    def start_fastest_path_run(self):
        if self.waypoint is None:
            self.gui.display_widgets.log_area.insert_log_message('Waypoint not set!')
            return

        self.reset_robot_to_initial_state()

        solver = AStarAlgorithm(self.map)

        self.gui.display_widgets.log_area.insert_log_message('Finding fastest path...')
        path = solver.run_algorithm(self.robot.point,
                                    self.waypoint,
                                    ROBOT_END_POINT,
                                    self.robot.direction)

        if not path:
            self.gui.display_widgets.log_area.insert_log_message('No fastest path route found...')
            return

        movements = solver.convert_fastest_path_to_movements(path, self.robot.direction)
        arduino_format_movements = solver.consolidate_movements_to_string(movements)

        self.send_movements_to_rpi(arduino_format_movements)
        self.display_result_in_gui(path)

    def send_movements_to_rpi(self, movements: str):
        # Signal fastest path
        self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER,
                                                       RPIService.ARDUINO_FASTEST_PATH_INDICATOR)
        sleep(_SLEEP_DELAY)

        self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER, movements)

    def display_result_in_gui(self, path: list):
        if len(path) <= 0:
            return

        action = path.pop(0)
        self.gui.display_widgets.arena.update_robot_point_on_map_with_node(action)

        self.gui.display_widgets.arena.after(self.canvas_repaint_delay_ms, self.display_result_in_gui, path)

    def reset_robot_to_initial_state(self):
        if self.robot_updated_point is None:
            self.robot.point = ROBOT_START_POINT
        else:
            self.robot.point = self.robot_updated_point

        if self.robot_updated_direction is None:
            self.robot.direction = Direction.NORTH
        else:
            self.robot.direction = self.robot_updated_direction

        self.gui.display_widgets.arena.update_robot_position_on_map()

    def start_gui(self) -> None:
        self.gui.title(f'{GUI_TITLE} FASTEST PATH Run')
        self.gui.resizable(False, False)
        self.gui.mainloop()


def main(task_type: str) -> None:
    if task_type == 'fp':
        app = FastestPathRun()

    elif task_type == 'exp':
        app = ExplorationRun()

    else:
        raise ValueError('Invalid type')

    Thread(target=app.start_service, daemon=True).start()
    app.start_gui()


if __name__ == '__main__':
    arguments = get_parser()

    main(arguments.task_type)
