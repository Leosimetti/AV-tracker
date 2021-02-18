import os
import time
from collections import deque
from copy import deepcopy
from datetime import datetime
from queue import SimpleQueue
from threading import Thread

import cv2
import imageio
from pcv.vidIO import LockedCamera

from db.video_data_db import insert_image
from device_tracking import Tracker


class VideoProcessor:
    GIF_LENGTH = 10

    def __init__(self, models, debug):
        super(VideoProcessor, self).__init__()
        self.debug = debug
        if self.debug:
            if not os.path.exists("tmp"):
                os.mkdir("tmp")
            else:
                for file in os.listdir("tmp"):
                    os.remove(f"tmp/{file}")
                os.rmdir("tmp")
                os.mkdir("tmp")
            os.chmod("tmp", 0o777)

        self.state_change_count = 1
        self.models = models
        self.previous_state = None
        self.image_id = 0
        self.snapshot = deque()
        self.snapshot_queue = SimpleQueue()
        self.state_change_time = None

    def record_gif(self, state):
        Thread(target=
               lambda: imageio.mimsave(f"tmp/{self.state_change_count} {state}.gif", deepcopy(self.snapshot), "GIF"),
               daemon=True
               ).start()
        self.state_change_count += 1

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
        MIN_TIME_SPENT_IN_STATE = 2
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

        self.snapshot.append(cv2.cvtColor(debug_image[PICTURE_TO_CHOOSE], cv2.COLOR_BGR2RGB))

        if len(self.snapshot) > self.GIF_LENGTH:  # TODO remove for optimisation
            self.snapshot.popleft()

        resulting_state = self.determine_state(states)

        state_changed = resulting_state != self.previous_state

        if state_changed and self.previous_state is not None:
                # and (self.state_change_time is None or (time.time() - self.state_change_time > MIN_TIME_SPENT_IN_STATE)):

            self.state_change_time = time.time()

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
                    " ".join(map(lambda x: str(x), image_array.shape))
                )
            )

            if self.debug:
                self.record_gif(state=f"from {self.previous_state} to {resulting_state}")
                print(f"[{resulting_state}] {timestamp}")
        self.previous_state = resulting_state

        time.sleep(0.1377)
        if self.debug:
            return debug_image[PICTURE_TO_CHOOSE]
        else:
            return img


class PythonicVideoTracker(Tracker):

    def __init__(self, source, debug, models):
        self.source = source
        self.models = models
        self.debug = debug
        self.processor = VideoProcessor(models=self.models, debug=self.debug)

    def track(self):
        with LockedCamera(self.source, process=self.processor, display="Live Feed") as cam:
            cam.stream()

# writer = DatabaseWriter()
