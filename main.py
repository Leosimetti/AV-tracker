import cv2
import time
import threading

from GUI import *
from db.processed_signals_db import *
from db.signals_db import *
from db.video_data_db import *
from db.timer import Timer
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.mouse_tracker import MouseTracker
from device_tracking.video_tracker import VideoTracker, DNNVideoProcessor, ProcessedImageEvent
from models.DNN_model import DNNModel
from models.Keras_model import KerasModel
from queue import SimpleQueue
import imageio


# from video_tracking.omegamodel import determine_state
# from video_tracking.Keras_face_tracker import determine_state

def create_gif(imgs, count, state):
    # time.sleep(0.43)
    imageio.mimsave(f"tmp/{count}[{state}].gif", imgs[:], "GIF")


def callback(w):
    while w.exists:
        event = event_queue.get()
        event.process()
        if isinstance(event, ProcessedImageEvent):
            print("sas")
            get_image(event.image_id).show()


DEBUG = True
USE_GUI = False

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
        model=KerasModel(DEBUG)
    )
    video_tracker.track()
    video_processor.start()

    # Start timer that help determine user presence based on K&M input singals
    timer = threading.Thread(target=Timer.startTimer, daemon=True)
    timer.start()

    # For testing purposes
    # cap = cv2.VideoCapture(0)
    # determine_state(cap)

    count = 0

    if USE_GUI:
        w = Window(Tk())
        threading.Thread(target=lambda: callback(w), daemon=True).start()
        w.create()
    else:
        while True:
            event = event_queue.get()
            event.process()
            if isinstance(event, ProcessedImageEvent):
                count += 1

                threading.Thread(
                    target=lambda:
                    create_gif(video_processor.snapshot, count, event.state),
                    # imageio.mimsave(f"tmp/{count}[{event.state}].gif", video_processor.snapshot[:], "GIF"),
                    daemon=True
                ).start()

                print(f" Length is {len(video_processor.snapshot[:])}")
                # get_image(event.image_id).show()
