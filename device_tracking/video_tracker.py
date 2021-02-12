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

    def __init__(self, frame_queue, event_queue, model, debug):
        super(DNNVideoProcessor, self).__init__()
        self.frame_queue = frame_queue
        self.event_queue = event_queue
        self.debug = debug
        self.model = model
        self.previous_state = None
        self.image_id = 0

    def run(self):
        while True:
            frame_data = self.frame_queue.get()
            img = frame_data.image
            timestamp = frame_data.timestamp
            state, debug_image = self.model.predict(img)

            if state != self.previous_state:
                self.image_id += 1
                if debug_image is not None:
                    image_array = cv2.cvtColor(debug_image, cv2.COLOR_BGR2RGB)
                else:
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
