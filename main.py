from keyboard_tracker import process_keyboard_event, keyboard
from mouse_tracker import process_mouse_event, mouse
from database_interaction import *
from functools import partial


if __name__ == "__main__":
    conn = sqlite3.connect('signals.sqlite')
    prepareDB(conn)

    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    keyboard.wait()
    conn.close()
