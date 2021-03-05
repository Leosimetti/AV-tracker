from pynput import mouse
from device_tracking import TrackingEvent, Tracker
from db.signals_db import insert_data
from datetime import datetime
from device_tracking import togglable
import multiprocessing
import threading
from db.timer import Timer
from functools import partial

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
    move_count = 0
    scroll_count = 0

    def on_move(flag, event_queue, x, y):
        if flag.is_set():
            import sys
            sys.exit(0)
        else:
            Timer.reset_timer()
            nonlocal move_count
            move_count += 1
            if move_count % 200 == 0:
                event = MouseTrackingEvent(MouseTrackingEvent.MOVE, timestamp=datetime.now())
                print(event)
                move_count = 0
                event_queue.put(event)

    def on_click(flag, event_queue, x, y, button, pressed):
        if flag.is_set():
            import sys
            sys.exit(0)
        else:
            Timer.reset_timer()
            if pressed:
                event = MouseTrackingEvent(MouseTrackingEvent.CLICK, timestamp=datetime.now())
                print(event)
                event_queue.put(event)

    def on_scroll(flag, event_queue, x, y, dx, dy):
        if flag.is_set():
            import sys
            sys.exit(0)
        else:
            Timer.reset_timer()
            nonlocal scroll_count
            scroll_count += 1
            if scroll_count % 10 == 0:
                event = MouseTrackingEvent(MouseTrackingEvent.WHEEL, timestamp=datetime.now())
                print(event)
                event_queue.put(event)
                scroll_count = 0

    with mouse.Listener(
            on_click=partial(on_click, flag, event_queue),
            on_scroll=partial(on_scroll, flag, event_queue),
            on_move=partial(on_move, flag, event_queue)
    ) as listen:
        listen.join()


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
        self.listener = multiprocessing.Process(
            target=start_listener,
            args=(disable_event, event_queue,),
            daemon=True
        )

    def click_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"Mouse was clicked at {event.timestamp}!")

    def move_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.move_count} times"
                        f" at {event.timestamp}!")

    def wheel_msg(self, event: MouseTrackingEvent):
        self.debug_info(f"{event} has been registered {self.scroll_count} times"
                        f" at {event.timestamp}!")

    def track(self):
        self.listener.start()

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


if __name__ == "__main__":
    t = MouseTracker(debug=True)
