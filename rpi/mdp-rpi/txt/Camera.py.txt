import base64
import json
import os
from picamera import PiCamera
import cv2
import time

def capture(img_pth):
    camera = PiCamera()
    camera.capture(img_pth)
    camera.close()
    print("[Camera] Image captured")

def preprocess_img(img_pth):
    img = cv2.imread(img_pth)
    resized_img = cv2.resize(img, (800,800))
    cv2.imwrite(img_pth, resized_img)
    print("[Camera] Image preprocessing complete")

def get_image():
    # capture img to img_pth 
    img_pth = f"img_{round(time.time())}.jpg" 
    capture(img_pth)
    # preprocessing image
    preprocess_img(img_pth)
                
    # construct image
    encoded_string = ""
    if os.path.isfile(img_pth):
        with open(img_pth, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode('utf-8')

    message = {
        "type": 'IMAGE_TAKEN',
        "data":{
            "image": encoded_string
            }
        }
    
    return json.dumps(message).encode("utf-8")

