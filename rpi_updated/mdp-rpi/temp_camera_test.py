"""
Just to test the individual image sending and receiving back via socket. Can delete once fully integrated
"""

import socket
from threading import Thread
from PC import PCInterface
import Camera
from queue import Queue
import socket
import json
from rpi_config import *

class PCInterface:
    def __init__(self, RPiMain):
        # Initialize PCInterface with RPiMain instance and connection details
        self.RPiMain = RPiMain
        self.host = RPI_IP
        self.port = PC_PORT
        self.client_socket = None
        self.msg_queue = Queue()
        self.send_message = False

    def connect(self):
        # Establish a connection with the PC
        if self.client_socket is not None:
            self.disconnect()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow the socket to be reused immediately after it is closed
                print("[PC] Socket established successfully.")
                sock.bind((self.host, self.port))
                sock.listen(128)

                print("[PC] Waiting for PC connection...")
                self.client_socket, self.address = sock.accept() #blocks until a client connects to the server
                self.send_message = True
        except socket.error as e:
            print("[PC] ERROR: Failed to connect -", str(e))
        else:
            print("[PC] PC connected successfully:", self.address)

    def disconnect(self):
        # Disconnect from the PC
        try:
            if self.client_socket is not None:
                self.client_socket.close()
                self.client_socket = None
                self.send_message = False
                print("[PC] Disconnected from PC successfully.")
        except Exception as e:
            print("[PC] Failed to disconnect from PC:", str(e))

    def reconnect(self):
        # Disconnect and then connect again
        self.disconnect()
        self.connect()

    def listen(self):
        # Continuously listen for messages from the PC
        while True:
            try:
                if self.client_socket is not None:
                    # Receive the length of the message
                    length_bytes = self.client_socket.recv(4)
                    if not length_bytes:
                        print("[PC] Client disconnected.")
                        break
                    message_length = int.from_bytes(length_bytes, byteorder="big")
                    
                    # Receive the message
                    message = self.client_socket.recv(message_length)

                    if not message:
                        self.send_message = False
                        print("[PC] PC disconnected remotely. Reconnecting...")
                        self.reconnect()

                    decoded_msg = message.decode("utf-8")
                    if len(decoded_msg) <= 1:
                        continue

                    print("[PC] Read from PC:", decoded_msg[:MSG_LOG_MAX_SIZE])
                    parsed_msg = json.loads(decoded_msg)
                    msg_type = parsed_msg["type"]

                    # Route messages to the appropriate destination
                    # PC -> Rpi -> STM
                    if msg_type == 'NAVIGATION': 
                        self.RPiMain.STM.msg_queue.put(message)
                    # PC -> Rpi -> Android
                    elif msg_type == 'IMAGE_RESULTS' or msg_type in ['COORDINATES', 'PATH']:
                        self.RPiMain.Android.msg_queue.put(message)
                    else:
                        print("[PC] ERROR: Received message with unknown type from PC -", message)
                else:
                    print("[PC Client] ERROR: Client socket is not initialized.")
                    return None

            except (socket.error, IOError, Exception, ConnectionResetError) as e:
                print("[PC] ERROR:", str(e))

    def send(self):
        # Continuously send messages to the PC
        # while True:
        for i in range(1):
            if self.send_message:
                # uncomment once ready
                # message = self.msg_queue.get()
                # message = message.decode("utf-8")
                # for testing
                message = Camera.get_image()
                exception = True
                while exception:
                    try:
                        self.client_socket.send(self.prepend_msg_size(message))
                        print("[PC] Write to PC:", message)
                        # self.send_message = False
                    except Exception as e:
                        print("[PC] ERROR: Failed to write to PC -", str(e))
                        self.reconnect()
                    else:
                        exception = False

    def prepend_msg_size(self, message):
        # message_bytes = message.encode("utf-8")
        message_len = len(message)
        length_bytes = message_len.to_bytes(4, byteorder="big")
        return length_bytes + message



class RPiMain:
    def __init__(self):
        # Initialize interfaces
        # self.Android = AndroidInterface(self)
        self.PC = PCInterface(self)
        # self.STM = STMInterface(self)

    def connect_components(self):
        # Connect all components
        # self.Android.connect()
        self.PC.connect()
        # self.STM.connect()

    def cleanup(self):
        pass
        # Disconnect from all components
        # self.Android.disconnect()
        self.PC.disconnect()
        # self.STM.disconnect()

    def run(self):
        print("[RPiMain] Starting RPiMain...")

        # Connect components
        self.connect_components()
        print("[RPiMain] Components connected successfully")

        # Create threads for sending messages
        # Android_send = Thread(target=self.Android.send, name="Android_send_thread")
        PC_send = Thread(target=self.PC.send, name="PC_send_thread")
        # STM_send = Thread(target=self.STM.send, name="STM_send_thread")

        # Create threads for receiving messages
        # Android_listen = Thread(target=self.Android.listen, name="Android_listen_thread")
        PC_listen = Thread(target=self.PC.listen, name="PC_listen_thread")

        # Start sending threads
        # Android_send.start()
        PC_send.start()
        # STM_send.start()
        print("[RPiMain] Sending threads started successfully")

        # Start listening threads
        # Android_listen.start()
        PC_listen.start()
        print("[RPiMain] Listening threads started successfully")

        # Wait for threads to end
        # Android_send.join()
        PC_send.join()
        # STM_send.join()
        # Android_listen.join()
        PC_listen.join()

        print("[RPiMain] All threads concluded, cleaning up...")

        # Cleanup after threads finish
        self.cleanup()

        print("[RPiMain] Exiting RPiMain...")

if __name__ == "__main__":
    # Create an instance of RPiMain and run it
    rpi = RPiMain()
    rpi.run()
