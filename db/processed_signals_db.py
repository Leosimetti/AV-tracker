import sqlite3
import datetime


def prepare_processed_signalDB():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS processed_signals;")
    cursor.execute(
        "CREATE TABLE processed_signals"
        "( id INTEGER PRIMARY KEY AUTOINCREMENT,dateTime TEXT, state TEXT);")

    conn.commit()
    conn.close()


def insert_processed_data(state: str):
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()
    dateTime = datetime.datetime.now()

    cursor.execute(f"""
    INSERT INTO processed_signals
    (dateTime, state)
    VALUES (?, ?);
    """, [dateTime, state])

    conn.commit()
    conn.close()
