import time
import cv2
import sqlite3
import datetime
import numpy as np
import os
from PIL import Image

PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(PATH, 'signals.sqlite')


def prepare_imageDB():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS images;")
    cursor.execute(
        "CREATE TABLE images"
        "( id INTEGER PRIMARY KEY AUTOINCREMENT, dateTime TEXT, state Text, size TEXT, image BLOB);")

    conn.commit()
    conn.close()


def insert_image(data):
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO images
        (dateTime, image, state, size)
        VALUES (?, ?, ?, ?);
        """, data)

    conn.commit()
    conn.close()


def get_image(ID):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT image, size from images WHERE id = ?", [ID])

    row = cursor.fetchone()
    img = row[0]
    size = tuple(map(lambda x: int(x), row[1].split(" ")))

    np_arr = np.frombuffer(img, dtype=np.uint8).reshape(size)
    conn.commit()
    conn.close()

    return Image.fromarray(np_arr)
