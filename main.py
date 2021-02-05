from device_tracking.keyboard_tracker import process_keyboard_event, keyboard
from device_tracking.mouse_tracker import process_mouse_event, mouse
from db.database_interaction import *
import time

DEBUG = False

if __name__ == "__main__":
    conn = sqlite3.connect('db/signals.sqlite')
    prepareDB(conn)

    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    if DEBUG:
        time.sleep(10)
        read_signals(conn)

    keyboard.wait()
    conn.close()
