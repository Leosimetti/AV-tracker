import sqlite3
import queue


def prepareDB(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS signals;")
    cursor.execute(
        "CREATE TABLE signals "
        "( id INTEGER PRIMARY KEY AUTOINCREMENT,dateTime TEXT, deviceType VARCHAR(1), actionType TEXT);")

    conn.commit()


def insert_data(conn: sqlite3.Connection, data):
    cursor = conn.cursor()

    # Split by ? instead of " " because dateTime contain space.
    dateTime, deviceType, actionType = data.split("?")

    cursor.execute(f"""
    INSERT INTO signals
    (dateTime, deviceType, actionType)
    VALUES (?, ?, ?);
    """, [dateTime, deviceType, actionType])

    conn.commit()


def read_signals(conn: sqlite3.Connection):
    cursor = conn.execute("SELECT id, dateTime, deviceType, actionType from signals")
    print("{:^6}|{:^26}|{:^6}|{:6}".format("id", "dateTime", "device", "action"))
    for row in cursor:
        print("{:^6}|{:26}|{:^6}|{:6}".format(row[0], row[1], row[2], row[3]))
