"""
Contain class for image recognition service
"""
import socket
import struct
import time
from threading import Thread

import cv2

from image_recognition import ImageRecogniser
from rpi_service import RPIService
from utils.constants import DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES
from utils.logger import print_img_rec_error_log, print_img_rec_general_log, print_img_rec_exception_log

_DEFAULT_IMAGE_PATH = './image_recognition/Picture.jpg'
_CLASSES_TEXT_PATH = './image_recognition/classes.txt'
_MODEL_WEIGHTS_PATH = './image_recognition/model_weights2.pth'


class ImageRecognitionService:
    """
    Client class for managing image recognition-related communication
    """
    HOST = '192.168.6.6'
    PORT = 8082

    ANDROID_HEADER = 'a'
    ALGORITHM_HEADER = ''

    def __init__(self):
        self.rpi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.image_recogniser = ImageRecogniser(_CLASSES_TEXT_PATH, _MODEL_WEIGHTS_PATH)
        self.image = None
        self.img_count = 0
        self.label_list = list(str)

    def connect_to_rpi(self, host: str = HOST, port: int = PORT):
        """
        Connects to the RPI module with TCP/IP socket
        """
        try:
            print_img_rec_general_log('Connecting to RPI Server via '
                                      '{}:{}...'.format(host, port))

            self.rpi_server.connect((host, port))
            self.is_connected = True

            print_img_rec_general_log('Connected to RPI Server via '
                                      '{}:{}...'.format(host, port))
        except Exception as e:
            print_img_rec_error_log('Unable to connect to RPI')
            print_img_rec_exception_log(e)

    def disconnect_from_rpi(self):
        """
        Closes the RPI server
        @return: None
        """
        try:
            self.rpi_server.close()
            self.is_connected = False
            print_img_rec_general_log('Disconnected from RPI successfully…')
        except Exception as e:
            print_img_rec_error_log('Unable to close connection to rpi')
            print_img_rec_exception_log(e)

    def _send_message(self, payload: str) -> None:
        """
        Sends the payload to the RPI

        :param payload: Message to be sent
        """
        try:
            self.rpi_server.sendall(str.encode(payload))
            print_img_rec_general_log('Message sent successfully!')
        except Exception as e:
            print_img_rec_error_log('Unable to send the message to RPI')
            print_img_rec_exception_log(e)

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

    def check_for_image(self) -> None:
        """
        Checks for images received from the RPI
        """
        while True:
            robot_str = self.receive_image()

            if robot_str != "":
                Thread(target=self.image_recognition, args=(robot_str,), daemon=True).start()

    def display_image(self):
        """
        Displays found images in a CV2 window
        @return: None
        """
        while True:
            if self.image is None:
                time.sleep(5)
                continue
            cv2.imshow("{}".format(int(self.img_count / 5)), self.image)
            k = cv2.waitKey(1)
            if k == 27:
                break

        cv2.destroyAllWindows()

    def receive_image(self,
                      image_path: str = _DEFAULT_IMAGE_PATH,
                      buffer_size: int = DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES) -> str:
        """
        Get images from the second RPI server

        :param image_path: Path to store image
        :param buffer_size: Buffer size to receive
        :return: True if image received, False otherwise
        """
        robot_str = ""
        len_bytes = self.rpi_server.recv(4)
        if len_bytes:
            image_len = struct.unpack(">I", len_bytes)[0]
            image_bytes = b''
            print_img_rec_general_log('Receiving Image')
            while len(image_bytes) < image_len:
                try:
                    image_bytes += self.rpi_server.recv(min(buffer_size, image_len - len(image_bytes)))
                except Exception as e:
                    print_img_rec_error_log('Unable to receive the image from RPI')
                    print_img_rec_exception_log(e)
                    break
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            robot_pos = self.rpi_server.recv(buffer_size)
            robot_str = robot_pos.decode('utf-8')
            print_img_rec_general_log("Received robot position: {}".format(robot_str))
        return robot_str

    def image_recognition(self, robot_str: str, img_path: str = _DEFAULT_IMAGE_PATH):
        """
        Decodes the base64 image recognition string and runs the object detection on it
        Multi-threaded due to low prediction speed

        @param img_path: The path to the image to read
        @param robot_str: The string containing the robot's position and direction
        """
        print_img_rec_general_log('Starting image recognition.')

        label, new_image = self.image_recogniser.cv2_predict(img_path)

        print_img_rec_general_log('Image recognition finished.')

        resize_val = 0.5
        new_image = cv2.resize(new_image, (int(new_image.shape[1] * resize_val), int(new_image.shape[0] * resize_val)))

        if self.image is None:
            self.image = new_image
        else:
            self.image = cv2.hconcat([new_image, self.image])
        self.img_count += 1

        if self.img_count % 5 == 0:
            self.image = None

        if label is None:
            print('No symbol detected.')
            return
        elif label in self.label_list:
            print('Symbol already detected.')
            return

        self.label_list.append(label)

        # IMAGE ID X Y
        x, y = robot_str.split(",")
        label = label.split("_")[0]
        img_str = "IMAGE {} {} {}".format(label, x, y)

        print_img_rec_general_log('Sending image location: {}.'.format(img_str))
        self.send_message_with_header_type(ImageRecognitionService.ANDROID_HEADER, img_str)

        if len(self.label_list) > 5:
            self.send_message_with_header_type(ImageRecognitionService.ALGORITHM_HEADER,
                                               RPIService.ANDROID_QUIT_HEADER + RPIService.MESSAGE_SEPARATOR)

        print_img_rec_general_log('Symbol location sent.')


if __name__ == '__main__':
    image_recognition_service = ImageRecognitionService()

    image_recognition_service.connect_to_rpi()
    Thread(target=image_recognition_service.check_for_image, daemon=True).start()
    image_recognition_service.display_image()
