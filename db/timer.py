"""
Timer class to track when to set user state to passive based on K&M signals.
Evoke function insert_processed_data when state change
"""
import time

from db.processed_signals_db import insert_processed_data


class Timer:
    threshold = 5
    time_left = 5

    def __init__(self, new_threshold: int):
        if new_threshold > 0:
            Timer.threshold = new_threshold
            Timer.time_left = new_threshold
        else:
            raise ValueError("Threshold of timer should be positive number")

    @staticmethod
    def resetTimer():
        Timer.time_left = Timer.threshold

    @staticmethod
    def startTimer():
        while True:
            if Timer.time_left > 0:
                insert_processed_data("Present")
            while Timer.time_left > 0:
                time.sleep(1)
                Timer.time_left -= 1
            insert_processed_data("Absent")
