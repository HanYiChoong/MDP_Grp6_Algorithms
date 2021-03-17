"""
Contain tests for image recognition and processing
"""
import time
import unittest
from threading import Thread

from detecto import utils
import cv2

import image_recognition
from image_recognition_service import ImageRecognitionService
from rpi_service import RPIService
from utils.enums import Direction


class ImageRecTest(unittest.TestCase):
    def test_img_send(self):
        self.rpi_serv = RPIService()
        self.img_serv = ImageRecognitionService()
        self.rpi_serv.connect_to_rpi('127.0.0.1', 65432)
        self.img_serv.connect_to_rpi('127.0.0.1', 62550)
        # self.rpi_serv.connect_to_rpi()
        # self.img_serv.connect_to_rpi()

        Thread(target=self.img_serv.check_for_image, daemon=True).start()
        self.rpi_serv.take_photo([5, 5], Direction.NORTH)
        time.sleep(3)
        self.rpi_serv.take_photo([10, 5], Direction.WEST)
        self.img_serv.display_image()
        input()
        self.assertEqual(True, True)

        self.rpi_serv.disconnect_rpi()

    def test_get_pos(self):
        img = utils.read_image("tests/Images/WhatsApp Image 2021-03-16 at 17.57.44.jpeg")
        img_recogniser = image_recognition.ImageRecogniser("image_recognition/classes.txt",
                                                           "image_recognition/model_weights2.pth")
        img_str, img_pred = img_recogniser.cv2_predict(img)

        print("Detected", img_str)
        while True:
            cv2.imshow("", img_pred)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
