import socket
import json

# Constants
RPI_IP = "192.168.29.29"  # Replace with the Raspberry Pi's IP address
PC_PORT = 8888  # Replace with the port used by the PC server
PC_BUFFER_SIZE = 1024

import socket
import threading

class PCClient:
    def __init__(self):
        # Initialize PCClient with connection details
        self.host = RPI_IP
        self.port = PC_PORT
        self.client_socket = None

    def connect(self):
        # Establish a connection with the PC
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print("[PC Client] Connected to PC successfully.")
        except socket.error as e:
            print("[PC Client] ERROR: Failed to connect -", str(e))

    def disconnect(self):
        # Disconnect from the PC
        try:
            if self.client_socket is not None:
                self.client_socket.close()
                print("[PC Client] Disconnected from rpi.")
        except Exception as e:
            print("[PC Client] Failed to disconnect from rpi:", str(e))

    def send_message(self, message):
        try:
            if self.client_socket is not None:
                self.client_socket.sendall(self.prepend_msg_size(message))
                print("[PC Client] Message sent to rpi:", message)
            else:
                print("[PC Client] ERROR: Client socket is not initialized.")
        except Exception as e:
            print("[PC Client] ERROR: Failed to send message -", str(e))
            
    def prepend_msg_size(self, message):
        message_bytes = message.encode("utf-8")
        message_len = len(message_bytes)
        length_bytes = message_len.to_bytes(4, byteorder="big")
        return length_bytes + message_bytes

    def receive_messages(self):
        try:
            while True:
                # Receive the length of the message
                length_bytes = self.client_socket.recv(4)
                if not length_bytes:
                    print("[PC Server] Client disconnected.")
                    break
                message_length = int.from_bytes(length_bytes, byteorder="big")
                
                # Receive the message
                message = self.client_socket.recv(message_length).decode("utf-8")
                print("[PC Server] Received message:", message)
        except socket.error as e:
            print("[PC Server] ERROR:", str(e))

def send_message_thread(client, message):
    client.send_message(message)

if __name__ == "__main__":
    client = PCClient()
    client.connect()
    
    receive_thread = threading.Thread(target=client.receive_messages)
    receive_thread.start()
    
    while True:
        message = input("Enter message to send (or type 'quit' to exit): ")
        if message.lower() == "quit":
            break
        send_thread = threading.Thread(target=send_message_thread, args=(client, message))
        send_thread.start()

    client.disconnect()
