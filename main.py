import cv2
import time

from db.database_interaction import *
from db.video_store import *
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.mouse_tracker import MouseTracker
from device_tracking.video_tracker import VideoTracker, DNNVideoProcessor, ProcessedImageEvent
from video_tracking.omegamodel import determine_state
from queue import SimpleQueue

# from video_tracking.Keras_face_tracker import determine_state


DEBUG = True

if __name__ == "__main__":
    conn = sqlite3.connect('db/signals.sqlite')
    prepare_signalDB()
    prepare_imageDB()
    conn.close()

    event_queue = SimpleQueue()
    frame_queue = SimpleQueue()

    kb_tracker = KeyboardTracker(event_queue, DEBUG)
    kb_tracker.track()

    mouse_tracker = MouseTracker(event_queue, DEBUG)
    mouse_tracker.track()

    video_tracker = VideoTracker(0, frame_queue, DEBUG)
    video_processor = DNNVideoProcessor(
        frame_queue=frame_queue,
        event_queue=event_queue,
        debug=DEBUG
    )
    video_tracker.track()
    video_processor.start()

    # cap = cv2.VideoCapture(0)
    # determine_state(cap)
    while True:
        event = event_queue.get()
        event.process()
        if isinstance(event, ProcessedImageEvent):
            get_image(event.image_id).show()
