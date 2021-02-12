from abc import abstractmethod


class Model:
    @abstractmethod
    def predict(self, image):
        pass
