import sqlite3
import mouse
from database_interaction import insert_data
from datetime import datetime

endpoint = "http://some-url.com"

move_count = 0


def process_mouse_event(event):
    global move_count

    category = "ERROR"  # Just in case + IDE stop complaining

    event_type = type(event)
    if event_type is mouse.ButtonEvent:
        category = "M_CLICK"
        print(f"Mouse clicked at {datetime.fromtimestamp(event.time)}")
    elif event_type is mouse.WheelEvent:
        category = "M_WHEEL"
        print(f"Mouse wheel moved at {datetime.fromtimestamp(event.time)}")
    else:
        move_count += 1
        if move_count % 100 == 0:
            category = "M_MOVE"
            print(f"mouse.MoveEvent has been registered {move_count} times at {datetime.fromtimestamp(event.time)}!")
        else:
            return

    # Due to the problem that connection can be used only in the same thread where that connection was created
    # transfer of connection from main class is not valid. Most obvious solution is to create new connection.
    conn = sqlite3.connect('signals.sqlite')

    insert_data(conn, f"{datetime.fromtimestamp(event.time)}?M?{category}")



