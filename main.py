#!/usr/bin/sudo python3

import threading

from db.processed_signals_db import *
from db.signals_db import *
from db.timer import Timer
from db.video_data_db import *
from device_tracking.mouse_tracker import MouseTracker
from device_tracking.keyboard_tracker import KeyboardTracker
from device_tracking.pythonic_video_tracker import PythonicVideoTracker
from models.DNN_model import DNNModel
from models.Keras_pb_model import KerasPBModel
from GUI.WebUI import WebWindow
import os

# for Linux (maybe even MacOS):
# sudo pyinstaller main.py --noconsole --onefile --add-data GUI:GUI --exclude-module tensorflow
# for windows:
# pyinstaller main.py --noconsole --onefile --add-data "GUI;GUI" --exclude-module tensorflow

DEBUG = True
USE_GUI = not True

if __name__ == "__main__":
    if not os.path.exists("db"):
        os.mkdir("db")

    prepare_signal_db()
    prepare_imageDB()
    prepare_processed_signalDB()

    kb_tracker = KeyboardTracker(DEBUG)
    kb_tracker.track()

    mouse_tracker = MouseTracker(DEBUG)
    mouse_tracker.track()

    timer = threading.Thread(target=Timer.start_timer, daemon=True)
    timer.start()

    # Video tracker
    video_tracker = PythonicVideoTracker(
        source=0,
        debug=DEBUG,
        models=[DNNModel(DEBUG), KerasPBModel(DEBUG)]
    )

    w = WebWindow(
        video_tracker=video_tracker,
        mouse_tracker=mouse_tracker,
        kb_tracker=kb_tracker
    )
    w.create_window()
