"""
Contain classes for RPI server connection
"""
import socket
from collections import deque
from time import sleep
from typing import Callable, List, Tuple, Union

from utils.enums import Movement
from utils.logger import print_error_log, print_general_log, print_exception_log
from utils.message_conversion import validate_and_convert_sensor_values_from_arduino

_THREAD_SLEEP_DURATION_IN_SECONDS = 0.1
_DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES = 2048


class RPIService:
    """
    Main class to handle all RPI connections
    """
    HOST = '192.168.6.6'
    PORT = 8081

    # Message types
    TAKE_PHOTO_HEADER = 'p'
    PHOTO_HEADER = 'p'
    DEFAULT_ENCODING_TYPE = 'utf-8'
    ARDUINO_HEADER = 'h'
    ANDROID_HEADER = 'a'
    MESSAGE_SEPARATOR = '$'

    ANDROID_MDF_STRING_HEADER = 'MDF'

    WAYPOINT_HEADER = 'WP'
    NEW_ROBOT_POSITION_HEADER = 'START'
    ANDROID_FASTEST_PATH_HEADER = 'FP'
    ARDUINO_FASTEST_PATH_INDICATOR = 'F|'

    EXPLORATION_HEADER = 'EXP'
    IMAGE_REC_HEADER = 'IR'
    MOVE_ROBOT_HEADER = ''  # Check with arduino
    SENSOR_READING_SEND_HEADER = 'P|'  # Check with arduino
    SENSOR_READING_RECEIVING_HEADER = 'P'  # Check with arduino
    QUIT_HEADER = 'QQQQQQ'  # ??

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
            self.rpi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print_general_log('Connecting to RPI Server via {}:{}…'.format(RPIService.HOST, RPIService.PORT))

            self.rpi_server.connect((RPIService.HOST, RPIService.PORT))
            self.is_connected = True

            print_general_log('Connecting to RPI Server via {}:{}…'.format(RPIService.HOST, RPIService.PORT))
        except Exception as e:
            print_error_log('Unable to connect to RPI')
            print_exception_log(e)

    def disconnect_rpi(self):
        """
        Closes the RPI server
        """
        try:
            self.rpi_server.close()
            self.is_connected = False
            print_general_log('Disconnected from RPI successfully…')
        except Exception as e:
            print_error_log('Unable to close connection to RPI\n')
            print(e)

    def _send_message(self, payload: str) -> None:
        """
        Sends the payload to the RPI

        :param payload: Message to send
        """
        try:
            self.rpi_server.sendall(str.encode(payload))
            print_general_log('Message sent successfully! — {}'.format(payload))
        except Exception as e:
            print_error_log('Unable to send a message to RPI')
            print_exception_log(e)

    def _receive_message(self, buffer_size: int = _DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES) -> str:
        """
        Receives the response from the RPI

        :param buffer_size: The max amount of data in bytes to receive
        :return: The response message from the RPI
        """
        try:
            print_general_log('Receiving message from RPI')

            request_message = self.rpi_server.recv(buffer_size).decode(self.DEFAULT_ENCODING_TYPE)
            print_general_log('Message received: {}'.format(request_message))

            return request_message
        except Exception as e:
            print_error_log('Unable to receive a message from RPI')
            print_exception_log(e)

    def send_message_with_header_type(self, header_type: str, payload: str = None):
        """
        Concatenate the payload to header type and sends the message to the RPI

        :param header_type: Accepted headers established in the RPI class for RPI communication
        :param payload: Message to send to the RPI
        """
        full_payload = header_type

        if payload is not None:
            full_payload += payload

        self._send_message(full_payload)

    def get_message_from_rpi_queue(self) -> Tuple[str, str]:
        """
        Gets the first message from the FIFO queue of instructions. \n
        If queue empty, put the thread to sleep for a while and check again.
        """
        if len(self._fifo_queue) < 1:
            sleep(_THREAD_SLEEP_DURATION_IN_SECONDS)
            return '', ''

        request_message = self._fifo_queue.popleft()

        if request_message is None:
            return '', ''

        request_message = request_message.split(RPIService.MESSAGE_SEPARATOR)

        if len(request_message) > 1:
            header_type, message = request_message[0], request_message[1]

        else:
            header_type, message = request_message[0], ''

        if header_type == RPIService.QUIT_HEADER:
            # TODO: Temporary measure
            self.disconnect_rpi()
            self.on_quit()

            return '', ''

        return header_type, message

    def send_movement_to_rpi_and_get_sensor_values(self, movement: 'Movement') -> List[Union[None, int]]:
        """
        Sends the movement from exploration computation, the robot's position and direction to the RPI

        :param movement: The movement determined by the exploration algorithm
        """
        print_general_log('Sending movement {} to RPI…'.format(movement.name))
        print(movement)
        payload = Movement.to_string(movement) + '1|'  # Append 1 to move to the direction by one
        print(payload)
        self.send_message_with_header_type(RPIService.ARDUINO_HEADER, payload)

        return self.receive_sensor_values()

    def receive_sensor_values(self, start_sensing: bool = True) -> List[Union[None, int]]:
        """
        Processes the sensor values from the RPI queue. \n
        If the header does not match read sensor, it continues to get a message from the RPI queue. \n

        :param start_sensing:
        :return: List of neighbouring points from the robot that it can explore or contains obstacles
        """
        if start_sensing:
            self.send_message_with_header_type(RPIService.ARDUINO_HEADER, RPIService.SENSOR_READING_SEND_HEADER)

        while True:
            message_header_type, message = self.get_message_from_rpi_queue()

            if message_header_type == RPIService.QUIT_HEADER:
                return []

            if message_header_type != RPIService.SENSOR_READING_RECEIVING_HEADER:
                continue

            sensor_values = validate_and_convert_sensor_values_from_arduino(message)

            return sensor_values

    def take_photo(self, obstacles, robot=None) -> None:
        """
        Sends the instruction to the RPI to take photo

        :param obstacles:
        :param robot:
        :return: None
        """
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
