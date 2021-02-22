from flask import Flask, Response, stream_with_context, render_template
from flaskwebgui import FlaskUI  # get the FlaskUI class
import time


# http://fm.1tvcrimea.ru:8000/stream.mp3

# http://91.219.74.220:8000/Vanya-high.mp3

class WebWindow:
    def __init__(self):
        self.open = True
        self.msg = "sas"


    def create_window(self):

        app = Flask(__name__)

        # Feed it the flask app instance
        ui = FlaskUI(app)

        def sas():
            self.open = False
            exit()

        ui.on_exit = sas

        @app.route('/')
        def stream():
            return render_template("base.html")


        @app.route("/exit", methods=['POST'])
        def leave():
            self.open = False
            # Moving forward code
            # forward_message = "Exitting..."
            exit()

        # call the 'run' method
        ui.run()
