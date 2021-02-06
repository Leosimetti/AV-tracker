import cv2
import time

from db.database_interaction import *
from db.video_store import *
from device_tracking.keyboard_tracker import process_keyboard_event, keyboard
from device_tracking.mouse_tracker import process_mouse_event, mouse

DEBUG = False

if __name__ == "__main__":
    conn = sqlite3.connect('db/signals.sqlite')
    prepareSignalDB(conn)
    prepareImageDB(conn)

    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    if DEBUG:
        time.sleep(10)
        read_signals(conn)

    # Example of import photo to db
    store_photo(cv2.VideoCapture(0), conn)

    keyboard.wait()
    conn.close()
