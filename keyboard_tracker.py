import keyboard
from datetime import datetime

endpoint = "http://some-url.com"


def process_keyboard_event(event: keyboard.KeyboardEvent):
    print(event.name, datetime.fromtimestamp(event.time))


