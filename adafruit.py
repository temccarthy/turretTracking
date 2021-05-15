import Adafruit_IO as ada


class Fruit:
    def __init__(self, file_name):
        with open(file_name) as f:
            creds = f.readline()
            print(creds)
            self.aio = ada.Client(creds)

    def get_next(self):
        try:
            return self.aio.receive_next(u'Turret').value
        except ada.errors.RequestError:
            return None
