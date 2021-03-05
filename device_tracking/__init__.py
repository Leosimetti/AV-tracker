from abc import abstractmethod
from db.timer import Timer
import queue
import multiprocessing
import threading


def togglable(func):
    def wrapper(self, *args, **kwargs):
        if self.ENABLED:
            Timer.reset_timer()
            return func(self, *args, **kwargs)
        else:
            pass

    return wrapper


class TrackingEvent:

    @abstractmethod
    def process(self):
        pass


class Tracker:

    def __init__(self, debug):
        self.PROCESS_EVENTS = True
        self.ENABLED = True
        self.debug = debug

    def debug_info(self, msg):
        if hasattr(self, "debug"):
            if isinstance(self.debug, bool):
                if self.debug:
                    print(msg)
            else:
                print(f"Make sure that your {self.__class__} attribute is of type bool!")
        else:
            print(f"Define {self.__class__}.debug attribute in your class!")

    @abstractmethod
    def track(self):
        raise NotImplementedError()

    @abstractmethod
    def disable(self):
        raise NotImplementedError()

    @abstractmethod
    def enable(self):
        raise NotImplementedError()
