from models import Model
import cv2
import numpy as np
from PIL import Image


class DNNModel(Model):
    MODEL_FILE = "models/res10_300x300_ssd_iter_140000.caffemodel"
    CONFIG_FILE = "models/deploy.prototxt.txt"

    def __init__(self, debug):
        self.debug = debug
        self.model = cv2.dnn.readNetFromCaffe(self.CONFIG_FILE, self.MODEL_FILE)

    def predict(self, image):

        image = cv2.resize(image, None, fx=0.5, fy=0.5)
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
                                     1.0, (300, 300), (104.0, 117.0, 123.0))
        self.model.setInput(blob)
        faces3 = self.model.forward()

        number_of_faces = 0
        for i in range(faces3.shape[2]):
            confidence = faces3[0, 0, i, 2]
            if confidence > 0.5:
                number_of_faces += 1
                if self.debug:
                    box = faces3[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (x, y, x1, y1) = box.astype("int")
                    cv2.rectangle(image, (x, y), (x1, y1), (0, 0, 255), 2)
        states = ["Absent", "Present", "Group"]
        state = states[number_of_faces if number_of_faces <= 2 else 2]
        return [state, image if self.debug else None]
