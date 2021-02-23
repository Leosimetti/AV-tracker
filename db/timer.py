"""
Timer class to track when to set user state to passive based on K&M signals.
Evoke function insert_processed_data when state change
"""
import time

from db.processed_signals_db import insert_processed_data


class Timer:
    threshold = 5
    time_left = 5
    is_absent = True
    is_over = False

    def __init__(self, new_threshold):
        if new_threshold > 0:
            Timer.threshold = new_threshold
            Timer.time_left = new_threshold
        else:
            raise ValueError("Threshold of timer should be positive number")

    @classmethod
    def reset_timer(cls):
        cls.time_left = cls.threshold

    @classmethod
    def start_timer(cls):
        while True:
            if cls.time_left > 0:
                insert_processed_data("Present")
                cls.is_absent = False
            while cls.time_left > 0:
                time.sleep(1)
                cls.time_left -= 1
            if not cls.is_absent:
                insert_processed_data("Absent")
                cls.is_absent = True
                time.sleep(1)

    @classmethod
    def start_countdown(cls):
        while True:
            if cls.time_left > 0:
                cls.is_over = False
            while cls.time_left > 0:
                time.sleep(0.1)
                cls.time_left -= 0.1
            if not cls.is_absent:
                cls.is_absent = True
