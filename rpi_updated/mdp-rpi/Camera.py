import base64
import json
import os
from picamera import PiCamera
import cv2
import time

FOLDER_PATH = "/home/pi/Documents/SC2079-MDP-Group-29/rpi_updated/mdp-rpi/ImageCapture"
IMAGE_PREPROCESSED_FOLDER_PATH = "/home/pi/Documents/SC2079-MDP-Group-29/rpi_updated/mdp-rpi/ImagePreProcessed"

def capture(img_pth):
    # Capture image using PiCamera and save it to the specified path
    camera = PiCamera()
    print(img_pth)
    image_save_location = os.path.join(FOLDER_PATH, img_pth)
    camera.capture(image_save_location)
    camera.close()
    print("[Camera] Image captured")


def preprocess_img(img_pth):
    # Read image, resize it, and save the resized image
    image_save_location = os.path.join(FOLDER_PATH, img_pth)
    img = cv2.imread(image_save_location)

    resized_img = cv2.resize(img, (640, 480)) # (Width, Height) because we trained our dataset on 640x480 images

    image_save_location = os.path.join(IMAGE_PREPROCESSED_FOLDER_PATH, img_pth)
    cv2.imwrite(image_save_location, resized_img)
    print("[Camera] Image preprocessing complete")

def get_image():
    # Create a unique image path based on the current timestamp
    img_pth = f"img_{round(time.time())}.jpg"

    # Capture and preprocess the image
    capture(img_pth)
    preprocess_img(img_pth)

    # Construct a message with the encoded image
    encoded_string = ""
    image_save_location = os.path.join(IMAGE_PREPROCESSED_FOLDER_PATH, img_pth)
    if os.path.isfile(image_save_location):
        with open(image_save_location, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode('utf-8')

    # Create a JSON message containing the image data
    message = {
        "type": 'IMAGE_TAKEN',
        "data": {
            "image": encoded_string
        }
    }

    return json.dumps(message).encode("utf-8")
