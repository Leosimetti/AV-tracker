from pynput import mouse
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime
from device_tracking import togglable


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
        super(MouseTracker, self).__init__(debug)
        self.move_count = 0
        self.scroll_count = 0
        self.previous_event = None
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll,
        )

    def click_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"Mouse was clicked at {event.timestamp}!")

    def move_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.move_count} times"
                        f" at {event.timestamp}!")

    def wheel_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.scroll_count} times"
                        f" at {event.timestamp}!")

    @togglable
    def on_move(self, x, y):
        self.move_count += 1
        if self.move_count % 200 == 0:
            event = MouseTrackingEvent(MouseTrackingEvent.MOVE, timestamp=datetime.now())
            self.move_msg(event)
            self.move_count = 0
            event.process()

    @togglable
    def on_click(self, x, y, button, pressed):
        if pressed:
            event = MouseTrackingEvent(MouseTrackingEvent.CLICK, timestamp=datetime.now())
            self.click_msg(event)
            event.process()

    @togglable
    def on_scroll(self, x, y, dx, dy):
        self.scroll_count += 1
        if self.scroll_count % 10 == 0:
            event = MouseTrackingEvent(MouseTrackingEvent.WHEEL, timestamp=datetime.now())
            self.wheel_msg(event)
            event.process()
            self.scroll_count = 0

    def track(self):
        self.listener.start()

    def disable(self):
        self.listener.stop()

    def enable(self):
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll,
        )
        self.track()


if __name__ == "__main__":
    t = MouseTracker(debug=True)
