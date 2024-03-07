import json
from queue import Queue
import re
import threading
import time
import serial
from Camera import get_image
from rpi_config import *
import time

class STMInterface:
    def __init__(self, RPiMain):
        # Initialize STMInterface with necessary attributes
        self.RPiMain = RPiMain 
        self.baudrate = STM_BAUDRATE
        self.serial = None
        self.msg_queue = Queue()
        self.obstacle_count = 0 # Task 1 gyro reset
        # Task 2: return to carpark
        self.second_arrow = None
        self.xdist = None
        self.ydist = None

    def connect(self):
        # Connect to STM using available serial ports
        try:
            self.serial = serial.Serial("/dev/ttyUSB0", self.baudrate, write_timeout=0)
            print("[STM] Connected to STM 0 successfully.")
            self.clean_buffers()
        except:
            try:
                self.serial = serial.Serial("/dev/ttyUSB1", self.baudrate, write_timeout=0)
                print("[STM] Connected to STM 1 successfully.")
                self.clean_buffers()
            except Exception as e:
                print("[STM] ERROR: Failed to connect to STM -", str(e))
    
    def reconnect(self): 
        # Reconnect to STM by closing the current connection and establishing a new one
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
        self.connect()
    
    def clean_buffers(self):
        # Reset input and output buffers of the serial connection
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def listen(self):
        # Listen for messages from STM
        message = None
        while True:
            try:
                message = self.serial.read().decode("utf-8")
                print("[STM] Read from STM:", message[:MSG_LOG_MAX_SIZE])
                
                if len(message) < 1:
                    continue
                else: 
                    break

            except Exception as e:
                message = str(e)
                break

        return message
            
    def send(self):
        # Send commands to STM based on the received messages from PC
        self.obstacle_count = 1 # Task 1: Gyro reset
        # Task 2: return to carpark
        self.second_arrow = None
        self.xdist = None
        self.ydist = None
        while True: 
        # for i in range(1): 
            
            # Uncomment once implementation is done
            message_byte = self.msg_queue.get()
            message_str = message_byte.decode("utf-8")
            message = json.loads(message_str)
            message_type = message["type"]

            # comment once implementation is done.
            # message = {
            #     "type": "NAVIGATION",
            #     "data": {
            #     "commands":  ["SF010", "RF030", "LF030", "SF010"],
            #     # "commands":  ["SF030"],
            #     "path": [[0,1], [1,1], [2,1], [3,1]]
            #     }
            # }
            # message_type = 'NAVIGATION'
            # end of test code

            if message_type == "NAVIGATION":
                # Display path on Android
                self.send_path_to_android(message) 

                # Convert/adjust turn or obstacle routing commands
                commands = self.adjust_commands(message["data"]["commands"])

                # Real code
                for idx, command in enumerate(commands):
                    # Capture an image before every instruction
                    if idx >= len(commands) - NUM_IMAGES:
                        # Start a new thread to capture and send the image to PC
                        capture_and_send_image_thread = threading.Thread(target=self.send_image_to_pc(final_image=False), daemon=True)
                        capture_and_send_image_thread.start()

                    self.write_to_stm(command)
                    print("[RPI] Writing to STM:", command)
                    

                if self.second_arrow is not None:
                    self.return_to_carpark()
                    print("[STM] DONE")
                    return

                # Start a new thread to capture and send the image to PC
                capture_and_send_image_thread = threading.Thread(target=self.send_image_to_pc(final_image=True), daemon=True)
                capture_and_send_image_thread.start()

                self.obstacle_count += 1
                
                # Was previously in the code when we ran on 23/2/24, but may not be necessary?
                if self.obstacle_count % STM_GYRO_RESET_FREQ == 0:
                    print("[STM] Resetting gyroscope after %d obstacles" % self.obstacle_count)
                    self.write_to_stm(STM_GYRO_RESET_COMMAND)
            else:
                print("[STM] WARNING: Rejecting message with unknown type [%s] for STM" % message_type)

    def write_to_stm(self, command):
        # Write a command to STM, handling exceptions and reconnecting if necessary
        self.clean_buffers()
        if self.is_valid_command(command):
            exception = True
            while exception:
                try:
                    print("[STM] Sending command", command)
                    encoded_string = command.encode()
                    byte_array = bytearray(encoded_string)
                    self.serial.write(byte_array)
                except Exception as e:
                    print("[STM] ERROR: Failed to write to STM -", str(e)) 
                    exception = True
                    self.reconnect() 
                else:
                    exception = False
                    if command == STM_GYRO_RESET_COMMAND:
                        print("[STM] Waiting %ss for reset" % STM_GYRO_RESET_DELAY)
                        time.sleep(STM_GYRO_RESET_DELAY)
                    elif re.match(STM_XDIST_COMMAND_FORMAT, command):
                        dist = self.wait_for_dist()
                        if dist >= 0: 
                            self.xdist = dist
                            print("[STM] updated XDIST =", self.xdist)
                        else:
                            print("[STM] ERROR: failed to update XDIST, received invalid value:", dist)
                    elif re.match(STM_YDIST_COMMAND_FORMAT, command):
                        dist = self.wait_for_dist()
                        if dist >= 0: 
                            self.ydist = dist
                            print("[STM] updated YDIST =", self.ydist)
                        else:
                            print("[STM] ERROR: failed to update YDIST, received invalid value:", dist)
                    else:
                        print("[STM] Waiting for ACK")
                        self.wait_for_ack()
        else:
            print(f"[STM] ERROR: Invalid command to STM [{command}]. Skipping...")

    def wait_for_ack(self):
        # Wait for ACK message from STM
        message = self.listen()
        print(message)
        if message  == STM_ACK_MSG:
            print("[STM] Received ACK from STM") 
        else:
            print("[STM] ERROR: Unexpected message from STM -", message)
            self.reconnect() 

    def wait_for_dist(self):
        # Wait for distance measurement from STM
        distance = "0"
        for _ in range(3):  # expecting 3 digit distance in cm
            message = self.listen()
            if message.isnumeric(): 
                distance += message
            else: 
                print(f"[STM] ERROR: Unexpected message from STM while getting distance - {message}")
                self.reconnect() 
        distance = int(distance)
        print(f"[STM] Read final DIST =", distance) 
        return distance

    def send_image_to_pc(self, final_image:bool):
        # Send captured image to PC
        print("[STM] Adding image from camera to PC message queue")
        self.RPiMain.PC.msg_queue.put(get_image(final_image=final_image))      

    def send_path_to_android(self, message):
        # Send path to Android for display
        if "path" not in message["data"]:
            print("[STM] No path found in NAVIGATION message")  
        try: 
            path_message = self.create_path_message(message["data"]["path"])
            self.RPiMain.Android.msg_queue.put(path_message)
            print("[STM] Adding NAVIGATION path from PC to Android message queue")
        except:
            print("[STM] ERROR with path found in NAVIGATION message")    

    def is_valid_command(self, command):
        # Hard-coded portion for the angle, if the manual correction is not working, then uncomment this
        
        # Check if a command is valid according to the defined format
         if re.match(STM_NAV_COMMAND_FORMAT, command) or command == STM_GYRO_RESET_COMMAND:
             return True
         else:
             return False
    

    def adjust_commands(self, commands):
        # Adjust and combine commands for smoother execution
        def is_turn_command(command):
            return self.is_valid_command(command) and re.match("^[LR]", command)

        def adjust_turn_command(turn_command):
            return STM_COMMAND_ADJUSTMENT_MAP.get(turn_command, turn_command)
            # return True

        def is_obstacle_routing_command(command):
            return command in STM_OBS_ROUTING_MAP.keys()

        def adjust_obstacle_routing_command(obs_routing_command):
            if obs_routing_command.startswith("SECOND"):
                self.second_arrow = obs_routing_command[len("SECOND")]
                print("[STM] Saving second arrow as", self.second_arrow)
            return STM_OBS_ROUTING_MAP[obs_routing_command]
        
        def is_straight_command(command):
            return self.is_valid_command(command) and command.startswith("S")

        def is_validturn_command(command):
           return self.is_valid_command(command) and command.startswith("R") or command.startswith("L")

        def combine_straight_commands(straight_commands):
            dir_dict = {"SF": 1, "SB": -1} 
            total = 0
            for c in straight_commands:
                dir = c[:2]
                val = int(c[2:])
                total += dir_dict.get(dir, 0) * val
            
            if total > 0:
                return "SF%03d" % abs(total)
            elif total < 0:
                return "SB%03d" % abs(total)
            else:
                return None

        def add_command(final, new):
            if is_straight_command(new) and (len(final) > 0 and is_straight_command(final[-1])):
                prev = final.pop(-1)
                combined = combine_straight_commands([prev, new])
                if combined is not None:
                    final.append(combined)
                else:
                    final.append(prev)
                    final.append(new)
            else:
                final.append(new)
            
            return final

        final_commands = []     
        for i in range(len(commands)):
            command = commands[i].upper()
            #if is_straight_command(command):
            if True:
                final_commands = add_command(final_commands, command)
            else:
                adj_commands = []
                if is_turn_command(command): 
                    adj_commands = adjust_turn_command(command)
                # Just added to check it: 
                # if is_validturn_command(command):
                #    adj_commands = adjust_turn_command(command)
                elif is_obstacle_routing_command(command): 
                    adj_commands = adjust_obstacle_routing_command(command)
                else:
                    final_commands = add_command(final_commands, command)
                for c in adj_commands:
                    final_commands = add_command(final_commands, c)
        return final_commands

    def create_path_message(self, path):
        # Create a JSON-encoded message for path information
        message = {
            "type": "PATH",
            "data": {
                "path": path
            }
        }
        return json.dumps(message).encode("utf-8")
    
    # Task 2: Fastest car
    def return_to_carpark(self):
        # Execute the return to carpark procedure based on the obtained information
        print(f"[STM] Initiating return to carpark: XDIST = {self.xdist}, YDIST = {self.ydist}, ARROW = {self.second_arrow}")
        commands = self.get_commands_to_carpark()
        for command in commands:
            self.write_to_stm(command)  

    def get_commands_to_carpark(self):
        # Calculate the path to return to the carpark based on the obtained information
        print(f"[STM] Calculating path to carpark...")
        movement_list = []
        x_adjustment = (self.xdist) // 2 - 25 
        y_adjustment = self.ydist + 80 

        movement_list.append(f"SF{y_adjustment:03d}")
        if self.second_arrow == 'R':
            movement_list.append("LF090")
            if x_adjustment > 0:
                movement_list.append(f"SF{x_adjustment:03d}")
            else:
                movement_list.append(f"SB{abs(x_adjustment):03d}")
            movement_list.append("RF090")
            movement_list.append("VF200") 
        elif self.second_arrow == 'L':
            movement_list.append("RF090")
            if x_adjustment > 0:
                movement_list.append(f"SF{x_adjustment:03d}")
            else:
                movement_list.append(f"SB{abs(x_adjustment):03d}")
            movement_list.append("LF090")
            movement_list.append("VF200") 
        else:
            print("[STM] ERROR getting path to carpark, second arrow invalid -", self.second_arrow)
        
        print("[STM] Final path to carpark:", movement_list)
        return movement_list
