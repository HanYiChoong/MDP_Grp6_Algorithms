from threading import Thread
from typing import List

from algorithms.exploration import Exploration
from algorithms.fastest_path_solver import AStarAlgorithm
from configs.gui_config import GUI_TITLE
from gui import RealTimeGUI
from map import Map
from robot import RealRobot
from rpi_service import RPIService
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT
from utils.enums import Direction, Movement
from utils.logger import print_error_log

_GUI_REDRAW_INTERVAL = 0.0001
_DEFAULT_TIME_LIMIT_IN_SECONDS = 360
_ARENA_FILENAME = 'sample_arena_1'


def get_arena_file_directory():
    return f'./maps/{_ARENA_FILENAME}.txt'


class ActualRun:
    def __init__(self):
        self.rpi_service = RPIService()
        self.robot = RealRobot(ROBOT_START_POINT,
                               Direction.EAST,
                               self.on_move,
                               self.rpi_service.receive_sensor_values)
        self.exploration = None
        self.fastest_path = None
        self.robot_updated_point = None
        self.robot_updated_direction = None
        self.way_point = None
        self.map_reference = Map()
        self.gui = RealTimeGUI()

        self.gui.display_widgets.arena.robot = self.robot

    def on_move(self, movement: 'Movement'):
        sensor_values = self.rpi_service.send_movement_to_rpi_and_get_sensor_values(movement, self.robot)

        self.gui.display_widgets.arena.update_robot_position_on_map()

        return sensor_values

    def start_run(self) -> None:
        self.rpi_service.connect_to_rpi()
        self.rpi_service.ping()

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

            if message_header_type == RPIService.WAYPOINT_HEADER:
                self.decode_and_save_way_point(response_message)
                continue

            if message_header_type == RPIService.NEW_ROBOT_POSITION_HEADER:
                self.decode_and_set_robot_position(response_message)
                continue

            if message_header_type == RPIService.FASTEST_PATH_HEADER:
                self.start_fastest_path_search()
                continue

            if message_header_type == RPIService.IMAGE_REC_HEADER:
                self.start_image_recognition_search()
                continue

            if message_header_type == RPIService.QUIT_HEADER:
                # TODO: Perform cleanup and close gui or smt idk
                print_error_log('RPI connection closed')
                return

            print_error_log('Invalid command received from RPI')

    def start_exploration_search(self) -> None:
        self.map_reference.reset_exploration_maps()  # Get a fresh copy of map first

        exploration_arena = self.map_reference.explored_map
        obstacle_arena = self.map_reference.obstacle_map
        self.gui.display_widgets.arena.set_unexplored_arena_map()

        self.reset_robot_to_initial_state()

        exploration = Exploration(self.robot,
                                  exploration_arena,
                                  obstacle_arena,
                                  time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        exploration.start_exploration()
        self.map_reference.generate_map_descriptor(exploration_arena, obstacle_arena)
        # TODO: Figure out what to do here after exploration lmao

    def decode_and_save_way_point(self, message: str) -> None:
        # store way point then update in gui as well
        raise NotImplementedError

    def decode_and_set_robot_position(self, message: str) -> None:
        # set robot position then set in gui as well
        raise NotImplementedError

    def start_fastest_path_search(self):
        if self.way_point is None:
            self.gui.display_widgets.insert_log_message('Waypoint not set!')
            return

        p1_string, p2_string = self.map_reference.load_map_from_disk(get_arena_file_directory())
        decoded_arena = self.map_reference.decode_map_descriptor_for_fastest_path_task(p1_string, p2_string)
        Map.set_virtual_walls_on_map(decoded_arena)

        self.gui.display_widgets.arena.generate_arena_on_canvas(decoded_arena)
        solver = AStarAlgorithm(decoded_arena)
        self.reset_robot_to_initial_state()

        path = solver.run_algorithm(self.robot.point,
                                    self.way_point,
                                    ROBOT_END_POINT,
                                    self.robot.direction)

        if not path:
            print_error_log('No fastest path found at all')
            return

        movements = solver.convert_fastest_path_to_movements(path, self.robot.direction)
        # TODO: Reference arduino code and change the separator. Change to send one movement at a time in movement class
        # movements_in_string = solver.convert_fastest_path_movements_to_string(movements)

        for movement in movements:
            # TODO: move robot in gui as well
            self.rpi_service.send_message_with_header_type(RPIService.FASTEST_PATH_HEADER, Movement.to_string(movement))
            self.robot.move(movement, invoke_callback=False)

    def start_image_recognition_search(self):
        raise NotImplementedError

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
        self.gui.title(GUI_TITLE)
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
        self.canvas_repaint_delay_ms = 100
        self.map = self.load_map_from_disk()

    def load_map_from_disk(self) -> List[int]:
        generated_arena = self.gui.display_widgets.arena.load_map_from_disk(_ARENA_FILENAME)
        Map.set_virtual_walls_on_map(generated_arena)

        return generated_arena

    def start_service(self) -> None:
        self.rpi_service.connect_to_rpi()
        self.rpi_service.ping()

        Thread(target=self.interpret_rpi_messages, daemon=True).start()

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

            if message_header_type == RPIService.FASTEST_PATH_HEADER:
                self.start_fastest_path_run()
                continue

            if message_header_type == RPIService.QUIT_HEADER:
                # TODO: Perform cleanup and close gui or smt idk
                print_error_log('RPI connection closed')
                return

            print_error_log('Invalid command received from RPI')

    def decode_and_save_waypoint(self, message: str):
        # validate waypoint if valid format and within arena range and not obstacle
        # cache waypoint
        # display in arena via arena.set_way_point method
        raise NotImplementedError

    def decode_and_set_robot_position(self, message: str):
        # validate waypoint if valid format and within arena range and not obstacle
        # cache start_point
        # update gui via set_robot_starting_position method
        raise NotImplementedError

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

        Thread(target=self.send_movements_to_rpi, args=(movements,), daemon=True).start()

    def send_movements_to_rpi(self, movements: List[str]):
        for movement in movements:
            # TODO: Discuss about the type of header to send
            self.rpi_service.send_message_with_header_type(RPIService.FASTEST_PATH_HEADER, movement)

    def display_result_in_gui(self, path: list):
        if len(path) <= 0:
            return

        action = path.pop(0)
        self.gui.display_widgets.arena.update_cell_on_map(action)

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

    def start_gui(self) -> None:
        self.gui.title(GUI_TITLE)
        self.gui.resizable(False, False)
        self.gui.mainloop()


if __name__ == '__main__':
    app = ActualRun()
    app.start_gui()
