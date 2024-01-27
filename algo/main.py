import constants as c
import sys

from connect.rpi_client import RPIClient


class Main:
    def __init__(self):
        self.client = None
        self.commands = None
        self.count = 0

    def connect(self):
        if self.client is None:
            print(f"Connecting to RPi@{c.RPI_HOST}:{c.RPI_PORT}")
            self.client = RPIClient(c.RPI_HOST, c.RPI_PORT)
            while True:
                try:
                    self.client.connect()
                    break
                except OSError:
                    pass
                except KeyboardInterrupt:
                    self.client.close()
                    sys.exit(1)
            print("Connected to RPi!\n")

    def test(self):
        self.client.send("123")
        message = self.client.recv(1024)
        print(message.decode("utf-8"))


if __name__ == "__main__":
    # Create an instance of Main
    main_instance = Main()

    # Test connection with RPI
    main_instance.connect()
    main_instance.test()
