"""
Contain classes for robot's physical run
"""
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
from utils.enums import Direction, Movement, RobotMode
from utils.logger import print_error_log, print_general_log
from utils.message_conversion import validate_and_decode_point

_DEFAULT_TIME_LIMIT_IN_SECONDS = 360
_ARENA_FILENAME = 'exam'
_WAYPOINT_REGEX_PATTERN = r'\d+\s\d+'
_SLEEP_DELAY = 0.02


def _convert_to_android_coordinate_format(point_int: List[int]) -> List[str]:
    algo_x, algo_y = point_int

    x = algo_y
    y = 19 - algo_x

    return [str(x), str(y)]


def _convert_to_image_rec_coordinate_format(point_int: List[int]) -> List[int]:
    algo_x, algo_y = point_int

    x = algo_y
    y = 19 - algo_x

    return [x, y]


def _decode_android_coordinate_format(point_string: List[str]) -> List[int]:
    android_x, android_y = list(map(int, point_string))

    x = 19 - android_y
    y = android_x

    return [x, y]


class ExplorationRun:
    """
    Class for exploration tasks, including image recognition
    """

    def __init__(self):
        self.rpi_service = RPIService(self.stop_exploration)
        self.robot = RealRobot(ROBOT_START_POINT,
                               Direction.EAST,
                               on_move=self.on_move,
                               get_sensor_values=self.rpi_service.receive_sensor_values)
        self.exploration = None
        self.robot_updated_point = None
        self.robot_updated_direction = None
        self.exploration_arena = None
        self.obstacle_arena = None

        self.gui = RealTimeGUI()
        self.gui.display_widgets.arena.robot = self.robot
        self.image = None

    def on_move(self, movement: 'Movement') -> List[int]:
        """
        Callback when robot moves
        """
        sleep(0.5)
        sensor_values = self.rpi_service.send_movement_to_rpi_and_get_sensor_values(movement)

        self.gui.display_widgets.arena.update_robot_position_on_map()

        self.send_mdf_string_to_android()

        return sensor_values

    def send_mdf_string_to_android(self):
        p1, p2 = self.gui.display_widgets.arena.map_reference.generate_map_descriptor(self.exploration_arena,
                                                                                      self.obstacle_arena)

        payload = f'{RPIService.ANDROID_MDF_STRING_HEADER} {p1} {p2}'
        self.rpi_service.send_message_with_header_type(RPIService.ANDROID_HEADER, payload)

    def start_service(self) -> None:
        """
        Starts the run by connecting to the rpi
        """
        self.rpi_service.connect_to_rpi()

        Thread(target=self.interpret_rpi_messages, daemon=True).start()

        self.rpi_service.always_listen_for_instructions()

    def interpret_rpi_messages(self) -> None:
        """
        Gets header from rpi message and executes associated function
        """
        while True:
            message_header_type, response_message = self.rpi_service.get_message_from_rpi_queue()

            if message_header_type == '' and response_message == '':
                continue
            elif message_header_type == RPIService.EXPLORATION_HEADER:
                self.start_exploration_search()
                continue
            elif message_header_type == RPIService.NEW_ROBOT_POSITION_HEADER:
                self.decode_and_set_robot_position(response_message)
                continue
            elif message_header_type == RPIService.IMAGE_REC_HEADER:
                self.start_image_recognition_search()
                continue
            # elif message_header_type == RPIService.ANDROID_QUIT_HEADER:
            #     self.stop_exploration()
            #     return

            print_error_log('Invalid command received from RPI')

    # def stop_exploration(self):
    #     print_general_log('Quit command received. Handling termination now')

    def decode_and_set_robot_position(self, message: str) -> None:
        """
        Validate waypoint if valid format and within arena range and not obstacle
        Cache start_point
        Update gui via set_robot_starting_position method
        """
        start_point_string = validate_and_decode_point(message)

        if start_point_string is None:
            return

        start_point = _decode_android_coordinate_format(start_point_string)

        x, y = start_point

        if not is_within_arena_range(x, y):
            print_error_log('Start point is not within the arena range!')
            return

        self.robot_updated_point = start_point
        self.reset_robot_to_initial_state()

    def start_exploration_search(self) -> None:
        """
        Runs the exploration search loop
        """
        self._setup_exploration()

        exploration = Exploration(self.robot,
                                  self.exploration_arena,
                                  self.obstacle_arena,
                                  on_update_map=self.mark_sensed_area_as_explored,
                                  on_calibrate=self.calibrate_robot,
                                  time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        exploration.start_exploration()
        print_general_log('Done with exploration')
        self.send_mdf_string_to_android()

    def _setup_exploration(self):
        self.gui.display_widgets.arena.map_reference.reset_exploration_maps()  # Get a fresh copy of map first

        self.exploration_arena = self.gui.display_widgets.arena.map_reference.explored_map
        self.obstacle_arena = self.gui.display_widgets.arena.map_reference.obstacle_map

        self.gui.display_widgets.arena.set_unexplored_arena_map()
        self.reset_robot_to_initial_state()

    def mark_sensed_area_as_explored(self, point: List[int]):
        """
        Updates the gui during exploration
        """
        self.gui.display_widgets.arena.mark_sensed_area_as_explored_on_map(point)

    def start_image_recognition_search(self):
        """
        Runs the exploration search loop with image taking capabilities
        """
        self._setup_exploration()

        image_recognition_exploration = ImageRecognitionExploration(self.robot,
                                                                    self.exploration_arena,
                                                                    self.obstacle_arena,
                                                                    on_update_map=self.mark_sensed_area_as_explored,
                                                                    on_calibrate=self.calibrate_robot,
                                                                    on_take_photo=self.on_take_photo,
                                                                    time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        image_recognition_exploration.start_exploration()
        print_general_log("Image Exploration completed")

    def on_take_photo(self, robot_point, obstacles):
        """
        Callback when robot takes a photo
        """
        sleep(0.3)

        # find nearest obstacle point from the robot point
        closest_euclidean_distance = 9999999
        closest_obstacle_point_index = 0

        for i, obstacle_point in enumerate(obstacles):
            robot_row, robot_column = robot_point
            obstacle_row, obstacle_column = obstacle_point

            squared_magnitude = (robot_row - obstacle_row) ** 2 + (robot_column - obstacle_column) ** 2

            if squared_magnitude < closest_euclidean_distance:
                closest_euclidean_distance = squared_magnitude
                closest_obstacle_point_index = i

        closest_obstacle_point = obstacles[closest_obstacle_point_index]
        converted_point = _convert_to_image_rec_coordinate_format(closest_obstacle_point)

        self.rpi_service.take_photo(converted_point)

    def reset_robot_to_initial_state(self):
        """
        Resets the robot's path
        """
        if self.robot_updated_point is None:
            self.robot.point = ROBOT_START_POINT
        else:
            self.robot.point = self.robot_updated_point

        if self.robot_updated_direction is None:
            self.robot.direction = Direction.EAST
        else:
            self.robot.direction = self.robot_updated_direction

    def calibrate_robot(self):
        # self.rpi_service.send_movement_to_rpi_and_get_sensor_values(Movement.RIGHT)
        # sleep(0.5)
        self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER,
                                                       RPIService.CALIBRATE_ROBOT_RIGHT_WALL_MORE_ACC_HEADER)
        # sleep(0.5)
        # self.rpi_service.send_movement_to_rpi_and_get_sensor_values(Movement.LEFT)

    def stop_exploration(self):
        """
        Updates exploration as stopped
        """
        print_general_log('Stopping exploration now...')

        if self.exploration is not None:
            self.exploration.is_running = False

        # self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER, RPIService.ARDUINO_QUIT_HEADER)

    def change_robot_mode(self, robot_mode: 'RobotMode'):
        sleep(0.1)

        if robot_mode == RobotMode.EXPLORATION:
            self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER,
                                                           RPIService.ARDUINO_FASTEST_PATH_INDICATOR)

            return

        self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER,
                                                       RPIService.ARDUINO_EXPLORATION_INDICATOR)

    def start_gui(self) -> None:
        """
        Starts GUI for exploration
        """
        self.gui.title('{GUI_TITLE} EXPLORATION Run'.format(GUI_TITLE=GUI_TITLE))
        self.gui.resizable(False, False)
        self.gui.mainloop()


