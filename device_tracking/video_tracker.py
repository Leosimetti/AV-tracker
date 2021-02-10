from device_tracking import TrackingEvent, Tracker
from threading import Thread
import cv2
from datetime import datetime
import numpy as np
from db.video_store import insert_image, get_image
import time


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


class DNNVideoProcessor(Thread):
    MODEL_FILE = "models/res10_300x300_ssd_iter_140000.caffemodel"
    CONFIG_FILE = "models/deploy.prototxt.txt"

    def __init__(self, frame_queue, event_queue, debug):
        super(DNNVideoProcessor, self).__init__()
        self.frame_queue = frame_queue
        self.event_queue = event_queue
        self.debug = debug
        self.model = cv2.dnn.readNetFromCaffe(self.CONFIG_FILE, self.MODEL_FILE)
        self.previous_state = None
        self.image_id = 0

    def run(self):
        while True:
            frame_data = self.frame_queue.get()
            img = frame_data.image
            timestamp = frame_data.timestamp
            img = cv2.resize(img, None, fx=0.5, fy=0.5)

            blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)),
                                         1.0, (300, 300), (104.0, 117.0, 123.0))
            self.model.setInput(blob)
            faces3 = self.model.forward()

            number_of_faces = 0
            for i in range(faces3.shape[2]):
                confidence = faces3[0, 0, i, 2]
                if confidence > 0.5:
                    number_of_faces += 1

            states = ["Absent", "Present", "Group"]
            state = states[number_of_faces if number_of_faces <= 2 else 2]

            if state != self.previous_state:
                self.image_id += 1
                image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.event_queue.put(
                    ProcessedImageEvent(
                        timestamp,
                        image_array,
                        state,
                        image_array.shape,
                        self.image_id
                    )
                )
                if self.debug:
                    print(f"[{state}] {timestamp}")

            self.previous_state = state
            # time.sleep(0.01)


class VideoTracker(Tracker):

    def __init__(self, source, queue, debug):
        self.debug = debug
        self.queue = queue
        self.source = source

    def collect_frames(self, source):
        cap = cv2.VideoCapture(source)
        no_error = True
        while no_error:
            no_error, frame = cap.read()
            if no_error:
                self.queue.put(
                    Frame(
                        image=frame,
                        timestamp=datetime.now()
                    )
                )
        time.sleep(0.2)

    def track(self):
        Thread(target=self.collect_frames,
               args=(self.source,),
               daemon=True).start()
