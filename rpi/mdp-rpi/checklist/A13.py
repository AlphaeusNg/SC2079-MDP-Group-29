# Test USB connection to STM

import serial
import re

class STMInterface:
    def __init__(self):
        self.baudrate = 115200
        self.serial = 0
        self.connected = False

    def connect(self):    
        try:
            #Serial COM Configuration
            self.serial = serial.Serial("/dev/ttyUSB0", self.baudrate, write_timeout = 0)
            self.connected = True
            print("Connected to STM 0 successfully.")
        except:
            try:
                self.serial = serial.Serial("/dev/ttyUSB1", self.baudrate, write_timeout = 0)
                self.connected = True
                print("Connected to STM 1 successfully.")
            except Exception as e:
                print("Failed to connect to STM: %s" %str(e))

    def wait_for_ACK(self):        
        while True:
            print("Waiting for ACK from STM...")
            try:
                print("reached here")
                message = self.serial.read()
                print('Read from STM: %s' %str(message))
                message = str(message)
                length = len(message)
                
                if length <= 1:
                    continue
                if "A" in message:
                    break

            except Exception as e:
                print("Failed to read from STM: %s" %str(e))
                return
        
    def send(self, encoded_msg):
        try:
            print(encoded_msg)
            self.serial.write(encoded_msg) 
#            print("Write to STM: " + encoded_msg)
        except Exception as e:
            print("Failed to write to STM: %s" %str(e))
            
def main():
    stm = STMInterface()
    stm.connect()
    # for command in ["SF030", "RF090", "SB030", "LF090", "SF020"]:
    while True: 
        command = input("Enter command: ").strip().upper()
        if re.match('^[SLR][FB][0-9]{3}$', command):
#            print("Sending command:", command)
            stm.send(bytearray(command.encode()))
        else:
            print("Invalid command. Please use format <L/R/S><F/B>XXX.")
#main()
