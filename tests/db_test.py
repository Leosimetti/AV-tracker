import pytest
import sqlite3
import datetime
import numpy as np

from db.processed_signals_db import *
from db.signals_db import *
from db.video_data_db import *
from db.timer import Timer


@pytest.fixture
def db_connection():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()
    yield conn, cursor
    conn.close()


def test_preparation_signals_db(db_connection):
    conn, cursor = db_connection
    prepare_signalDB()
    presence = cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='signals'")
    assert presence.fetchone()[0] == 1


def test_preparation_video_db(db_connection):
    conn, cursor = db_connection
    prepare_imageDB()
    presence = cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='images' ")
    assert presence.fetchone()[0] == 1


def test_preparation_processed_signals_db(db_connection):
    conn, cursor = db_connection
    prepare_processed_signalDB()
    presence = cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='processed_signals'")
    assert presence.fetchone()[0] == 1


def test_insert_signal_data(db_connection):
    conn, cursor = db_connection
    time_example = str(datetime.datetime.now())
    insert_data([time_example, "K", "TYPING"])
    data = cursor.execute("SELECT id, dateTime, deviceType, actionType from signals")
    assert data.fetchone()[1:] == (time_example, "K", "TYPING")


def test_insert_image(db_connection):
    conn, cursor = db_connection
    time_example = str(datetime.datetime.now())
    blank_image = np.zeros((2, 2))
    stored_image = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00 '  # Binary representation of blank_image
    insert_image([time_example, blank_image, "ACTIVE", "10KB"])
    data = cursor.execute("SELECT id, dateTime, state, size, image from images")
    assert data.fetchone()[1:] == (time_example, "ACTIVE", "10KB", stored_image)


def test_insert_processed_data(db_connection):
    conn, cursor = db_connection
    current_time = str(datetime.datetime.now())
    insert_processed_data("ACTIVE")
    data = cursor.execute("SELECT id, dateTime, state from processed_signals")
    assert data.fetchone()[2] == "ACTIVE"
