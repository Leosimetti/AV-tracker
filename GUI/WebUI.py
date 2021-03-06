import json

from flask import Flask, render_template, Response, request
# from flaskwebgui import FlaskUI
import time
import os
from db.timer import Timer
import webbrowser


# http://fm.1tvcrimea.ru:8000/stream.mp3
# http://91.219.74.220:8000/Vanya-high.mp3


class WebWindow:
    def __init__(self, video_tracker, mouse_tracker, kb_tracker):
        self.video_tracker = video_tracker
        self.mouse_tracker = mouse_tracker
        self.kb_tracker = kb_tracker

    def on_exit(self):
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
            self.kb_tracker.disable()
            return Response("Keyboard tracking disabled")

        @app.route('/keyboard_enable')
        def keyboard_enable():
            self.kb_tracker.enable()
            return Response("Keyboard tracking enabled")

        @app.route('/mouse_disable')
        def mouse_disable():
            self.mouse_tracker.disable()
            return Response("Mouse tracking disabled")

        @app.route('/mouse_enable')
        def mouse_enable():
            self.mouse_tracker.enable()
            return Response("Mouse tracking enabled")

        @app.route('/available_cameras')
        def available_cameras():
            current = self.video_tracker.source
            arr = self.video_tracker.find_available_cams(current)
            arr = json.dumps(arr)
            return Response(arr)

        @app.route('/video_disable', methods=['POST'])
        def video_disable():
            self.video_tracker.disable()
            return Response("Video tracking disabled")

        @app.route('/video_enable', methods=['POST'])
        def video_enable():
            self.video_tracker.enable()
            return Response("Video tracking enabled")

        @app.route('/km_state')
        def km_state():
            bool_to_state = {False: "Present", True: "Absent"}
            return bool_to_state[Timer.time_left < 1]

        @app.route('/change_fps', methods=['POST'])
        def change_fps():
            print(int(request.values['fps']))
            self.video_tracker.processor.FPS = int(request.values['fps'])
            return Response("Changed FPS")

        @app.route('/change_cam', methods=['POST'])
        def change_cam():
            cam = int(request.values['source'])
            if self.video_tracker.source != cam:
                self.video_tracker.change_cam(cam)
            return Response("Changed Camera")

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
        webbrowser.open('http://127.0.0.1:5000/', new=2)
        app.run()