class FastestPathRun:
    """
    Class for fastest path task
    """

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
        self.canvas_repaint_delay_ms = 750

        self.p1_descriptor = None
        self.p2_descriptor = None
        self.map = self.load_map_from_disk()

    def load_map_from_disk(self) -> List[int]:
        """
        Loads the map string from _ARENA_FILENAME
        """
        generated_arena, p1_descriptor, p2_descriptor = self.gui.display_widgets.arena.load_map_from_disk(
            _ARENA_FILENAME)
        Map.set_virtual_walls_on_map(generated_arena)

        self.p1_descriptor = p1_descriptor
        self.p2_descriptor = p2_descriptor

        return generated_arena

    def start_service(self) -> None:
        """
        Starts the rpi server
        """
        self.rpi_service.connect_to_rpi()

        Thread(target=self.interpret_rpi_messages, daemon=True).start()
        Thread(target=self.send_mdf_string_to_android, daemon=True).start()

        self.rpi_service.always_listen_for_instructions()

    def interpret_rpi_messages(self) -> None:
        """
        Gets header from rpi messages and executes associated function
        """
        while True:
            message_header_type, response_message = self.rpi_service.get_message_from_rpi_queue()

            if message_header_type == '' and response_message == '':
                continue
            elif message_header_type == RPIService.WAYPOINT_HEADER:
                self.decode_and_save_waypoint(response_message)
                continue
            elif message_header_type == RPIService.NEW_ROBOT_POSITION_HEADER:
                self.decode_and_set_robot_position(response_message)
                continue
            elif message_header_type == RPIService.ANDROID_FASTEST_PATH_HEADER:
                self.start_fastest_path_run()
                continue
            elif message_header_type == RPIService.ANDROID_QUIT_HEADER:
                # TODO: Perform cleanup and close gui or smt idk
                print_error_log('RPI connection closed')
                return

            print_error_log('Invalid command received from RPI')

    def send_mdf_string_to_android(self):
        """
        Sends the mdf string to the android via rpi
        """
        payload = f'{RPIService.ANDROID_MDF_STRING_HEADER} {self.p1_descriptor} {self.p2_descriptor}'
        self.rpi_service.send_message_with_header_type(RPIService.ANDROID_HEADER, payload)

    def decode_and_save_waypoint(self, message: str):
        """
        Validate waypoint if valid format and within arena range and not obstacle
        Cache waypoint
        Display in the arena via arena.set_way_point method
        """
        waypoint_string = validate_and_decode_point(message)

        if waypoint_string is None:
            return

        waypoint = _decode_android_coordinate_format(waypoint_string)

        y, x = waypoint

        if not is_within_arena_range(y, x) or Map.point_is_not_free_area(self.map, waypoint):
            print_error_log('Waypoint is not within arena range, cannot be an obstacle or virtual wall!')
            return

        if self.waypoint is not None:  # clear old waypoint
            self.gui.display_widgets.arena.remove_way_point_on_canvas(self.waypoint)

        self.waypoint = waypoint

        self.gui.display_widgets.arena.set_way_point_on_canvas(waypoint)

    def decode_and_set_robot_position(self, message: str):
        """
        Validate waypoint if valid format and within arena range and not obstacle
        Cache start_point
        Update gui via set_robot_starting_position method
        """
        start_point_string = validate_and_decode_point(message)

        if start_point_string is None:
            return

        start_point = _decode_android_coordinate_format(start_point_string)

        y, x = start_point

        if not is_within_arena_range(y, x) or Map.point_is_not_free_area(self.map, start_point):
            print_error_log('Start point is not within the arena range, cannot be an obstacle or virtual wall!')
            return

        self.robot_updated_point = start_point
        self.reset_robot_to_initial_state()

    def start_fastest_path_run(self):
        """
        Runs the fastest path algorithm
        """
        if self.waypoint is None:
            self.gui.display_widgets.log_area.insert_log_message('Waypoint not set!')
            return

        self.reset_robot_to_initial_state()

        solver = AStarAlgorithm(self.map)

        self.gui.display_widgets.log_area.insert_log_message('Finding the fastest path…')
        path = solver.run_algorithm(self.robot.point,
                                    self.waypoint,
                                    ROBOT_END_POINT,
                                    self.robot.direction)

        if not path:
            self.gui.display_widgets.log_area.insert_log_message('No fastest path route found…')
            return

        movements = solver.convert_fastest_path_to_movements(path, self.robot.direction)
        arduino_format_movements = solver.consolidate_movements_to_string(movements)

        self.send_movements_to_rpi(arduino_format_movements)
        self.display_result_in_gui(path)

    def send_movements_to_rpi(self, movements: str):
        """
        Send the fastest path to rpi
        """
        self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER,
                                                       RPIService.ARDUINO_FASTEST_PATH_INDICATOR)
        sleep(_SLEEP_DELAY)

        movement_instructions_list = AStarAlgorithm.check_and_separate_long_instructions(movements)
        print(movement_instructions_list)
        for instruction_batch in movement_instructions_list:
            self.rpi_service.send_message_with_header_type(RPIService.ARDUINO_HEADER, instruction_batch)
            sleep(7)

    def display_result_in_gui(self, path: list):
        """
        Updates the GUI with the path
        """
        if len(path) <= 0:
            return

        action = path.pop(0)
        self.gui.display_widgets.arena.update_robot_point_on_map_with_node(action)

        self.gui.display_widgets.arena.after(self.canvas_repaint_delay_ms, self.display_result_in_gui, path)

    def reset_robot_to_initial_state(self):
        """
        Resets robot path
        """
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
        """
        Starts GUI for fastest path
        """
        self.gui.title(f'{GUI_TITLE} FASTEST PATH Run')
        self.gui.resizable(False, False)
        self.gui.mainloop()


def main(task_type: str) -> None:
    """
    Main run function
    """
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
