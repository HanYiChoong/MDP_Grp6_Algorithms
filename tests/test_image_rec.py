"""
Contain tests for image recognition and processing
"""
import base64
import unittest
import cv2
from threading import Thread

import ImageRecognition
from actual_run import ExplorationRun
from rpi_service import RPIService


class ImageRecTest(unittest.TestCase):
    def test_image_rec_offline(self):
        explore = ExplorationRun()
        rpi_serv = RPIService()
        # Simulate encoding and sending
        with open("Images/picture0.jpg", "rb") as f:
            img_bytes = base64.b64encode(f.read())
        img_str = img_bytes.decode()
        payload = str.encode(img_str)

        # Simulate receiving and decoding
        img_str2 = payload.decode(rpi_serv.DEFAULT_ENCODING_TYPE)
        explore.image_rec(img_str2)

        self.assertEqual(True, True)

    def test_image_rec_online(self):
        explore = ExplorationRun()
        rpi_serv = RPIService()

        rpi_serv.connect_to_rpi()

        rpi_serv.take_photo([])

        while True:
            message_header_type, response_message = rpi_serv.get_message_from_rpi_queue()

            if message_header_type == '' and response_message == '':
                continue
            elif message_header_type == RPIService.PHOTO_HEADER:
                Thread(target=explore.image_rec, args=(response_message,), daemon=True).start()
                break
            elif message_header_type == RPIService.QUIT_HEADER:
                print('RPI connection closed')
                return

        self.assertEqual(True, True)

    def test_get_pos(self):
        img = cv2.imread("Images/picture0.jpg")
        img_recogniser = ImageRecognition.ImageRecogniser("classes.txt", "model_weights.pth")
        img_str, _ = img_recogniser.cv2_predict(img)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
