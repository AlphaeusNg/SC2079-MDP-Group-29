import socket
import json

# Constants
RPI_IP = "192.168.29.29"  # Replace with the Raspberry Pi's IP address
PC_PORT = 8888  # Replace with the port used by the PC server
PC_BUFFER_SIZE = 1024

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

    def receive_message(self):
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

# Example usage:
if __name__ == "__main__":
    pc_client = PCClient()
    pc_client.connect()
    PC1_sample = {
        "type": "NAVIGATION",
        "data": {
        "commands": ["SF010", "RF090", "SB050", "LB090"],
        "path": [[0,1], [1,1], [2,1], [3,1]]
        }
    }
    PC2_sample = {
        "type": "IMAGE_RESULTS",
        "data": {
        "obs_id": "00", 
        "img_id": "36"
        }
    }
    PC1_json = json.dumps(PC1_sample)
    PC2_json = json.dumps(PC2_sample)
    # Send a message to the rpi
    pc_client.send_message(PC1_json)

    # Receive a message from the rpi
    received_message = pc_client.receive_message()
    pc_client.send_message(PC2_json)
    pc_client.disconnect()
