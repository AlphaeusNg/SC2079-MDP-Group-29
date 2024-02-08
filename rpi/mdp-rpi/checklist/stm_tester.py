# for testing: sending commands to STM with adjustment for turning radius 3 * 10cm
# A13.py sends commands with no adjustments and no wait for ACK

import sys
sys.path.append("../rpi_mdp")
from stm import STMInterface
from rpi_config import *

stm = STMInterface(None)
stm.connect()

while True: 
    command = input("Enter command: ").strip().upper()
    if stm.is_valid_command(command):
        for c in stm.adjust_command(command):
            print("> Sending command:", c)
            stm.serial.write(bytearray(c.encode()))
            message = stm.listen()
            print(">>> Received:", message)
    else:
        print("> Invalid command. Please use format <L/R/S><F/B>XXX.")
