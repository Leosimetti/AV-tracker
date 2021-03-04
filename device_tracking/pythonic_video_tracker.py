import os
import time
from collections import deque
import copy
from datetime import datetime
from queue import SimpleQueue
from threading import Thread
import pcv
import simplejpeg

import cv2
import imageio
from pcv.vidIO import LockedCamera, SlowCamera, Camera

from db.video_data_db import insert_image
from device_tracking import Tracker

placeholder = imageio.mimread("device_tracking/200.gif")
gif_frame = 0


def stream_placeholder():
    global placeholder
    global gif_frame
    while True:
        current_frame = cv2.resize(placeholder[gif_frame], (320, 240))
        current_frame = cv2.imencode('.jpg', current_frame)[1].tobytes()
        gif_frame = gif_frame + 1 \
            if gif_frame + 1 < len(placeholder) \
            else 0
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')


placeholder_stream = stream_placeholder()


class VideoProcessor:
    GIF_LENGTH = 10
    FPS = 5

    def __init__(self, models, debug):
        super(VideoProcessor, self).__init__()
        self.debug = debug

        if self.debug:
            if not os.path.exists("tmp"):
                os.mkdir("tmp")
            else:
                for file in os.listdir("tmp"):
                    os.remove(f"tmp/{file}")
                os.rmdir("tmp")
                os.mkdir("tmp")
            os.chmod("tmp", 0o777)

        self.state_change_count = 0
        self.models = models
        self.previous_state = None
        self.image_id = 0
        self.snapshot = deque()
        self.gif_queue = SimpleQueue()
        self.state_change_time = None

        for i in range(2):
            Thread(target=self.record_gifs, daemon=True).start()

    def record_gifs(self):
        while True:
            gif = self.gif_queue.get()
            count, state, prev_state, snapshot = gif
            imageio.mimsave(f"tmp/{count} {prev_state} to {state}.gif", snapshot, "GIF")

    @staticmethod
    def put_outlined_text(img, text, where):
        cv2.putText(img, text, where,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        cv2.putText(img, text, where,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    @staticmethod
    def determine_state(states):
        if len(states) == 1:
            return states[0]

        elif (states[0] == "Present" or states[0] == "Group") and states[1] == "Present":
            return "Present"

        elif (states[0] == "No face" and states[1] == "Present") or (states[0] == "Group" and states[1] == "Present"):
            return "Present"

        elif states[1] == "Distracted":
            return "Distracted"

        elif states[0] == "No face" and states[1] == "Absent" or states[0] == "Group" and states[1] == "Absent":
            return "Absent"

        elif (states[0] == "Present" and states[1] == "Absent") or (states[0] == "No face" and states[1] == "Present"):
            # TODO: need other signal data
            return "Inconsistent"

    def set_cam(self, cam):
        self._cam = cam

    def preprocess(self, img):
        # TODO: ubrat' eto gavno s debug_image[PICTURE_TO_CHOOSE]
        PICTURE_TO_CHOOSE = 0
        MIN_TIME_SPENT_IN_STATE = 2
        offset = 33

        states = ["Error"] * len(self.models)
        debug_image = [None] * len(self.models)
        for i, model in enumerate(self.models):
            states[i], debug_image[i] = model.predict(img)
            VideoProcessor.put_outlined_text(
                img=debug_image[PICTURE_TO_CHOOSE],
                text=f'{states[i]}',
                where=(1, 30 + offset * i)
            )

        timestamp = datetime.now()
        VideoProcessor.put_outlined_text(
            img=debug_image[PICTURE_TO_CHOOSE],
            text=f'{timestamp.hour}:{timestamp.minute}:{timestamp.second}',
            where=(185, 233)
        )

        self.snapshot.append(cv2.cvtColor(debug_image[PICTURE_TO_CHOOSE], cv2.COLOR_BGR2RGB))

        if len(self.snapshot) > self.GIF_LENGTH:
            self.snapshot.popleft()

        resulting_state = self.determine_state(states)

        state_changed = resulting_state != self.previous_state

        if state_changed and self.previous_state is not None:
            # and (self.state_change_time is None or (time.time() - self.state_change_time > MIN_TIME_SPENT_IN_STATE)):
            self.state_change_count += 1
            self.state_change_time = time.time()

            self.image_id += 1
            if self.debug:
                image_array = cv2.cvtColor(debug_image[PICTURE_TO_CHOOSE], cv2.COLOR_BGR2RGB)
            else:
                image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            insert_image(
                (
                    timestamp,
                    memoryview(image_array),
                    resulting_state,
                    " ".join(map(lambda x: str(x), image_array.shape))
                )
            )

            if self.debug:
                self.gif_queue.put(
                    (
                        self.state_change_count,
                        resulting_state,
                        self.previous_state,
                        copy.copy(self.snapshot),
                    )
                )
                print(f"[{resulting_state}] {timestamp}")
        self.previous_state = resulting_state

        start = time.perf_counter()
        while time.perf_counter() - start < 1 / self.FPS:
            self._cam.grab()

        if self.debug:
            return debug_image[PICTURE_TO_CHOOSE]
        else:
            return img


class PythonicVideoTracker(Tracker):

    @staticmethod
    def find_available_cams(current):
        arr = []
        for i in range(0, 10):
            if i != current:
                cap = cv2.VideoCapture(i)
                if cap.read()[0]:
                    arr.append(i)
                cap.release()
            else:
                arr.append(current)
        return arr

    def __init__(self, source, debug, models):
        # self.available_cams = self.find_available_cams()
        self.source = source
        self.models = models
        self.debug = debug
        self.processor = VideoProcessor(models=self.models, debug=self.debug)
        self.cam = LockedCamera(self.source,
                                preprocess=self.processor.preprocess
                                )
        self.processor.set_cam(self.cam)

    def change_cam(self, n):
        self.cam.open(n)

    def toggle(self):
        if self.cam.isOpened():
            self.cam.release()
        else:
            self.cam.open(self.source)

    def change_camera(self):
        self.cam.open(self.source)

    def obtain_frame(self):
        import queue

        def do_task(queue, self):
            try:
                queue.put(next(self.cam))
            except pcv.vidIO.OutOfFrames:
                pass

        q = queue.Queue()
        grab_frame = Thread(target=do_task, args=(q, self), daemon=True)
        grab_frame.start()
        try:
            return q.get(block=True, timeout=0.85)
        except queue.Empty:
            raise pcv.vidIO.OutOfFrames

    def track(self):
        while True:
            try:
                _, frame = self.obtain_frame()
                if frame is not None:
                    # frame = self.processor.preprocess(frame)
                    status, buffer = cv2.imencode('.jpg', frame)
                    if status:
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except pcv.vidIO.OutOfFrames:
                yield next(placeholder_stream)
