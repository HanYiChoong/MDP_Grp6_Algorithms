from threading import Thread

from algorithms.exploration import Exploration
from algorithms.fastest_path_solver import AStarAlgorithm
from gui import GUI
from map import Map
from robot import RealRobot
from rpi_service import RPIService
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT
from utils.enums import Direction, Movement
from utils.logger import print_error_log

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
        self.arena = Map()
        self.gui = GUI(is_simulation=False)

    def on_move(self, movement: 'Movement'):
        sensor_values = self.rpi_service.send_movement_to_rpi_and_get_sensor_values(movement, self.robot)
        return sensor_values

    def start_run(self) -> None:
        self.rpi_service.connect_to_rpi()
        self.rpi_service.ping()

        Thread(target=self.interpret_rpi_messages).start()

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

            print_error_log('Invalid command received from RPI')

    def start_exploration_search(self) -> None:
        self.arena.reset_exploration_maps()  # Get a fresh copy of map first

        exploration_arena = self.arena.explored_map
        obstacle_arena = self.arena.obstacle_map
        self.gui.display_widgets.arena.set_unexplored_arena_map()

        self.reset_robot_to_initial_state()

        exploration = Exploration(self.robot,
                                  exploration_arena,
                                  obstacle_arena,
                                  time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        exploration.start_exploration()
        self.arena.generate_map_descriptor(exploration_arena, obstacle_arena)
        # TODO: Figure out what to do here after exploration lmao

    def decode_and_save_way_point(self, message: str) -> None:
        # store way point then update in gui as well
        raise NotImplementedError

    def decode_and_set_robot_position(self, message: str) -> None:
        # set robot position then set in gui as well
        raise NotImplementedError

    def start_fastest_path_search(self):
        # TODO: Check if way point exists

        p1_string, p2_string = self.arena.load_map_from_disk(get_arena_file_directory())
        decoded_arena = self.arena.decode_map_descriptor_for_fastest_path_task(p1_string, p2_string)
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


if __name__ == '__main__':
    pass
