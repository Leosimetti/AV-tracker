import sqlite3
import queue


def prepare_signalDB():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS signals;")
    cursor.execute(
        "CREATE TABLE signals "
        "( id INTEGER PRIMARY KEY AUTOINCREMENT,dateTime TEXT, deviceType VARCHAR(1), actionType TEXT);")

    conn.commit()
    conn.close()


def insert_data(data):
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.cursor()

    cursor.execute(f"""
    INSERT INTO signals
    (dateTime, deviceType, actionType)
    VALUES (?, ?, ?);
    """, data)

    conn.commit()
    conn.close()


def read_signals():
    conn = sqlite3.connect('db/signals.sqlite')
    cursor = conn.execute("SELECT id, dateTime, deviceType, actionType from signals")

    print("{:^6}|{:^26}|{:^6}|{:6}".format("id", "dateTime", "device", "action"))
    for row in cursor:
        print("{:^6}|{:26}|{:^6}|{:6}".format(row[0], row[1], row[2], row[3]))

    conn.close()
