import mouse
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime


class MouseTrackingEvent(TrackingEvent):
    DEVICE_TYPE = "MOUSE"
    CLICK = "CLICK"
    WHEEL = "WHEEL"
    MOVE = "MOVE"

    def __init__(self, action_type, timestamp):
        self.action_type = action_type
        self.timestamp = timestamp
        self.data = (self.timestamp, self.DEVICE_TYPE, self.action_type)

    def process(self):
        insert_data(self.data)

    def is_wheel(self):
        return self.action_type == self.WHEEL

    def is_click(self):
        return self.action_type == self.CLICK

    def is_move(self):
        return self.action_type == self.MOVE

    def __ne__(self, other):
        return self.action_type != other.action_type

    def __eq__(self, other):
        return self.action_type == other.action_type

    def __str__(self):
        if self.action_type == self.CLICK:
            return "mouse.ButtonEvent"
        elif self.action_type == self.WHEEL:
            return "mouse.WheelEvent"
        else:
            return "mouse.MoveEvent"


class MouseTracker(Tracker):

    def __init__(self, debug):
        if debug:
            self.event_dict = {}
        self.move_count = 0
        self.scroll_count = 0
        self.debug = debug
        self.previous_event = None

    def click_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"Mouse was clicked at {event.timestamp}!")

    def move_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.move_count} times"
                        f" at {event.timestamp}!")

    def wheel_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.scroll_count} times"
                        f" at {event.timestamp}!")

    def on_mouse_event(self, event):
        timestamp = datetime.fromtimestamp(event.time)
        if isinstance(event, mouse.WheelEvent):
            event = MouseTrackingEvent(MouseTrackingEvent.WHEEL, timestamp)
        elif isinstance(event, mouse.MoveEvent):
            event = MouseTrackingEvent(MouseTrackingEvent.MOVE, timestamp)
        else:
            event = MouseTrackingEvent(MouseTrackingEvent.CLICK, timestamp)

        if self.previous_event is None:
            self.previous_event = event
        elif self.previous_event != event:

            if self.previous_event.is_move():
                self.move_msg(self.previous_event)
                self.move_count = 0
                self.previous_event.process()
                if event.is_wheel():
                    self.scroll_count = 1
                else:
                    self.click_msg(event)
                    event.process()

            elif self.previous_event.is_wheel():
                self.wheel_msg(self.previous_event)
                self.scroll_count = 0
                self.previous_event.process()
                if event.is_move():
                    self.move_count = 1
                else:
                    self.click_msg(event)
                    event.process()
            elif self.previous_event.is_click():
                if event.is_move():
                    self.move_count += 1
                else:
                    self.scroll_count += 1

        elif event.is_click():
            self.click_msg(event)
        elif event.is_move():
            self.move_count += 1
        else:
            self.scroll_count += 1

        self.previous_event = event

    def track(self):
        mouse.hook(self.on_mouse_event)
