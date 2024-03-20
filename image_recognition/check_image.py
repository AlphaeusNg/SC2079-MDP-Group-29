from ultralytics import YOLO
from pathlib import Path
import os
from typing import List
import time
from datetime import datetime
import torch

TASK_1_MODEL_PATH = Path("image_recognition") / "runs" / "detect" / "train (old + current + MDP CV.v8)" / "weights" / "best.pt"
TASK_2_MODEL_PATH = Path("image_recognition") / "runs" / "detect" / "train task_2" / "weights" / "best.pt"
FOREIGN_AID_MODEL_PATH = Path("image_recognition") / "ImageRecNew-main" / "YoloV8 Inference Server" / "Weights" / "bestv2.pt"

# Check if GPU is available and move the model to the device
device = 'cuda' if torch.cuda.is_available() else 'cpu'


def map_yoloid_to_mdp_image_id(yoloid: int) -> str:
    # a function that checks the yoloid and returns the corresponding MDP image id, the given yoloid to MDP image id mapping is as follows:
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


def predict_multiple_images(folder_path, model):

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
        model.predict(file, save=True, imgsz=640, conf=0.8, device=device)


def find_largest_bbox_label(bboxes):

    largest_bbox_area = 0.0
    largest_bbox_label = None

    for bbox in bboxes: 
        
        # Extract label, x, y, width, height
        label = bbox['label']
        x, y, width, height = bbox['xywh']

        # ignore bullseye      
        if label == "0":
            continue  
        # factor in '1' being thinner
        if label == "11":
            width *= 1.2

        # Calculate the area of the bounding box
        bbox_area = width * height

        # Check if the current bounding box has a larger area
        if bbox_area > largest_bbox_area:
            largest_bbox_area = bbox_area
            largest_bbox_label = label

    return largest_bbox_label, largest_bbox_area


def get_highest_confidence(predictions_list:list[dict]) -> dict:
    if not predictions_list:
        return None  # Return None if the list is empty

    max_confidence = float('-inf')  # Start with a very low value
    highest_conf_pred = None

    for prediction in predictions_list:
        conf = prediction["data"].get("conf", 0)
        if conf > max_confidence:
            max_confidence = conf
            highest_conf_pred = prediction

    return highest_conf_pred


def image_inference(image_path, obs_id, image_id_map:list[str], task_2:bool=True):
    # Create a unique image path based on the current timestamp (and also check the delay)
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"img_{formatted_time}"

    # Initialize the YOLO model
    if not task_2:
        model = YOLO(TASK_1_MODEL_PATH)
    else:
        model = YOLO(TASK_2_MODEL_PATH)
    model.to(device)

    # run inference on the image
    results = model.predict(source=image_path, verbose=False, project="./captured_images", name=f"{img_name}", save=True, save_txt=True, save_conf=True, imgsz=640, conf=0.8, device=device)
    bboxes = []

    for r in results:
        # Iterate over each object
        for c in r:
            label = c.names[c.boxes.cls.tolist().pop()].split("_")[0]
            # If label previously detected, skip
            if label in image_id_map and not task_2:
                continue
            bboxes.append({"label": label, "xywh": c.boxes.xywh.tolist().pop()})
            # print(bboxes)

    # To make it display, useful for testing
    # results[0].show()

    largest_bbox_label, largest_bbox_area = find_largest_bbox_label(bboxes)

    image_prediction = {
        "type": "IMAGE_RESULTS",
        "data": {
            "obs_id": obs_id, 
            "img_id": largest_bbox_label, 
            "bbox_area": largest_bbox_area
            },
        "image_path": Path("captured_images") / img_name
        }

    return image_prediction

    
if __name__ == '__main__':
    # folder_path = r"image recognition\dataset\MDP CV.v7i.yolov8"
    # predict_multiple_images(folder_path)
    # image_path = r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\obs_id_5_1.jpg"
    # image_path = r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\captured_images\obs_id_6_1.jpg"
    image_path = r"C:\Users\kelvi\Desktop\MDP29\SC2079-MDP-Group-29\captured_images\obs_id_0_0.jpg"
    _ = image_inference(image_path, "00")