"""
Contain tests for image recognition and processing
"""
import unittest
from actual_run import ExplorationRun
import base64
import rpi_service


class ImageRecTest(unittest.TestCase):
    def test_image_rec_offline(self):
        explore = ExplorationRun()
        rpi_serv = rpi_service.RPIService()
        # Simulate encoding and sending
        with open("Images/picture0.jpg", "rb") as f:
            img_bytes = base64.b64encode(f.read())
        img_str = img_bytes.decode()
        payload = str.encode(img_str)

        # Simulate receiving and decoding
        img_str2 = payload.decode(rpi_serv.DEFAULT_ENCODING_TYPE)
        explore.image_rec(img_str2)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
