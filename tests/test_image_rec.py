"""
Contain tests for image recognition and processing
"""
import unittest
from actual_run import ExplorationRun
import base64


class ImageRecTest(unittest.TestCase):
    def test_image_rec_offline(self):
        explore = ExplorationRun()
        # Simulate encoding and sending
        with open("Images/picture0.jpg", "rb") as f:
            img_bytes = base64.b64encode(f.read())
        img_str = img_bytes.decode("utf-8")
        payload = str.encode(img_str)

        # Simulate receiving and decoding
        img_str2 = payload.decode('utf-8')
        explore.image_rec(img_str2)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
