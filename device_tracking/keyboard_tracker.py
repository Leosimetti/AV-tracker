from pynput import keyboard
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime
from device_tracking import togglable
import multiprocessing
from functools import partial
from db.timer import Timer
import threading

event_queue = multiprocessing.Queue()
disable_event = multiprocessing.Event()
PROCESS_EVENTS = True


def process_events():
    while PROCESS_EVENTS:
        # print(self.event_queue.qsize())
        event = event_queue.get()
        event.process()


processing_thread = threading.Thread(
    target=process_events,
    daemon=True
)
processing_thread.start()


def start_listener(flag, event_queue):
    def on_press(flag, event_queue, key):
        if flag.is_set():
            import sys
            sys.exit(0)
        else:
            Timer.reset_timer()
            try:
                char = key.char
                category = KeyboardTrackingEvent.TYPING
            except AttributeError:
                category = KeyboardTrackingEvent.NON_TYPING

            timestamp = datetime.now()
            tracking_event = KeyboardTrackingEvent(category, timestamp)
            event_queue.put(tracking_event)
            print(f"{timestamp} {category}")

    with keyboard.Listener(on_press=partial(on_press, flag, event_queue)) as listen:
        listen.join()


class KeyboardTrackingEvent(TrackingEvent):
    DEVICE_TYPE = "KEYBOARD"
    TYPING = "TYPING"
    NON_TYPING = "NON_TYPING"

    def __init__(self, action_type, timestamp):
        self.action_type = action_type
        self.timestamp = timestamp
        self.data = (self.timestamp, self.DEVICE_TYPE, self.action_type)

    def process(self):
        insert_data(self.data)


class KeyboardTracker(Tracker):

    def __init__(self, debug):
        super(KeyboardTracker, self).__init__(debug)
        self.listener = multiprocessing.Process(
            target=start_listener,
            args=(disable_event, event_queue,),
            daemon=True
        )

    def disable(self):
        disable_event.set()

    def enable(self):
        self.listener = multiprocessing.Process(
            target=start_listener,
            args=(disable_event, event_queue,),
            daemon=True
        )
        disable_event.clear()
        self.listener.start()

    def track(self):
        self.listener.start()


