import cv2
import time

from db.database_interaction import *
from db.video_store import *
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.mouse_tracker import MouseTracker
from video_tracking.omegamodel import determine_state
from queue import Queue

# from video_tracking.Keras_face_tracker import determine_state


DEBUG = True

if __name__ == "__main__":
    conn = sqlite3.connect('db/signals.sqlite')
    prepare_signalDB()
    prepare_imageDB()
    conn.close()

    event_queue = Queue()

    kb_tracker = KeyboardTracker(event_queue, DEBUG)
    kb_tracker.track()

    mouse_tracker = MouseTracker(event_queue, DEBUG)
    mouse_tracker.track()

    cap = cv2.VideoCapture(0)
    # determine_state(cap)

    while True:
        event = event_queue.get()
        event.process()
        event_queue.task_done()