from keyboard_tracker import process_keyboard_event, keyboard
from mouse_tracker import process_mouse_event, mouse
from database_interaction import *
import time

DEBUG = False

if __name__ == "__main__":
    conn = sqlite3.connect('signals.sqlite')
    prepareDB(conn)

    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    if DEBUG:
        time.sleep(10)
        read_signals(conn)

    keyboard.wait()
    conn.close()
