from queue import Queue
import bluetooth as bt
import socket
import sys
import subprocess
import json
from rpi_config import *

class AndroidInterface:
    """
    Represents the interface between the Raspberry Pi and an Android device over Bluetooth.

    Args:
    - RPiMain: Instance of the RPiMain class.

    Attributes:
    - RPiMain (RPiMain): Instance of the RPiMain class.
    - host (str): IP address of the Raspberry Pi.
    - uuid (str): Bluetooth UUID for the service.
    - msg_queue (Queue): Queue for storing messages.
    - socket (BluetoothSocket): Bluetooth socket for communication.
    - port (int): Port number for the socket connection.
    - client_socket (BluetoothSocket): Socket for communication with the connected Android device.
    - client_info (tuple): Information about the connected Android client.
    """
    def __init__(self, RPiMain):
        # Initialize AndroidInterface with RPiMain instance
        self.RPiMain = RPiMain
        self.host = RPI_IP
        self.uuid = BT_UUID
        self.msg_queue = Queue()

    def connect(self):
        # Grant permission for Bluetooth access
        subprocess.run("sudo chmod o+rw /var/run/sdp", shell=True) 

        # Establish and bind socket
        self.socket = bt.BluetoothSocket(bt.RFCOMM)
        print("[Android] BT socket established successfully.")
    
        try:
            self.port = self.socket.getsockname()[1]
            print("[Android] Waiting for connection on RFCOMM channel", self.port)
            self.socket.bind((self.host, bt.PORT_ANY))
            print("[Android] BT socket binded successfully.")
            
            # Turning advertisable
            subprocess.run("sudo hciconfig hci0 piscan", shell=True)
            self.socket.listen(128)
            
            # Advertise Bluetooth service
            bt.advertise_service(self.socket, "Group29-Server", service_id=self.uuid, service_classes=[self.uuid, bt.SERIAL_PORT_CLASS], profiles=[bt.SERIAL_PORT_PROFILE])

        except socket.error as e:
            print("[Android] ERROR: Android socket binding failed -", str(e))
            sys.exit()
            
        print("[Android] Waiting for Android connection...")

        try:
            self.client_socket, self.client_info = self.socket.accept()
            print("[Android] Accepted connection from", self.client_info)
            
        except socket.error as e:
            print("[Android] ERROR: connection failed -", str(e))

    def disconnect(self):
        # Close the Bluetooth socket
        try:
            self.socket.close()
            print("[Android] Disconnected from Android successfully.")
        except Exception as e:
            print("[Android] ERROR: Failed to disconnect from Android -", str(e))
            
    def reconnect(self):
        # Disconnect and then connect again
        self.disconnect()
        self.connect()

    def listen(self):
        # Continuously listen for messages from Android
        while True:
            try:
                message = self.client_socket.recv(BT_BUFFER_SIZE) 

                if not message:
                    print("[Android] Android disconnected remotely. Reconnecting...")
                    self.reconnect()

                decodedMsg = message.decode("utf-8")
                if len(decodedMsg) <= 1:
                    continue

                print("[Android] Read from Android:", decodedMsg[:MSG_LOG_MAX_SIZE])
                parsedMsg = json.loads(decodedMsg)
                msg_type = parsedMsg["type"]

                # Route messages to the appropriate destination
                if msg_type == 'NAVIGATION':
                    self.RPiMain.STM.msg_queue.put(message) 

                elif msg_type == 'START_TASK' or msg_type == 'FASTEST_PATH':
                    self.RPiMain.PC.msg_queue.put(message)

            
            except (socket.error, IOError, Exception, ConnectionResetError) as e:
                print("[Android] ERROR:", str(e))
                

    def send(self):
        # Continuously send messages to Android
        while True: 
            message = self.msg_queue.get()
            # Test code start
#             message_ori =   {
#                 "type": "IMAGE_RESULTS",
               # "data": {
                #"obs_id": "11", 
               # "img_id": "30", 
               # }
            #}
            # message = {
            #     "type": "NAVIGATION",
            #     "data": {
            #     "commands":  ["LF045", "RF045", "SF040", "RF045", "LF045"],
            #     # "commands": ["UF150"],

            #     "path": [[0,1], [1,1], [2,1], [3,1], [3,3]]
            #     }
            # }
            # message_ori = "hello from rpi"
#             message = json.dumps(message).encode("utf-8")
            # test code end

            exception = True
            while exception: 
                try:
                    self.client_socket.sendall(message)
                    print("[Android] Write to Android: " + message.decode("utf-8")[:MSG_LOG_MAX_SIZE])
                except Exception as e:
                    print("[Android] ERROR: Failed to write to Android -", str(e))
                    self.reconnect()  # reconnect and resend
                else:
                    exception = False  # done sending, get next message

