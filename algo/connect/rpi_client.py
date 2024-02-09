import socket


class RPIClient:
    """
    Used for connecting to RPI as client
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_message(self, obj):
        for command in obj:
            self.socket.send(command.encode("utf-8"))

    def receive_message(self):
        data = self.socket.recv(1024)
        if not data:
            return False
        return data

    def close(self):
        self.socket.close()
    