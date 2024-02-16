import base64
import json
import os
from picamera import PiCamera
import cv2
import time

def capture(img_pth):
    # Capture image using PiCamera and save it to the specified path
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.capture(img_pth)
    camera.close()
    print("[Camera] Image captured")

def preprocess_img(img_pth):
    # Read image, resize it, and save the resized image
    img = cv2.imread(img_pth)
    new_width, new_height = 640, 480 # because we trained our dataset on 640x480 images
    resized_img = cv2.resize(img, (new_width, new_height))
    cv2.imwrite(img_pth, resized_img)
    print("[Camera] Image preprocessing complete")

def get_image():
    # Create a unique image path based on the current timestamp
    img_pth = f"img_{round(time.time())}.jpg"

    # Capture and preprocess the image
    capture(img_pth)
    # preprocess_img(img_pth)

    # Construct a message with the encoded image
    encoded_string = ""
    if os.path.isfile(img_pth):
        with open(img_pth, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode('utf-8')

    # Create a JSON message containing the image data
    message = {
        "type": 'IMAGE_TAKEN',
        "data": {
            "image": encoded_string
        }
    }

    return json.dumps(message).encode("utf-8")
