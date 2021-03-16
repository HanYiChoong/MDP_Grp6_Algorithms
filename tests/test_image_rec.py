"""
Contain tests for image recognition and processing
"""
# from actual_algorithm_run import ExplorationRun
import unittest

import cv2

import image_recognition
from image_recognition_service import ImageRecognitionService
from rpi_service import RPIService


class ImageRecTest(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the local RPI connection. To use with test_conn in RPI side.
        """
        self.rpi_serv = RPIService()
        self.img_serv = ImageRecognitionService()
        # self.rpi_serv.connect_to_rpi('127.0.0.1', 65432, 62550)
        self.rpi_serv.connect_to_rpi()
        self.img_serv.connect_to_rpi()
        # self.explore_run = ExplorationRun()

    def test_img_send(self):
        self.rpi_serv.take_photo([])
        while True:
            img = self.img_serv.receive_image()
            if img:
                self.img_serv.image_recognition()

    def test_get_pos(self):
        img = cv2.imread("Images/picture0.jpg")
        img_recogniser = image_recognition.ImageRecogniser("classes.txt", "model_weights.pth")
        img_str, img_pred = img_recogniser.cv2_predict(img)

        print(img_str)
        cv2.imshow("", img_pred)

        self.assertEqual(True, True)

    def tearDown(self) -> None:
        """
        Disconnects RPI upon test end.
        """
        self.rpi_serv.disconnect_rpi()


if __name__ == '__main__':
    unittest.main()