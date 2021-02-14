from models import Model
import cv2
import numpy as np
from PIL import Image, ImageOps


# https://github.com/opencv/opencv/issues/16582

class DNNModel(Model):
    MODEL_FILE = "models/keras_pb_model.pb"

    def __init__(self, debug):
        self.debug = debug
        self.model = cv2.dnn.readNetFromTensorflow(self.MODEL_FILE)

    def predict(self, image):

        image = cv2.resize(image, None, fx=0.5, fy=0.5)
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, size=(224, 224), swapRB=True, crop=False)
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
        states = ["No face", "Present", "Group"]
        state = states[number_of_faces if number_of_faces <= 2 else 2]
        return [state, image if self.debug else None]


MODEL_FILE = "keras_model.pb"

if __name__ == "__main__":
    import tensorflow as tf

    # model = tf.keras.models.load_model('keras_model.h5')
    # model.save('my_model', save_format='tf')
    #
    # from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
    #
    # loaded = tf.saved_model.load('my_model')
    # infer = loaded.signatures['serving_default']
    #
    # f = tf.function(infer).get_concrete_function(input_1=tf.TensorSpec(shape=[None, 224, 224, 3], dtype=tf.float32))
    # f2 = convert_variables_to_constants_v2(f)
    # graph_def = f2.graph.as_graph_def()
    #
    # # Export frozen graph
    # with tf.io.gfile.GFile('frozen_graph.pb', 'wb') as f:
    #     f.write(graph_def.SerializeToString())

    # net = cv2.dnn.readNet('frozen_graph.pb')
    # inp = np.random.standard_normal([1, 3, 224, 224]).astype(np.float32)
    # net.setInput(inp)
    # out = net.forward()
    # print(out.shape)

    tensorflowNet = cv2.dnn.readNet('frozen_graph.pb')

    cap = cv2.VideoCapture(0)
    no_error = True
    while no_error:
        no_error, img = cap.read()
        # rows, cols, channels = img.shape

        # blob = cv2.dnn.blobFromImage(cv2.resize(img, (224, 224)))

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        color_coverted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)

        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        #
        # # turn the image into a numpy array
        # image_array = np.asarray(image)
        #
        # # Normalize the image
        # normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        #
        # # Load the image into the array
        # data[0] = normalized_image_array
        #
        # # print(data[0].shape)

        #
        # inpBlob = cv2.dnn.blobFromImage(img,
        #                                 size=(224, 224),
        #                                 mean=(0, 0, 0),
        #                                 swapRB=False,
        #                                 crop=False)

        tensorflowNet.setInput(image)

        # Runs a forward pass to compute the net output
        out = tensorflowNet.forward()

        print(f"[Flat] {out}")
        out = out.flatten()
        print(f"{out}")
        classId = np.argmax(out)
        confidence = out[classId]

        states = ["Present", "Absent", "Distracted"]

        print(f"[{states[classId]}], {confidence}")

        # Show the image with a rectagle surrounding the q objects
        cv2.imshow('Image', img)
        cv2.waitKey()
        cv2.destroyAllWindows()
