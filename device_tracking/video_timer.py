"""
Timer class to track when to set user state to passive based on K&M signals.
Evoke function insert_processed_data when state change
"""
import time


class VideoTimer:
    threshold = 1.5
    time_left = 1.5
    is_over = False

    def __init__(self, new_threshold):
        VideoTimer.threshold = new_threshold
        VideoTimer.time_left = new_threshold
        VideoTimer.is_over = False

    @staticmethod
    def resetTimer():
        VideoTimer.time_left = VideoTimer.threshold
        VideoTimer.is_over = False

    @staticmethod
    def startCountdown():
        while True:
            if VideoTimer.time_left > 0:
                VideoTimer.is_over = False
            while VideoTimer.time_left > 0:
                time.sleep(0.1)
                VideoTimer.time_left -= 0.1
            VideoTimer.is_over = True
