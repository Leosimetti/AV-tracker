import cv2
import time
import threading

from GUI.WebUI import WebWindow
from db.processed_signals_db import *
from db.signals_db import *
from db.video_data_db import *
from db.timer import Timer
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.mouse_tracker import MouseTracker
from device_tracking.video_tracker import VideoTracker, VideoProcessor, ProcessedImageEvent
from models.DNN_model import DNNModel
from models.Keras_pb_model import KerasPBModel
from queue import SimpleQueue
import imageio
import os

# from video_tracking.omegamodel import determine_state
# from video_tracking.Keras_face_tracker import determine_state

# pyinstaller main.py --noconsole --onefile --add-data "GUI;GUI" --exclude-module tensorflow

DEBUG = True
USE_GUI = True

if __name__ == "__main__":
    if not os.path.exists("db"):
        os.mkdir("db")

    prepare_signalDB()
    prepare_imageDB()
    prepare_processed_signalDB()

    event_queue = SimpleQueue()
    frame_queue = SimpleQueue()

    kb_tracker = KeyboardTracker(event_queue, DEBUG)
    kb_tracker.track()

    mouse_tracker = MouseTracker(event_queue, DEBUG)
    mouse_tracker.track()

    # Video tracker
    video_tracker = VideoTracker(0, frame_queue, DEBUG)
    video_processor = VideoProcessor(
        frame_queue=frame_queue,
        event_queue=event_queue,
        debug=DEBUG,
        models=[DNNModel(DEBUG), KerasPBModel(DEBUG)]
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

    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    else:
        for file in os.listdir("tmp"):
            os.remove(f"tmp/{file}")
        os.rmdir("tmp")
        os.mkdir("tmp")


    if USE_GUI:
        w = WebWindow()
        threading.Thread(
            target= w.create_window,
            daemon=True
        ).start()


        while w.open:
            event = event_queue.get()
            event.process()
            if isinstance(event, ProcessedImageEvent):
                count += 1

                threading.Thread(
                    target=lambda: imageio.mimsave(f"tmp/{count} {event.state}.gif",
                                                   video_processor.snapshot_queue.get(), "GIF"),
                    daemon=True
                ).start()
        exit()
    else:
        while True:
            event = event_queue.get()
            event.process()
            if isinstance(event, ProcessedImageEvent):
                count += 1

                threading.Thread(
                    target=lambda: imageio.mimsave(f"tmp/{count} {event.state}.gif",
                                                   video_processor.snapshot_queue.get(), "GIF"),
                    daemon=True
                ).start()

                # print(f" Length is {len(video_tracker.sn[:])}")
                # get_image(event.image_id).show()
