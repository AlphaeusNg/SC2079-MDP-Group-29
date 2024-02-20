import base64
import json
import os
from picamera import PiCamera
import cv2
import time
from datetime import datetime

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
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%H-%M-%S.%f')[:-3]
    img_pth = f"img_{formatted_time}.jpg"

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

# import picamera
# import time

# def capture_video(output_path, duration=10):
#     # Initialize the camera
#     with picamera.PiCamera() as camera:
#         # Set the resolution (adjust as needed)
#         camera.resolution = (640, 480)
        
#         # Start recording video
#         camera.start_recording(output_path)
        
#         # Record for the specified duration
#         camera.wait_recording(duration)
        
#         # Stop recording
#         camera.stop_recording()

# if __name__ == "__main__":
#     video_output_path = "output_video.h264"  # Change the file name or path as needed
#     video_duration = 10  # Duration of the video in seconds
    
#     capture_video(video_output_path, video_duration)
#     print(f"Video captured and saved to {video_output_path}")

