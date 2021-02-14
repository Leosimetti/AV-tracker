from device_tracking import TrackingEvent, Tracker
from threading import Thread
import cv2
from datetime import datetime
import numpy as np
from db.video_data_db import insert_image, get_image
import time
from queue import SimpleQueue
from collections import deque
from copy import deepcopy


class ProcessedImageEvent(TrackingEvent):

    def __init__(self, timestamp, processed_image, state, size, image_id):
        self.timestamp = timestamp
        self.processed_image = memoryview(processed_image)
        self.size = " ".join(map(lambda dim: str(dim), size))
        self.state = state
        self.data = (self.timestamp, self.processed_image, self.state, self.size)
        self.image_id = image_id

    def process(self):
        insert_image(self.data)


class Frame:
    def __init__(self, image, timestamp):
        self.image = image
        self.timestamp = timestamp


class VideoProcessor(Thread):
    GIF_LENGTH = 50

    def __init__(self, frame_queue, event_queue, models, debug):
        super(VideoProcessor, self).__init__()
        self.frame_queue = frame_queue
        self.event_queue = event_queue
        self.debug = debug
        self.models = models
        self.previous_state = None
        self.image_id = 0
        self.snapshot = deque()
        self.daemon = True
        self.snapshot_queue = SimpleQueue()
        self.state_change_time = None

    def determine_state(self, states):
        if (states[0] == "Present" or states[0] == "Group") and states[1] == "Present":
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

    def run(self):  # TODO: refactor; It does not track both models...
        # TODO: ubrat' eto gavno s debug_image[PICTURE_TO_CHOOSE]
        PICTURE_TO_CHOOSE = 0
        while True:
            frame_data = self.frame_queue.get()
            img = frame_data.image

            offset = 33
            states = ["Error"] * len(self.models)
            debug_image = [None] * len(self.models)
            for i, model in enumerate(self.models):
                states[i], debug_image[i] = model.predict(img)
                cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{states[i]}', (1, 30 + offset * i),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
                cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{states[i]}', (1, 30 + offset * i),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            timestamp = frame_data.timestamp
            cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{timestamp.hour}:{timestamp.minute}:{timestamp.second}',
                        (185, 233),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
            cv2.putText(debug_image[PICTURE_TO_CHOOSE], f'{timestamp.hour}:{timestamp.minute}:{timestamp.second}',
                        (185, 233),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            self.snapshot.append(debug_image[PICTURE_TO_CHOOSE])
            # if len(self.snapshot) > self.GIF_LENGTH:  # TODO remove for optimisation
            #     self.snapshot.popleft()

            resulting_state = self.determine_state(states)

            if resulting_state != self.previous_state and (
                     self.state_change_time is None or (time.time() - self.state_change_time > 5)):
                self.state_change_time = time.time()
                self.snapshot_queue.put(deepcopy(self.snapshot))
                self.snapshot.clear()

                self.image_id += 1
                if debug_image is not None:
                    image_array = cv2.cvtColor(debug_image[PICTURE_TO_CHOOSE], cv2.COLOR_BGR2RGB)
                else:
                    image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                self.event_queue.put(
                    ProcessedImageEvent(
                        timestamp,
                        image_array,
                        resulting_state,
                        image_array.shape,
                        self.image_id
                    )
                )
                if self.debug:
                    print(f"[{resulting_state}] {timestamp}")
            self.previous_state = resulting_state
        # time.sleep(0.01)


class VideoTracker(Tracker):

    def __init__(self, source, queue, debug):
        self.source = source
        self.queue = queue
        self.debug = debug

    def collect_frames(self, source):
        frame_rate = 20
        prev = 0

        cap = cv2.VideoCapture(source)
        no_error = True
        while no_error:

            time_elapsed = time.time() - prev
            # res, image = cap.read()
            no_error, frame = cap.read()

            if time_elapsed > 1. / frame_rate:
                prev = time.time()

                if no_error:
                    self.queue.put(
                        Frame(
                            image=frame,
                            timestamp=datetime.now()
                        )
                    )
            # time.sleep(0.2)

    def track(self):
        Thread(target=self.collect_frames,
               args=(self.source,),
               daemon=True).start()
