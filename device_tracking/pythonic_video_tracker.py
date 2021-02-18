from pcv.vidIO import LockedCamera, VideoWriter
from datetime import datetime
import cv2
from models.DNN_model import DNNModel
from models.Keras_model import KerasModel
from models.Keras_pb_model import KerasPBModel
from collections import deque
from copy import deepcopy
from queue import SimpleQueue
from db.video_data_db import insert_image


# class DatabaseWriter(VideoWriter):
#
#     def __init__(self, db="images.sqlite"):
#         super(VideoWriter, self).__init__()
#         self.conn = sqlite3.connect(db)
#         self.cursor = self.conn.cursor()
#
#     def write(self, img):
#         data = (datetime.now(), img, state, img.shape)
#         self.cursor.execute("""
#         INSERT INTO images
#         (dateTime, image, state, size)
#         VALUES (?, ?, ?, ?);
#         """, data)
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.conn.close()


class VideoProcessor:
    GIF_LENGTH = 20

    def __init__(self, models, debug):
        super(VideoProcessor, self).__init__()
        self.debug = debug
        self.models = models
        self.previous_state = None
        self.image_id = 0
        self.snapshot = deque()
        self.daemon = True
        self.snapshot_queue = SimpleQueue()
        self.state_change_time = None

    @staticmethod
    def determine_state(states):
        if len(states) == 1:
            return states[0]

        elif (states[0] == "Present" or states[0] == "Group") and states[1] == "Present":
            return "Present"

        elif (states[0] == "No face" and states[1] == "Present") or (states[0] == "Group" and states[1] == "Present"):
            return "Present"

        elif states[1] == "Distracted":
            return "Distracted"

        elif states[0] == "No face" and states[1] == "Absent" or states[0] == "Group" and states[1] == "Absent":
            return "Absent"

        elif (states[0] == "Present" and states[1] == "Absent") or (states[0] == "No face" and states[1] == "Present"):
            # TODO: need other signal data
            return "Inconsistent"

    def __call__(self, img):  # TODO: refactor; It does not track both models...
        # TODO: ubrat' eto gavno s debug_image[PICTURE_TO_CHOOSE]
        PICTURE_TO_CHOOSE = 0
        MIN_TIME_SPENT_IN_STATE = 5
        offset = 33
        states = ["Error"] * len(self.models)
        debug_image = [None] * len(self.models)
        for i, model in enumerate(self.models):
            states[i], debug_image[i] = model.predict(img)
            cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{states[i]}', (1, 30 + offset * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
            cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{states[i]}', (1, 30 + offset * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        timestamp = datetime.now()
        cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{timestamp.hour}:{timestamp.minute}:{timestamp.second}',
                    (185, 233),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{timestamp.hour}:{timestamp.minute}:{timestamp.second}',
                    (185, 233),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        self.snapshot.append(debug_image[PICTURE_TO_CHOOSE])

        if len(self.snapshot) > self.GIF_LENGTH:  # TODO remove for optimisation
            self.snapshot.popleft()

        resulting_state = self.determine_state(states)

        state_changed = resulting_state != self.previous_state

        if state_changed:
            self.state_change_time = datetime.now()
            self.snapshot_queue.put(deepcopy(self.snapshot))
            self.snapshot.clear()

            self.image_id += 1
            if debug_image is not None:
                image_array = cv2.cvtColor(debug_image[PICTURE_TO_CHOOSE], cv2.COLOR_BGR2RGB)
            else:
                image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            insert_image(
                (
                    timestamp,
                    memoryview(image_array),
                    resulting_state,
                    str(image_array.shape)
                )
            )

            if self.debug:
                print(f"[{resulting_state}] {timestamp}")
        self.previous_state = resulting_state

        if self.debug:
            return debug_image[PICTURE_TO_CHOOSE]
        else:
            return img
    # time.sleep(0.01)


# writer = DatabaseWriter()
processor = VideoProcessor(models=[DNNModel(True), KerasModel(True), KerasPBModel(True)],
                           debug=True)


if __name__ == "__main__":
    with LockedCamera(0, process=processor) as cam:
        cam.stream()
