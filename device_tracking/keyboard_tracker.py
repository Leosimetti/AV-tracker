from pynput import keyboard
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime
from device_tracking import togglable


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
    def disable(self):
        self.listener.stop()

    def enable(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press
        )
        self.track()

    def __init__(self, debug):
        super(KeyboardTracker, self).__init__(debug)
        self.listener = keyboard.Listener(
            on_press=self.on_press
        )

    def track(self):
        self.listener.start()

    @togglable
    def on_press(self, key):
        try:
            char = key.char
            category = KeyboardTrackingEvent.TYPING
        except AttributeError:
            category = KeyboardTrackingEvent.NON_TYPING

        timestamp = datetime.now()
        tracking_event = KeyboardTrackingEvent(category, timestamp)
        self.event_queue.put(tracking_event)
        self.debug_info(f"{timestamp} {category}")
