from flask import Flask, render_template, Response, request
# from flaskwebgui import FlaskUI
import time
import os
from db.timer import Timer
import webbrowser

# http://fm.1tvcrimea.ru:8000/stream.mp3
# http://91.219.74.220:8000/Vanya-high.mp3


class WebWindow:
    def __init__(self, video_tracker):
        self.video_tracker = video_tracker

    def on_exit(self):
        import keyboard
        import mouse

        keyboard.unhook_all()
        mouse.unhook_all()

        self.video_tracker.RECORDING = False
        os._exit(0)

    def create_window(self):
        app = Flask(__name__)

        @app.route('/video_feed')
        def video_feed():
            return Response(self.video_tracker.track(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @app.route('/')
        def stream():
            return render_template("base.html")

        @app.route('/keyboard_disable')
        def keyboard_disable():
            import keyboard
            keyboard.unhook_all()
            return Response("Keyboard tracking disabled")

        @app.route('/keyboard_enable')
        def keyboard_enable():
            from device_tracking.keyboard_tracker import KeyboardTracker
            tracker = KeyboardTracker(True)
            tracker.track()
            return Response("Keyboard tracking enabled")

        @app.route('/mouse_disable')
        def mouse_disable():
            import mouse
            mouse.unhook_all()
            return Response("Mouse tracking disabled")

        @app.route('/mouse_enable')
        def mouse_enable():
            from device_tracking.mouse_tracker import MouseTracker
            tracker = MouseTracker(True)
            tracker.track()
            return Response("Mouse tracking enabled")

        @app.route('/video_disable')
        def video_disable():
            self.video_tracker.RECORDING = False
            return Response("Video tracking disabled")

        @app.route('/video_enable')
        def video_enable():
            self.video_tracker.RECORDING = True
            return Response("Video tracking enabled")

        @app.route('/km_state')
        def km_state():
            bool_to_state = {False: "Present", True: "Absent"}
            return bool_to_state[Timer.time_left < 1]

        @app.route('/change_fps', methods=['POST'])
        def change_fps():
            self.video_tracker.processor.FPS = int(request.values['fps'])
            return Response("Changed FPS")

        @app.route('/change_threshold', methods=['POST'])
        def change_threshold():
            new_threshold = int(request.values['new_threshold'])
            Timer(new_threshold)
            return Response("Changed timer threshold")

        @app.route("/exit", methods=['POST'])
        def leave():
            self.on_exit()
            # return Response("")

        # call the 'run' method
        webbrowser.open('http://127.0.0.1:5000/ ', new=2)
        app.run()
