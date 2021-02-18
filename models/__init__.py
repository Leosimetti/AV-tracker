from abc import abstractmethod
import os


class Model:
    MODEL_PATH = os.path.dirname(__file__)

    @abstractmethod
    def predict(self, image):
        pass
