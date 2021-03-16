"""
Contain class for image recognition service
"""
import socket
import struct
from threading import Thread

import cv2
import time

from image_recognition import ImageRecogniser
from utils.constants import DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES
from utils.logger import print_img_rec_error_log, print_img_rec_general_log, print_img_rec_exception_log

_DEFAULT_IMAGE_PATH = './image_recognition/Picture.jpg'
_CLASSES_TEXT_PATH = './image_recognition/classes.txt'
_MODEL_WEIGHTS_PATH = './image_recognition/model_weights.pth'


class ImageRecognitionService:
    """
    Client class for managing image recognition-related communication
    """
    HOST = '192.168.6.6'
    PORT = 8082

    ANDROID_HEADER = 'a'
    ALGORITHM_HEADER = ''  # TODO: Insert the header from RPI

    def __init__(self):
        self.rpi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.image_recogniser = ImageRecogniser(_CLASSES_TEXT_PATH, _MODEL_WEIGHTS_PATH)
        self.image = None

    def connect_to_rpi(self, host: str = HOST, port: int = PORT):
        """
        Connects to the RPI module with TCP/IP socket
        """
        try:
            print_img_rec_general_log(f'Connecting to RPI Server via {host}:{port}...')

            self.rpi_server.connect((host, port))
            self.is_connected = True

            print_img_rec_general_log(f'Connected to RPI Server via {host}:{port}...')
        except Exception as e:
            print_img_rec_error_log('Unable to connect to RPI')
            print_img_rec_exception_log(e)

    def disconnect_from_rpi(self):
        """
        Closes the RPI server
        :return: None
        """
        try:
            self.rpi_server.close()
            self.is_connected = False
            print_img_rec_general_log('Disconnected from RPI successfully...')
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
            image_received = self.receive_image()

            if image_received:
                Thread(target=self.image_recognition, daemon=True).start()

    def display_image(self):
        """
        Displays found images in a CV2 window
        @return: None
        """
        while True:
            if self.image is None:
                time.sleep(5)
                continue

            cv2.imshow("", self.image)
            k = cv2.waitKey(1)
            if k == 27:
                break

        cv2.destroyAllWindows()

    def receive_image(self,
                      image_path: str = _DEFAULT_IMAGE_PATH,
                      buffer_size: int = DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES) -> bool:
        """
        Get images from the second RPI server

        :param image_path: Path to store image
        :param buffer_size: Buffer size to receive
        :return: True if image received, False otherwise
        """
        image_received = False
        len_bytes = self.rpi_server.recv(4)

        if len_bytes:
            image_len = struct.unpack(">I", len_bytes)[0]
            image_bytes = b''
            while len(image_bytes) < image_len:
                image_received = True
                try:
                    print_img_rec_general_log('Receiving')
                    image_bytes += self.rpi_server.recv(min(buffer_size, image_len - len(image_bytes)))
                except Exception as e:
                    print_img_rec_error_log('Unable to receive the image from RPI')
                    print_img_rec_exception_log(e)
                    image_received = False
                    break
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
        return image_received

    def image_recognition(self, img_path: str = _DEFAULT_IMAGE_PATH):
        """
        Decodes the base64 image recognition string and runs the object detection on it
        Multi-threaded due to low prediction speed

        :param img_path: The path to the image to read
        """
        print_img_rec_general_log('Starting image recognition.')

        image = cv2.imread(img_path)

        image_string, new_image = self.image_recogniser.cv2_predict(image)

        print_img_rec_general_log('Image recognition finished.')

        if image_string is None:
            print('No symbol detected.')
            return

        if self.image is None:
            self.image = new_image
        else:
            self.image = cv2.hconcat([new_image, self.image])

        cv2.imshow('Prediction', self.image)
        cv2.waitKey(1)

        print_img_rec_general_log(f'Sending image location: {image_string}.')
        # TODO: Settle image header format with algo
        self.send_message_with_header_type(ImageRecognitionService.ANDROID_HEADER, image_string)

        print_img_rec_general_log('Symbol location sent.')


if __name__ == '__main__':
    image_recognition_service = ImageRecognitionService()

    image_recognition_service.connect_to_rpi()
    Thread(target=image_recognition_service.check_for_image, daemon=True).start()
    image_recognition_service.display_image()

