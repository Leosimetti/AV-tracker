from models import Model
import tensorflow
import cv2
import numpy as np
import os
from PIL import Image, ImageOps


class KerasModel(Model):

    MODEL_FILE = os.path.join(Model.MODEL_PATH, "keras_model.h5")

    def __init__(self, debug):
        self.debug = debug
        self.model = tensorflow.keras.models.load_model(self.MODEL_FILE)
        np.set_printoptions(suppress=True)

    def predict(self, img):

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        color_coverted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)

        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array

        prediction = self.model.predict(data)
        states = ["Present", "Absent", "Distracted"]
        state_index = tensorflow.math.argmax(prediction, axis=-1)[0]
        current_state = states[state_index]

        return [current_state, img]
