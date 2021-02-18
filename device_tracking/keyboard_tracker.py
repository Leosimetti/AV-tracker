import keyboard
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime


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

    def __init__(self, queue, debug):
        self.queue = queue
        self.debug = debug

    def track(self):
        keyboard.on_press(self.on_press)

    def on_press(self, event):
        key = str(event.name)
        if len(key) == 1 or key == "space":
            category = KeyboardTrackingEvent.TYPING
        else:
            category = KeyboardTrackingEvent.NON_TYPING

        timestamp = datetime.utcfromtimestamp(event.time)
        tracking_event = KeyboardTrackingEvent(category, timestamp)
        tracking_event.process()
        self.debug_info(f"{timestamp} {category}")
