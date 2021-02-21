from threading import Thread

from rpi_service import RPIService
from robot import RealRobot
from map import Map
from algorithms.exploration import Exploration
from algorithms.fastest_path_solver import AStarAlgorithm
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT
from utils.enums import Direction, Movement
from utils.logger import print_error_log

_DEFAULT_TIME_LIMIT_IN_SECONDS = 360
_ARENA_FILENAME = ''


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

    def on_move(self, movement):
        sensor_values = self.rpi_service.send_movement_to_rpi(movement, self.robot)
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
        exploration_arena = self.arena.explored_map[:]
        obstacle_arena = self.arena.obstacle_map[:]
        self.reset_robot_to_initial_state()

        exploration = Exploration(self.robot,
                                  exploration_arena,
                                  obstacle_arena,
                                  time_limit=_DEFAULT_TIME_LIMIT_IN_SECONDS)

        exploration.start_exploration()
        self.arena.generate_map_descriptor(exploration_arena, obstacle_arena)
        # TODO: Figure out what to do here after exploration lmao

    def decode_and_save_way_point(self, message: str) -> None:
        raise NotImplementedError

    def decode_and_set_robot_position(self, message: str) -> None:
        raise NotImplementedError

    def start_fastest_path_search(self):
        p2_string = self.arena.load_map_from_disk(_ARENA_FILENAME)
        decoded_arena = self.arena.decode_map_descriptor_for_fastest_path_task(p2_string)
        self.arena.set_virtual_walls_on_map(decoded_arena)

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

        for movement in movements:
            self.robot.move(movement)

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
