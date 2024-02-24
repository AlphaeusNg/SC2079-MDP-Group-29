import socket
import json
from queue import Queue
from image_recognition import check_image
import base64
from algo.pathfinding import task1
from algo.pathfinding import pathcommands

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
        self.msg_queue = Queue()
        self.send_message = False
        self.t1 = task1.task1()

    def connect(self):
        # Establish a connection with the PC
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.send_message = True
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
    
    def reconnect(self):
        # Disconnect and then connect again
        self.disconnect()
        self.connect()

    def send(self):
        while True:
            if self.send_message:
                message = self.msg_queue.get()
                exception = True
                while exception:
                    try:
                        # message_sized = self.prepend_msg_size(message)
                        self.client_socket.send(self.prepend_msg_size(message))
                        print("[PC Client] Write to RPI: first 100=", message[:100])
                        # self.send_message = False
                    except Exception as e:
                        print("[PC Client] ERROR: Failed to write to RPI -", str(e))
                        self.reconnect()
                    else:
                        exception = False
            
    def prepend_msg_size(self, message):
        message_bytes = message.encode("utf-8")
        message_len = len(message_bytes)
        length_bytes = message_len.to_bytes(4, byteorder="big")
        return length_bytes + message_bytes

    def receive_messages(self):
        try:
            image_id = 1
            while True:
                # Receive the length of the message
                length_bytes = self.receive_all(4)
                if not length_bytes:
                    print("[PC Server] Client disconnected.")
                    break
                message_length = int.from_bytes(length_bytes, byteorder="big")

                # Receive the actual message data
                message = self.receive_all(message_length)
                print("[PC Client] Received message: first 100:", message[:100])

                message = json.loads(message)
                if message["type"] == "START_TASK":
                    # Add algo implementation here:
                    self.t1.generate_path(message)
                    path_message = self.t1.get_command_to_next_obstacle() # get command to next, will pop from list automatically
                    # Test code below
                    # path_message = {"type": "NAVIGATION", "data": {"commands": ["LF180"], "path": [[1, 2], [1, 3], [1, 4], [1, 5], [2, 5], [3, 5], [4, 5]]}}
                    # End of test code
                    path_message = json.dumps(path_message)
                    self.msg_queue.put(path_message)
                
                elif message["type"] == "IMAGE_TAKEN":
                    # Add image recognition here:
                    encoded_image = message["data"]["image"]
                    decoded_image = base64.b64decode(encoded_image)
                    image_path = "captured_images/decoded_image.jpg"
                    with open(image_path, "wb") as img_file:
                        img_file.write(decoded_image)
                    
                    image_predictions = check_image.image_inference(image_path, obs_id=str(image_id)) #obs_id need to find out put what
                    image_id += 1
                    # image_predictions = check_image.test_image_inference(image_path, obs_id="1") #obs_id need to find out put what
                    if image_predictions['data']['img_id'] == None:
                        # if still no img_id, repeat
                        image_predictions['data']['img_id'] = "0" # just a last hail mary effort for the weakest prediction
                        
                    # For A.5
                    # else:
                    #      print("[Algo] Find the non-bulleye ended")
                    #      return
                    message = json.dumps(image_predictions)
                    self.msg_queue.put(message)
                    # For testing
                    # message = {"type": "IMAGE_RESULTS", "data": {"obs_id": "3", "img_id": "20"}}
                    # end of temp test code
                
                    # Update self.t1 to input new path, may put this above the image inference if we don't want to wait and stop
                    if not self.t1.has_task_ended():
                        command = self.t1.get_command_to_next_obstacle()
                        command = json.dumps(command)
                        self.msg_queue.put(command)
                    else:
                        print("[Algo] Task 1 ended")

        except socket.error as e:
            print("[PC Client] ERROR:", str(e))

    def receive_all(self, size):
        data = b""
        while len(data) < size:
            chunk = self.client_socket.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection closed unexpectedly")
            data += chunk
        return data

    


if __name__ == "__main__":
    client = PCClient()
    client.connect()
    
    PC_client_receive = threading.Thread(target=client.receive_messages, name="PC-Client_listen_thread")
    PC_client_send = threading.Thread(target=client.send, name="PC-Client_send_thread")

    PC_client_send.start()
    print("[PC Client] Sending threads started successfully")

    PC_client_receive.start()
    print("[PC Client] Listening threads started successfully")

    PC_client_receive.join()
    PC_client_send.join()
    print("[PC Client] All threads concluded, cleaning up...")
    
    # while True:
        # message = input("Enter message to send (or type 'quit' to exit): ")
        # if message.lower() == "quit":
        #     break
        # send_thread = threading.Thread(target=send_thread, args=(client, message))
        # send_thread.start()

    client.disconnect()
