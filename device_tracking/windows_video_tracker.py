from device_tracking.pythonic_video_tracker import PythonicVideoTracker, placeholder_stream, VideoProcessor
# from pygrabber.dshow_graph import FilterGraph
import queue
import cv2

class Camera:

    def put_image(self, image):
        try:
            self.buffer.put_nowait(image)
        except queue.Full:
            pass

    def __init__(self, source):
        self.source = source
        # self.graph = FilterGraph()
        # self.graph.add_video_input_device(source)
        # # self.graph.add_sample_grabber(lambda image: self.buffer.put(image))
        # self.graph.add_null_render()
        # self.graph.prepare_preview_graph()
        # self.graph.run()
        self.buffer = queue.Queue(1)
        # self.buffer.maxsize = 5

    def grab(self):
        pass

class WindowsVideoTracker(PythonicVideoTracker):

    def __init__(self, source, debug, models):
        self.source = source
        self.models = models
        self.debug = debug
        self.processor = VideoProcessor(models=self.models, debug=self.debug)
        # self.graph = FilterGraph()
        # self.graph.add_video_input_device(0)
        # self.graph.add_sample_grabber(lambda image: self.cam.put(image))
        # self.graph.add_null_render()
        # self.graph.prepare_preview_graph()
        # self.graph.run()
        self.cam = Camera(source)
        self.processor.set_cam(self.cam)

    def obtain_frame(self):

        self.cam.grab()
        try:
            return self.cam.buffer.get(block=True, timeout=1)
        except queue.Empty:
            raise IOError

    def track(self):
        while True:
            try:
                frame = self.obtain_frame()
                if frame is not None:
                    frame = self.processor.preprocess(frame)
                    status, buffer = cv2.imencode('.jpg', frame)
                    if status:
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except IOError:
                yield next(placeholder_stream)
