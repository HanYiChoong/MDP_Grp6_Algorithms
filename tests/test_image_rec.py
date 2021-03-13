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
    def test_conn(self):
        rpi_serv = RPIService()
        rpi_serv.connect_to_rpi('127.0.0.1', 65432)
        rpi_serv.disconnect_rpi()

        self.assertEqual(True, True)

    def test_get_pos(self):
        img = cv2.imread("Images/picture0.jpg")
        img_recogniser = ImageRecognition.ImageRecogniser("classes.txt", "model_weights.pth")
        img_str, img_pred = img_recogniser.cv2_predict(img)

        print(img_str)
        cv2.imshow("", img_pred)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
