import tensorflow
from PIL import Image, ImageOps
import numpy as np
import cv2
import time
from db.video_store import *

PROCESSING_FREQUENCY = 255400
DISPLAY_IMAGE = True


def determine_state(cap):
    conn = sqlite3.connect('db/signals.sqlite')

    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    # Load the model
    model = tensorflow.keras.models.load_model('models/keras_model.h5')

    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    previous_state = None
    # frame_counter = 0

    ids = 0

    while True:
        # if frame_counter == PROCESSING_FREQUENCY:
        frame_counter = 0

        _, img = cap.read()

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
        prediction = model.predict(data)
        states = ["Present", "Not present", "Distracted"]
        state_index = tensorflow.math.argmax(prediction, axis=-1)[0]

        if previous_state == None:
            previous_state = state_index

        elif previous_state != state_index:
            previous_state = state_index
            ids += 1

            # Inserting an array
            insertImage(image_array, states[state_index], image_array.shape)

            get_image(ids).show() if DISPLAY_IMAGE else None

        print(f"[{states[state_index]}] {time.ctime()} {prediction}")
        # else:
        #     frame_counter += 1
        time.sleep(0.21)
