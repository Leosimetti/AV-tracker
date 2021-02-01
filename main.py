from keyboard_tracker import process_keyboard_event, keyboard
from mouse_tracker import process_mouse_event, mouse
from database_interaction import *


if __name__ == "__main__":
    conn = sqlite3.connect('signals.sqlite')
    prepareDB(conn)

    interact(conn, "M kok sas")
    interact(conn, "M kok sas")
    interact(conn, "K kok sas")
    interact(conn, "M kok sas")

    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    conn.commit()

    conn.close()
    keyboard.wait()

