from queue import Queue
import time
import json
from picamera import PiCamera

import sys
sys.path.append("../rpi_mdp")
from stm import STMInterface
from rpi_config import *
from Camera import capture, preprocess_img

def get_image():
    # capture img to img_pth 
    img_pth = f"img_{round(time.time())}.jpg" 
    capture(img_pth)
    # preprocessing image
    preprocess_img(img_pth)
    print("IMAGE SAVED TO", img_pth, "(pretend sent to PC)")
 

def main():
    stm = STMInterface(None)
    stm.connect()
    while True: 
        command = input("Enter command: ").strip().upper()
        if command == "IMG":
            get_image()
        # elif command == "PARK":
        #     stm.return_to_carpark()
        elif stm.is_valid_command(command.upper()) or command in STM_OBS_ROUTING_MAP.keys():
            for c in stm.adjust_commands([command]):
                print("> Sending command:", c)
                stm.write_to_stm(c)
        else:
            print("> Invalid command. Please use specified format.")
main()