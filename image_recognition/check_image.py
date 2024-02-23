from ultralytics import YOLO
from pathlib import Path
import cv2 as cv
import numpy as np
import os
from typing import List
import time
from datetime import datetime

# Load a pretrained YOLOv8n model
MODEL_PATH = r"image_recognition\runs\detect\train (old + current + MDP CV.v8)\weights\best.pt"
model = YOLO(MODEL_PATH)


def map_yoloid_to_mdp_image_id(yoloid: int) -> str:
    # Code out a function that checks the yoloid and returns the corresponding MDP image id, the given yoloid to MDP image id mapping is as follows:
    return {
        0: '0_BullsEye',
        1: '11_1',
        2: '12_2',
        3: '13_3',
        4: '14_4',
        5: '15_5',
        6: '16_6',
        7: '17_7',
        8: '18_8',
        9: '19_9',
        10: '20_A',
        11: '21_B',
        12: '22_C',
        13: '23_D',
        14: '24_E',
        15: '25_F',
        16: '26_G',
        17: '27_H',
        18: '28_S',
        19: '29_T',
        20: '30_U',
        21: '31_V',
        22: '32_W',
        23: '33_X',
        24: '34_Y',
        25: '35_Z',
        26: '36_Up',
        27: '37_Down',
        28: '38_Right',
        29: '39_Left',
        30: '40_Stop'
    }[yoloid]


def predict_multiple_images(folder_path):

    def extract_jpg_files(folder_path):
        jpg_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".jpg"):
                    jpg_files.append(os.path.join(root, file))
        return jpg_files

    # Replace 'your_folder_path' with the path to your target folder
    
    jpg_files_list = extract_jpg_files(folder_path)

    # Display the list of JPG files
    print("List of JPG files:")
    for jpg_file in jpg_files_list:
        print(jpg_file)    

    # Define path to the image file
    source = jpg_files_list

    # Run inference on 'bus.jpg' with arguments
    for file in source:
        model.predict(file, save=True, imgsz=640, conf=0.8, device='cuda')


def find_largest_bbox_label(bboxes):

    largest_bbox_area = 0
    largest_bbox_label = None

    for bbox in bboxes:            
        # Extract label, x, y, width, height
        label = bbox['label']
        x, y, width, height = bbox['xywh']
        conf = bbox['conf']

        # Calculate the area of the bounding box
        bbox_area = width * height

        # Check if the current bounding box has a larger area
        if bbox_area > largest_bbox_area:
            largest_bbox_area = bbox_area
            largest_bbox_label = label

    return largest_bbox_label


def image_inference(image_path, obs_id):
    # Create a unique image path based on the current timestamp (and also check the delay)
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"img_{formatted_time}"
    # run inference on the image
    results = model.predict(source=image_path, project="./captured_images", name=f"{img_name}", save=True, save_txt=True, save_conf=True, imgsz=640, conf=0.8, device='cuda')
    # results = model.predict(source=image_path,imgsz=640, conf=0.8, device='cuda')
    bboxes = []
    for r in results:
        # Iterate over each object
        for c in r:
            bboxes.append({"label": c.names[c.boxes.cls.tolist().pop().split("_")[0]], 
                           "conf": c.boxes.conf.tolist().pop(), 
                           "xywh": c.boxes.xywh.tolist().pop()})
            # file_path = rf"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\{img_name}"

            # Save the image to the specified path
            # r.orig_img.save(file_path+".jpg")
            # with open(file_path+".txt", 'w') as output_file:
            #     for value in c.boxes.xywhn.tolist().pop():
            #         output_file.write(f"{value} ")

    # To make it display, useful for testing
    # results[0].show()

    largest_bbox_label = find_largest_bbox_label(bboxes)

    image_prediction = {
        "type": "IMAGE_RESULTS",
        "data": {
            "obs_id": obs_id, 
            "img_id": largest_bbox_label, 
            }
        }

    return image_prediction

def test_image_inference(image_path, obs_id):
    # Create a unique image path based on the current timestamp (and also check the delay)
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"img_{formatted_time}"
    # run inference on the image
    results = model.predict(source=r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\img_23-02_12-34-08.262\decoded_image.jpg",imgsz=640, conf=0.8, device='cuda')
    bboxes = []
    for r in results:
        # Iterate over each object
        for c in r:
            bboxes.append({"label": c.names[c.boxes.cls.tolist().pop()], 
                        "conf": c.boxes.conf.tolist().pop(), 
                        "xywh": c.boxes.xywh.tolist().pop()})
            file_path = rf"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\{img_name}"

            # Save the image to the specified path
            r.orig_img.save(file_path+".jpg")
            with open(file_path+".txt", 'w') as output_file:
                for value in c.boxes.xywhn.tolist().pop():
                    output_file.write(f"{value} ")

    # To make it display, useful for testing
    # results[0].show()

    largest_bbox_label = find_largest_bbox_label(bboxes)

    image_prediction = {
        "type": "IMAGE_RESULTS",
        "data": {
            "obs_id": obs_id, 
            "img_id": largest_bbox_label, 
            }
        }

    return image_prediction


    
if __name__ == '__main__':
    folder_path = r"image recognition\dataset\MDP CV.v7i.yolov8"
    # predict_multiple_images(folder_path)
    _ = image_inference(r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\img_10-24-33.134\decoded_image.jpg", "00")