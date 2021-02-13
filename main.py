import cv2
import time
import threading

from db.processed_signals_db import *
from db.signals_db import *
from db.video_data_db import *
from db.timer import Timer
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.mouse_tracker import MouseTracker
from device_tracking.video_tracker import VideoTracker, DNNVideoProcessor, ProcessedImageEvent
from models.DNN_model import DNNModel
from queue import SimpleQueue

# from video_tracking.omegamodel import determine_state
# from video_tracking.Keras_face_tracker import determine_state

DEBUG = True

if __name__ == "__main__":
    # Preparing databases
    prepare_signalDB()
    prepare_imageDB()
    prepare_processed_signalDB()

    # Creating queues
    event_queue = SimpleQueue()
    frame_queue = SimpleQueue()

    # Assigning trackers for K&M
    kb_tracker = KeyboardTracker(event_queue, DEBUG)
    kb_tracker.track()

    mouse_tracker = MouseTracker(event_queue, DEBUG)
    mouse_tracker.track()

    # Video tracker
    video_tracker = VideoTracker(0, frame_queue, DEBUG)
    video_processor = DNNVideoProcessor(
        frame_queue=frame_queue,
        event_queue=event_queue,
        debug=DEBUG,
        model=DNNModel(DEBUG)
    )
    video_tracker.track()
    video_processor.start()

    # Start timer that help determine user presence based on K&M input singals
    timer = threading.Thread(target=Timer.startTimer)
    timer.start()

    # For testing purposes
    # cap = cv2.VideoCapture(0)
    # determine_state(cap)

    while True:
        event = event_queue.get()
        event.process()
        if isinstance(event, ProcessedImageEvent):
            get_image(event.image_id).show()
