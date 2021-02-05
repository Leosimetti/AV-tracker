from datetime import datetime
import keyboard
import sqlite3

from db.database_interaction import insert_data

endpoint = "http://some-url.com"


def process_keyboard_event(event: keyboard.KeyboardEvent):
    conn = sqlite3.connect('db/signals.sqlite')

    key = str(event.name)
    if len(key) == 1:
        category = "K_TYPING"
    else:
        category = "K_NON-TYPING"

    insert_data(conn, f"{datetime.fromtimestamp(event.time)}?K?{category}")

    print(key, datetime.fromtimestamp(event.time))

    # connection should be closed once not necessary
    conn.close()
