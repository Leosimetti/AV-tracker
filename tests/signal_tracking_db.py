import pytest
import sqlite3

import keyboard
from queue import SimpleQueue
from device_tracking.keyboard_tracker import *
from db.signals_db import prepare_signalDB
from pynput.keyboard import Key, Controller
import time


@pytest.fixture
def db_connection():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS signals;")
    cursor.execute(
        "CREATE TABLE signals "
        "( id INTEGER PRIMARY KEY AUTOINCREMENT,dateTime TEXT, deviceType VARCHAR(1), actionType TEXT);")

    conn.commit()

    yield conn, cursor
    conn.close()


test_data_single_input = [("a", "TYPING"),
                          ("space", "TYPING"),
                          ("ctrl", "NON_TYPING"),
                          ("esc", "NON_TYPING")]
key_name_to_key = {"space": Key.space, "ctrl": Key.ctrl, "esc": Key.esc}


@pytest.mark.parametrize("key,expected_type", test_data_single_input)
def test_keyboard_tracker_single_input(db_connection, key, expected_type):
    event_queue = SimpleQueue()
    kb_tracker = KeyboardTracker(event_queue, True)
    kb_tracker.track()
    conn, cursor = db_connection

    keyboard = Controller()
    if len(key) == 1:
        keyboard.press("s")
        keyboard.release("s")
    else:
        keyboard.press(key_name_to_key[key])

    event = event_queue.get()
    event.process()

    cursor = conn.cursor()
    cursor: sqlite3.Cursor = cursor.execute("SELECT id, dateTime, deviceType, actionType from signals")
    assert cursor.fetchone()[2:4] == ("KEYBOARD", expected_type)

# def test_keyboard_tracker_multiple_input()
