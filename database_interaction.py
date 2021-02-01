import sqlite3
import queue


def prepareDB(conn):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS signals;")
    cursor.execute(
        "CREATE TABLE signals ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " dateTIme TEXT, deviceType VARCHAR(1), actionType TEXT);")

    conn.commit()

def interact(conn, data):
    cursor = conn.cursor()

    sas, kek, lol = data.split(" ")

    cursor.execute(f"""
    INSERT INTO signals
    (dateTime, deviceType, actionType)
    VALUES (?, ?, ?);
    """, (sas, kek, lol))

    conn.commit()
