import time
import cv2
import sqlite3
import datetime
import numpy as np
from PIL import Image

''' RESERVED
# PARAMETERS OF VIDEO CAPTURING
DEBUG = True
FILENAME = 'video.avi'
FRAMERATE = 20.0
RESOLUTION = (640, 480)
EXIT_KEYS = ['q', 'Q']
REGULATE_TIME = True

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Choose video camera interface?

    # Video codec
    # TODO Test on different platforms
    fourCC = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(FILENAME, fourCC, FRAMERATE, RESOLUTION)

    start_time = time.time()
    capture_duration = 5

    while cap.isOpened():
        if REGULATE_TIME & int(time.time() - start_time) > capture_duration:
            out = cv2.VideoWriter(FILENAME, fourCC, FRAMERATE, RESOLUTION)
        ret, frame = cap.read()

        if ret:
            # Write frame to video file
            out.write(frame)

            if DEBUG:
                # Show video
                cv2.imshow('frame', frame)

                # Stop program on exit key
                if cv2.waitKey(1) & 0xFF in [ord(i) for i in EXIT_KEYS]:
                    break
        else:
            break

    # Release everything
    out.release()
    cap.release()
    cv2.destroyAllWindows()
'''


def prepare_imageDB():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS images;")
    cursor.execute(
        "CREATE TABLE images"
        "( id INTEGER PRIMARY KEY AUTOINCREMENT, dateTime TEXT, state Text, size TEXT, image BLOB);")

    conn.commit()
    conn.close()


def insert_image(data):
    conn = sqlite3.connect("db/signals.sqlite")

    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO images
        (dateTime, image, state, size)
        VALUES (?, ?, ?, ?);
        """, data)

    conn.commit()
    conn.close()


def get_image(id):
    conn = sqlite3.connect("db/signals.sqlite")
    cursor = conn.execute("SELECT image, size from images WHERE id = ?", [id])

    row = cursor.fetchone()
    img = row[0]
    size = tuple(map(lambda x: int(x), row[1].split(" ")))

    np_arr = np.frombuffer(img, dtype=np.uint8).reshape(size)
    conn.commit()
    conn.close()

    return Image.fromarray(np_arr)
