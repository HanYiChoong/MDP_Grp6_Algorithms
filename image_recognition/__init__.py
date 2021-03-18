import cv2
import matplotlib.pyplot as plt
import numpy as np
from detecto import core, utils

from image_recognition import detect_object_position as detect_pos


def detecto_test(img_path: str) -> None:
    """
    Tests detecto installation by reading an image.

    :param img_path: path to image
    """
    image = utils.read_image(img_path)
    plt.imshow(image)
    plt.show()


class ImageRecogniser:
    """
    Master class for detecting images
    """

    def __init__(self, classes_path: str, weights_path: str):
        with open(classes_path, "r") as f:
            classes = f.readlines()

        classes = [x[:-1] for x in classes]
        self.model = core.Model.load(weights_path, classes)

    def webcam_test(self) -> None:
        """
        Creates a webcam window and runs detection.
        """
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = self.cv2_predict(frame)

            cv2.imshow('frame', frame)
            cv2.waitKey(1)
            # if cv2.waitKey(1) & 0xFF == ord('q'): break

        cv2.destroyAllWindows()

    def read_image(self, img_path: str) -> None:
        """
        Runs detecto on a provided image and creates an opencv window.
        :param img_path: path to image
        """
        image = utils.read_image(img_path)

        image = self.cv2_predict(image)

        cv2.imshow('frame', image)
        cv2.waitKey(1)
        # if cv2.waitKey(1) & 0xFF == ord('q'): break

        cv2.destroyAllWindows()

    def cv2_predict(self, img_path: str) -> (str, np.ndarray):
        """
        Predicts and draws bounding boxes over the provided image.
        :param img_path: The input image
        :return: list of items, modified image
        """
        colour = (0, 255, 0)
        img = utils.read_image(img_path)

        defaults = utils.default_transforms()
        new_img = defaults(img)
        labels, boxes, scores = self.model.predict(new_img)

        img = cv2.imread(img_path)

        scores = scores.tolist()
        boxes = boxes.tolist()
        img_lab = None

        if len(scores) > 0 and max(scores) > 0.7:
            index_list = list()
            for i in range(len(scores)):
                if scores[i] > 0.7:
                    index_list.append(i)
                
            size_list = list()
            for i in index_list:
                x_width = boxes[i][0] - boxes[i][1]
                size_list.append(x_width)
            
            max_index = size_list.index(max(size_list))
            max_index = index_list[max_index]
            # max_index = scores.index(max(scores))

            bound_box = [int(x) for x in boxes[max_index]]
            label = labels[max_index]
            score = scores[max_index]
            cv2.rectangle(img, (bound_box[0], bound_box[1]), (bound_box[2], bound_box[3]), colour, 2)
            cv2.putText(img, '{}: {}'.format(label, round(score, 2)), (bound_box[0], bound_box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 3)

            per_width = abs(bound_box[1] - bound_box[0])
            obj_dist = detect_pos.distance_to_camera(per_width)
            x_centre = (bound_box[0] + bound_box[1]) / 2
            pos = detect_pos.get_obj_pos(obj_dist, x_centre)

            img_lab = label

        return img_lab, img
