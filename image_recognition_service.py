import socket
from threading import Thread

import cv2

from image_recognition import ImageRecogniser
from utils.logger import print_general_log, print_exception_log, print_error_log

_DEFAULT_IMAGE_PATH = 'Picture.jpg'
_CLASSES_TEXT_PATH = './image_recognition/classes.txt'
_MODEL_WEIGHTS_PATH = './image_recognition/model_weights.pth'
_DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES = 2048


class ImageRecognitionService:
    HOST = '192.168.6.6'
    PORT = 8082

    ALGORITHM_HEADER = 'a'

    def __init__(self):
        self.rpi_server = None
        self.is_connected = False
        self.image_recogniser = ImageRecogniser(_CLASSES_TEXT_PATH, _MODEL_WEIGHTS_PATH)
        self.image = None

    def connect_to_rpi(self):
        """
        Connects to the RPI module with TCP/IP socket connection
        """
        try:
            self.rpi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print_general_log('Connecting to RPI Server via '
                              f'{ImageRecognitionService.HOST}:{ImageRecognitionService.PORT}...')

            self.rpi_server.connect((ImageRecognitionService.HOST, ImageRecognitionService.PORT))
            self.is_connected = True

            print_general_log('Connected to RPI Server via '
                              f'{ImageRecognitionService.HOST}:{ImageRecognitionService.PORT}...')
        except Exception as e:
            print_error_log('Unable to connect to RPI service')
            print_exception_log(e)

    def disconnect_from_rpi(self):
        try:
            self.rpi_server.close()
            self.is_connected = False
            print_general_log('Disconnected from RPI service successfully...')
        except Exception as e:
            print_error_log('Unable to close connection to rpi service')
            print_exception_log(e)

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
            print_exception_log(e)

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

            if not image_received:
                continue

            Thread(target=self.image_recognition, daemon=True).start()

    def receive_image(self,
                      image_path: str = _DEFAULT_IMAGE_PATH,
                      buffer_size: int = _DEFAULT_SOCKET_BUFFER_SIZE_IN_BYTES) -> bool:
        """
        Get images from the second RPI server

        :param image_path: Path to store image
        :param buffer_size: Buffer size to receive
        :return: True if image received, False otherwise
        """
        image_received = False

        image_file = open(image_path, "wb")
        image_bytes = self.rpi_server.recv(buffer_size)

        while image_bytes:
            image_received = True

            print_general_log('Receiving image from RPI')

            try:
                print_general_log('Receiving')
                image_file.write(image_bytes)
                image_bytes = self.rpi_server.recv(buffer_size)
            except Exception as e:
                print_error_log('Unable to receive the image from RPI')
                print_exception_log(e)

                image_received = False

                break
        image_file.close()

        return image_received

    def image_recognition(self, img_path: str = _DEFAULT_IMAGE_PATH):
        """
        Decodes the base64 image recognition string and runs the object detection on it
        Multi-threaded due to low prediction speed

        :param img_path: The path to the image to read
        """
        print('Starting image recognition.')

        image = cv2.imread(img_path)

        image_string, new_image = self.image_recogniser.cv2_predict(image)

        print('Image recognition finished.')

        if image_string is None:
            print('No symbol detected.')
            return

        if self.image is None:
            self.image = new_image
        else:
            self.image = cv2.hconcat(self.image, new_image)

        cv2.imshow('Prediction', self.image)
        cv2.waitKey(1)

        print(f'Sending image location: {image_string}.')
        # TODO: Settle image header format with algo
        self.rpi_server.send_message_with_header_type(ImageRecognitionService.ALGORITHM_HEADER, image_string)

        print('Symbol location sent.')


if __name__ == '__main__':
    # Initialise the service
    image_recognition_service = ImageRecognitionService()

    image_recognition_service.connect_to_rpi()
    image_recognition_service.check_for_image()
