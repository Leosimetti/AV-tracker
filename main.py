from keyboard_tracker import process_keyboard_event, keyboard
from mouse_tracker import process_mouse_event, mouse

if __name__ == "__main__":
    keyboard.on_press(callback=process_keyboard_event)
    mouse.hook(callback=process_mouse_event)
    keyboard.wait()
