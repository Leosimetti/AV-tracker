from models import Model
import tensorflow
import cv2
import numpy as np
from PIL import Image, ImageOps


class KerasModel(Model):
    MODEL_FILE = "models/keras_model.h5"

    def __init__(self, debug):
        self.debug = debug
        self.model = tensorflow.keras.models.load_model('models/keras_model.h5')
        np.set_printoptions(suppress=True)

    def predict(self, img):
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        color_coverted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)

        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        # turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = self.model.predict(data)
        states = ["Present", "Absent", "Distracted"]
        state_index = tensorflow.math.argmax(prediction, axis=-1)[0]
        current_state = states[state_index]
        # cv2.putText(img, f'{current_state}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        # cv2.putText(img, f'{curent_state}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # print(f"[{states[state_index]}] {time.ctime()} {prediction}")

        return [current_state, img if self.debug else None]
