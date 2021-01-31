import mouse
from datetime import datetime

endpoint = "http://some-url.com"

move_count = 0


def process_mouse_event(event):
    global move_count
    event_type = type(event)
    if event_type is mouse.ButtonEvent:
        print(f"Mouse clicked at {datetime.fromtimestamp(event.time)}")
    elif event_type is mouse.WheelEvent:
        print(f"Mouse wheel moved at {datetime.fromtimestamp(event.time)}")
    else:
        move_count += 1
        if move_count % 100 == 0:
            print(f"mouse.MoveEvent has been registered {move_count} times at {datetime.fromtimestamp(event.time)}!")



