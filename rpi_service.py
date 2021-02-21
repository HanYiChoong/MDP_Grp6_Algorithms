import socket
from collections import deque
from time import sleep
from typing import Callable, List, Tuple, Union

from utils.enums import Direction, Movement
from utils.logger import print_error_log, print_general_log

_DEFAULT_ENCODING_TYPE = 'utf-8'
_THREAD_SLEEP_DURATION_IN_SECONDS = 0.1
_DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES = 1024


class RPIService:
    HOST = ''
    PORT = ''

    # Message types
    WAYPOINT_HEADER = ''
    NEW_ROBOT_POSITION_HEADER = ''
    FASTEST_PATH_HEADER = ''
    EXPLORATION_HEADER = ''
    IMAGE_REC_HEADER = ''
    TAKE_PHOTO_HEADER = ''
    MESSAGE_SEPARATOR = ''
    MOVE_ROBOT_HEADER = ''
    REQUEST_SENSOR_READING_HEADER = ''
    QUIT_HEADER = ''

    def __init__(self, on_quit: Callable = None):
        self.rpi_server = None
        self.is_connected = False
        self.on_quit = on_quit if on_quit is not None else lambda: None
        self._fifo_queue = deque([])

    def connect_to_rpi(self) -> None:
        """
        Connects to the RPI module with UDP socket connection
        """
        try:
            self.rpi_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rpi_server.connect((RPIService.HOST, RPIService.PORT))
            self.is_connected = True
            print_general_log(f'Connected to RPI service via {RPIService.HOST}:{RPIService.PORT}...')
        except Exception as e:
            print_error_log('Unable to connect to RPI service\n')
            print_error_log(e)

    def disconnect_rpi(self):
        try:
            self.rpi_server.close()
            self.is_connected = False
            print_general_log('Disconnected from RPI service successfully...')
        except Exception as e:
            print_error_log('Unable to close connection to rpi service\n')
            print(e)

    def _send_message(self, payload: str) -> None:
        """
        Sends the payload to the RPI

        :param payload: Message to be sent
        """
        try:
            self.rpi_server.sendall(str.encode(payload))
            print_general_log('Message sent successfully!')
        except Exception as e:
            print_error_log('Unable to send message to RPI service')
            print_error_log(e)

    def _receive_message(self, buffer_size: int = _DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES) -> str:
        """
        Receives the response from the RPI

        :param buffer_size: The max amount of data in bytes to be received at once
        :return: The response message from the RPI
        """
        try:
            print_general_log('Receiving message from RPI service')

            request_message = self.rpi_server.recv(buffer_size).decode(_DEFAULT_ENCODING_TYPE)
            print_general_log(f'Message received: {request_message}')

            return request_message
        except Exception as e:
            print_error_log('Unable to send message to RPI service')
            print_error_log(e)

    def send_message_with_header_type(self, header_type: str, payload: str = None):
        """
        Concatenate the payload to header type and sends the message to the RPI

        :param header_type:  Accepted headers defined in the RPI class for RPI communication
        :param payload: Message to be sent to the RPI
        """
        full_payload = header_type

        if payload is not None:
            full_payload += payload

        self._send_message(full_payload)

    def get_message_from_rpi_queue(self) -> Tuple[str, str]:
        """
        Gets the first message from the FIFO queue of instructions
        """
        if len(self._fifo_queue) < 1:
            sleep(_THREAD_SLEEP_DURATION_IN_SECONDS)
            return '', ''

        request_message = self._fifo_queue.popleft()

        if request_message is None:
            return '', ''

        request_message = request_message.split(RPIService.MESSAGE_SEPARATOR)

        if len(request_message) > 1:
            header_type, message = request_message[0], RPIService.MESSAGE_SEPARATOR.join(request_message[1])

        else:
            header_type, message = request_message[0], ''

        if header_type == RPIService.QUIT_HEADER:
            # TODO: Temporary measure
            print_general_log(self._fifo_queue)
            self.disconnect_rpi()

        return header_type, message

    def ping(self):
        """
        Test connection
        """
        self._send_message('YOYO')

    def send_movement_to_rpi(self, movement: 'Movement', robot) -> List[Union[None, int]]:
        """
        Sends the movement from exploration computation, the robot's position and direction to the RPI

        :param movement: The movement determined by the exploration algorithm
        :param robot: The robot in the exploration arena
        """
        print_general_log(f'Sending movement {movement} to RPI...')

        movement_in_string = Movement.to_string(movement)
        robot_position = robot.point
        robot_direction_in_string = Direction.to_string(robot.direction)

        payload = f'{movement_in_string} {robot_position[0]},{robot_position[1]} {robot_direction_in_string}'

        self.send_message_with_header_type(RPIService.MOVE_ROBOT_HEADER, payload)

        return self.receive_sensor_values(start_sensing=False)

    def receive_sensor_values(self, start_sensing: bool = True) -> List[Union[None, int]]:
        """
        Processes the sensor values from the RPI queue

        :param start_sensing:
        :return: List of neighbouring points from the robot that can be explored or contains obstacles
        """
        if start_sensing:
            self._send_message(RPIService.REQUEST_SENSOR_READING_HEADER)

        while True:
            message_header_type, message = self.get_message_from_rpi_queue()

            if message_header_type == RPIService.QUIT_HEADER:
                return []

            if message_header_type != RPIService.REQUEST_SENSOR_READING_HEADER:
                continue

            # TODO: Handle message from the rpi queue

            return []

    def take_photo(self, obstacles, robot=None) -> None:
        # TODO Understand image rec algo then write this method
        """
        Sends the instruction to the RPI to take photo

        :param obstacles:
        :param robot:
        :return:
        """
        # TODO: Build payload to send to RPI
        payload = ''
        self.send_message_with_header_type(RPIService.TAKE_PHOTO_HEADER, payload)

    def always_listen_for_instructions(self):
        """
        Listens for messages and append them into the FIFO queue
        """
        while self.is_connected:
            request_message = self._receive_message()
            self._fifo_queue.append(request_message)


if __name__ == '__main__':
    rpi = RPIService()
    rpi.connect_to_rpi()
    rpi.ping()
