from models import Model
import cv2
import numpy as np
import os
from PIL import Image, ImageOps


# https://github.com/opencv/opencv/issues/16582

class KerasPBModel(Model):

    MODEL_FILE = os.path.join("models", "frozen_graph.pb")

    def __init__(self, debug):
        self.debug = debug
        self.model = cv2.dnn.readNet(self.MODEL_FILE)

    def predict(self, img):
        tensorflowNet = self.model

        no_error = True
        while no_error:
            color_coverted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(color_coverted)

            # resize the image to a 224x224 with the same strategy as in TM2:
            # resizing the image to be at least 224x224 and then cropping from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.ANTIALIAS)

            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

            blob = cv2.dnn.blobFromImage(cv2.resize(normalized_image_array, (224, 224)))
            tensorflowNet.setInput(blob)

            # Runs a forward pass to compute the net output
            out = tensorflowNet.forward()

            # print(f"[Flat] {out}")
            # out = out.flatten()
            # print(f"{out}")
            classId = np.argmax(out)
            # confidence = out[classId]

            states = ["Present", "Absent", "Distracted"]


            # state_index = tensorflow.math.argmax(prediction, axis=-1)[0]
            current_state = states[classId]

            return [current_state, img]

            # print(f"[{states[classId]}], {confidence}")


# MODEL_FILE = "keras_model.pb"

# converts h5 to pb
if __name__ == "__main__":
    import tensorflow as tf

    model = tf.keras.models.load_model('keras_model.h5')
    # model.save('my_model', save_format='tf')
    #
    from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

    # Save model to SavedModel format
    tf.saved_model.save(model, "./models")

    # Convert Keras model to ConcreteFunction
    full_model = tf.function(lambda x: model(x))
    full_model = full_model.get_concrete_function(
        tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

    # Get frozen ConcreteFunction
    frozen_func = convert_variables_to_constants_v2(full_model)
    frozen_func.graph.as_graph_def()

    layers = [op.name for op in frozen_func.graph.get_operations()]


    # Save frozen graph from frozen ConcreteFunction to hard drive
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                      logdir="./frozen_models",
                      name="frozen_graph.pb",
                      as_text=False)

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

    # tensorflowNet = cv2.dnn.readNet('frozen_graph.pb')
    #
    # cap = cv2.VideoCapture(0)
    # no_error = True
    # while no_error:
    #     no_error, img = cap.read()
    #     # rows, cols, channels = img.shape
    #
    #     data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    #     color_coverted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     image = Image.fromarray(color_coverted)
    #
    #     # resize the image to a 224x224 with the same strategy as in TM2:
    #     # resizing the image to be at least 224x224 and then cropping from the center
    #     size = (224, 224)
    #     image = ImageOps.fit(image, size, Image.ANTIALIAS)
    #
    #     image_array = np.asarray(image)
    #     normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    #
    #     blob = cv2.dnn.blobFromImage(cv2.resize(normalized_image_array, (224, 224)))
    #     #
    #     # # turn the image into a numpy array
    #     # image_array = np.asarray(image)
    #     #
    #     # # Normalize the image
    #     # normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    #     #
    #     # # Load the image into the array
    #     # data[0] = normalized_image_array
    #     #
    #     # # print(data[0].shape)
    #
    #     #
    #     # inpBlob = cv2.dnn.blobFromImage(img,
    #     #                                 size=(224, 224),
    #     #                                 mean=(0, 0, 0),
    #     #                                 swapRB=False,
    #     #                                 crop=False)
    #
    #     tensorflowNet.setInput(blob)
    #
    #     # Runs a forward pass to compute the net output
    #     out = tensorflowNet.forward()
    #
    #     print(f"[Flat] {out}")
    #     out = out.flatten()
    #     print(f"{out}")
    #     classId = np.argmax(out)
    #     confidence = out[classId]
    #
    #     states = ["Present", "Absent", "Distracted"]
    #
    #     print(f"[{states[classId]}], {confidence}")
    #
    #     # Show the image with a rectagle surrounding the q objects
    #     cv2.imshow('Image', img)
    #     cv2.waitKey()
    #     cv2.destroyAllWindows()
