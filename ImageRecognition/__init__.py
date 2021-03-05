"""
Contains class for image recognition
"""
from detecto import core, utils
import matplotlib.pyplot as plt
import cv2


def detecto_test(img_path: str):
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

    def webcam_test(self):
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

    def read_image(self, img_path: str):
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

    def cv2_predict(self, img):
        """
        Predicts and draws bounding boxes over the provided image.
        :param img:
        :return: modified image
        """
        labels, boxes, scores = self.model.predict_top(img)
        # pred = cv2.resize(pred, dsize=(args.size, args.size))

        scores = scores.tolist()
        boxes = boxes.tolist()

        if len(scores) > 0 and max(scores) > 0.5:
            max_index = scores.index(max(scores))

            bound_box = [int(x) for x in boxes[max_index]]
            label = labels[max_index]
            score = scores[max_index]
            cv2.rectangle(img, (bound_box[0], bound_box[1]), (bound_box[2], bound_box[3]), (255, 0, 0), 3)
            cv2.putText(img, '{}: {}'.format(label, round(score, 2)), (bound_box[0], bound_box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        return img
