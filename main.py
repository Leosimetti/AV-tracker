from db.database_interaction import *
from db.video_store import *
from device_tracking.keyboard_tracker import process_keyboard_event, keyboard
from device_tracking.mouse_tracker import process_mouse_event, mouse
# from video_tracking.omegamodel import determine_state
from video_tracking.Keras_face_tracker import determine_state


DEBUG = False

if __name__ == "__main__":
    conn = sqlite3.connect('db/signals.sqlite')
    prepare_signalDB()
    prepare_imageDB()


    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)

    if DEBUG:
        time.sleep(10)
        read_signals()
    # To capture video from webcam.
    cap = cv2.VideoCapture(0)
    determine_state(cap)

    keyboard.wait()
    conn.close()
