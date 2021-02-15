import pytest
import sqlite3

import keyboard
from queue import SimpleQueue
from device_tracking.keyboard_tracker import *
from device_tracking.mouse_tracker import *
from db.signals_db import prepare_signalDB
import pynput
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
key_name_to_key = {"space": pynput.keyboard.Key.space, "ctrl": pynput.keyboard.Key.ctrl, "esc": pynput.keyboard.Key.esc}


@pytest.mark.parametrize("key,expected_type", test_data_single_input)
def test_keyboard_tracker(db_connection, key, expected_type):
    event_queue = SimpleQueue()
    kb_tracker = KeyboardTracker(event_queue, True)
    kb_tracker.track()
    conn, cursor = db_connection

    keyboard_controller = pynput.keyboard.Controller()
    if len(key) == 1:
        keyboard_controller.press("s")
        keyboard_controller.release("s")
    else:
        keyboard_controller.press(key_name_to_key[key])
        keyboard_controller.release(key_name_to_key[key])

    event = event_queue.get()
    event.process()

    cursor = conn.cursor()
    cursor: sqlite3.Cursor = cursor.execute("SELECT id, dateTime, deviceType, actionType from signals")
    assert cursor.fetchone()[2:4] == ("KEYBOARD", expected_type)


mouse_button_name_to_button = {'left_click': pynput.mouse.Button.left, 'right_click': pynput.mouse.Button.right}

"""
@pytest.mark.parametrize("key,expected_type",
                         [("left_click", "CLOCK"), ("right_click", "SAS")])
def test_mouse_tracker(db_connection, key, expected_type):
    event_queue = SimpleQueue()
    mouse_tracker = MouseTracker(event_queue, True)
    mouse_tracker.track()
    conn, cursor = db_connection

    mouse_controller = pynput.mouse.Controller()

    mouse_controller.press(mouse_button_name_to_button[key])
    mouse_controller.release(mouse_button_name_to_button[key])

    event = event_queue.get()
    event.process()

    cursor = conn.cursor()
    cursor: sqlite3.Cursor = cursor.execute("SELECT id, dateTime, deviceType, actionType from signals")
    assert cursor.fetchone()[2:4] == ("MOUSE", "CLICK")
"""