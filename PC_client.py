import os
import socket
import json
from queue import Queue
from image_recognition import check_image
import base64
from algo.pathfinding import task1
from algo.pathfinding import pathcommands
from datetime import datetime
import time

# Constants
RPI_IP = "192.168.29.29"  # Replace with the Raspberry Pi's IP address
PC_PORT = 8888  # Replace with the port used by the PC server
PC_BUFFER_SIZE = 1024
NUM_OF_RETRIES = 2

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
        self.image_record = []
        self.task_2 = False #TODO: Put True for task1, false for task2

    def connect(self):
        # Establish a connection with the PC
        retries:int = 0
        while not self.send_message:  # Keep trying until successful connection
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                self.send_message = True
                print("[PC Client] Connected to PC successfully.")
            except socket.error as e:
                retries += 1
                print("[PC Client] ERROR: Failed to connect -", str(e), "Retry no." + str(retries), "in 1 second...")
                time.sleep(1)

    def disconnect(self):
        # Disconnect from the PC
        try:
            if self.client_socket is not None:
                self.client_socket.close()
                self.send_message = False
                print("[PC Client] Disconnected from rpi.")
        except Exception as e:
            print("[PC Client] Failed to disconnect from rpi:", str(e))
    
    def reconnect(self):
        # Disconnect and then connect again
        print("[PC Client] Reconnecting...")
        self.send_message = False
        self.disconnect()
        self.connect()

    def send(self):
        while True:
            if self.send_message:
                message = self.msg_queue.get()
                exception = True
                while exception:
                    try:
                        self.client_socket.sendall(self.prepend_msg_size(message))
                        print("[PC Client] Write to RPI: first 100=", message[:100])
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
            image_counter = 0
            obs_id = 0
            retries = 0
            path_message = None
            while True:
                # Receive the length of the message
                length_bytes = self.receive_all(4)
                if not length_bytes:
                    print("[PC Client] PC Server disconnected.")
                    self.reconnect()
                message_length = int.from_bytes(length_bytes, byteorder="big")

                # Receive the actual message data
                message = self.receive_all(message_length)
                if not message:
                    print("[PC Client] PC Server disconnected remotely.")
                    self.reconnect()

                print("[PC Client] Received message: first 100:", message[:100])

                message = json.loads(message)
                if message["type"] == "START_TASK":
                    # Add algo implementation here:
                    self.t1.generate_path(message)
                    path_message = self.t1.get_command_to_next_obstacle() # get command to next, will pop from list automatically
                    obs_id = str(self.t1.get_obstacle_id())
                    # Test code below
                    # path_message = {"type": "NAVIGATION", "data": {"commands": ["LF180"], "path": [[1, 2], [1, 3], [1, 4], [1, 5], [2, 5], [3, 5], [4, 5]]}}
                    # End of test code
                    path_message_json = json.dumps(path_message)
                    self.msg_queue.put(path_message_json)

                elif message["type"] == "FASTEST_PATH":
                    path_message = {"type": "FASTEST_PATH"}
                    path_message_json = json.dumps(path_message)
                    self.msg_queue.put(path_message_json)
                
                elif message["type"] == "test":
                    message = {"type": "IMAGE_RESULTS", "data": {"obs_id": "3", "img_id": "39"}}
                    command = json.dumps(command)
                    self.msg_queue.put(command)

                elif message["type"] == "IMAGE_TAKEN":
                    # Add image recognition here:
                    encoded_image = message["data"]["image"]
                    decoded_image = base64.b64decode(encoded_image)
                    
                    image_path = f"captured_images/obs_id_{obs_id}_{image_counter}.jpg"
                    # os.makedirs(directory_path, exist_ok=True)
                    with open(image_path, "wb") as img_file:
                        img_file.write(decoded_image)

                    image_prediction = check_image.image_inference(image_path=image_path, obs_id=str(obs_id), image_id_map=self.t1.get_image_id(), task_2=self.task_2)
                    self.image_record.append(image_prediction)
                    image_counter += 1

                    if message["final_image"] == True:
                        
                        # image_prediction = check_image.get_highest_confidence(self.image_record)
                        # Get last prediction and move forward
                        while image_prediction['data']['img_id'] == None and self.image_record is not None:
                            if self.image_record:
                                image_prediction = self.image_record.pop()
                            else:
                                break

                        del image_prediction["data"]["bbox_area"]
                        del image_prediction["image_path"]
                        
                        # If still can't find a prediction, repeat the last command
                        if image_prediction['data']['img_id'] == None and NUM_OF_RETRIES > retries:
                            
                            if path_message['type'] == 'FASTEST_PATH':
                                image_prediction['data']['img_id'] = "38"
                            else:
                                last_command = path_message['data']['commands'][-1]
                                last_path = path_message['data']['path'][-1]
                                if "F" in last_command:
                                    command = {"type": "NAVIGATION", "data": {"commands": ['RF010','RB005'], "path": [last_path, last_path]}}
                                elif "B" in last_command:
                                    command = {"type": "NAVIGATION", "data": {"commands": ['RB010','RF005'], "path": [last_path, last_path]}}
                            
                                command = json.dumps(command)
                                self.msg_queue.put(command)
                                retries += 1
                                continue
                            
                        # # For checklist A.5
                        # else:
                        #     print("[Algo] Find the non-bulleye ended")
                        #     return

                        message = json.dumps(image_prediction)
                        self.msg_queue.put(message)
                        self.t1.update_image_id(image_prediction['data']['img_id'])
                        image_counter = 0
                        retries = 0

                        # For testing
                        # message = {"type": "IMAGE_RESULTS", "data": {"obs_id": "3", "img_id": "20"}}
                        # end of temp test code

                        # Update self.t1 to input new path, may put this above the image inference if we don't want to wait and stop
                        if not self.t1.has_task_ended():
                            command = self.t1.get_command_to_next_obstacle()
                            command = json.dumps(command)
                            self.msg_queue.put(command)
                            obs_id = str(self.t1.get_obstacle_id())
                        else:
                            print("[Algo] Task 1 ended")

                        self.image_record = [] # reset the image record

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
