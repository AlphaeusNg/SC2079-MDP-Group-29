from ultralytics import YOLO
from pathlib import Path
import os
from typing import List
import time
from datetime import datetime
import torch

# Add your model paths here
TASK_1_V1_MODEL_CONFIG = {"conf":0.803, "path":Path("image_recognition") / "runs" / "detect" / "train (old + current + MDP CV.v8)" / "weights" / "best.pt"}
TASK_1_V2_MODEL_CONFIG = {"conf":0.791, "path":Path("image_recognition") / "runs" / "detect" / "train task_1" / "weights" / "best.pt"}
TASK_2_MODEL_CONFIG = {"conf":0.868, "path":Path("image_recognition") / "runs" / "detect" / "train task_2" / "weights" / "best.pt"}

# Check if GPU is available and move the model to the device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

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
        label = bbox['label']
        _, _, width, height = bbox['xywh']

        # ignore bullseye      
        if label == "0":
            continue  
        # factor in '1' being thinner
        if label == "11":
            width *= 1.2

        bbox_area = width * height
        if bbox_area > largest_bbox_area:
            largest_bbox_area = bbox_area
            largest_bbox_label = label

    return largest_bbox_label, largest_bbox_area


def image_inference(image_or_path, obs_id, image_counter, image_id_map:list[str], task_2:bool=True):
    # Create a unique image path based on the current timestamp (and also check the delay)
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"img_{formatted_time}"
    largest_bbox_area_2 = None
    model_2 = None
    # Initialize the YOLO model
    if not task_2:
        model = YOLO(TASK_1_V1_MODEL_CONFIG["path"]) # The better model.
        conf = TASK_1_V1_MODEL_CONFIG["conf"]
        model_2 = YOLO(TASK_1_V2_MODEL_CONFIG["path"]) # Backup 2nd model.
        conf_2 = TASK_1_V2_MODEL_CONFIG["conf"]
    else:
        model = YOLO(TASK_2_MODEL_CONFIG["path"]) # The better model.
        conf = TASK_2_MODEL_CONFIG["conf"]
        model_2 = YOLO(TASK_1_V2_MODEL_CONFIG["path"]) # # Backup 2nd model.
        conf_2 = TASK_1_V2_MODEL_CONFIG["conf"]

    model.to(device)
    # run inference on the image
    results = model.predict(source=image_or_path, verbose=False, project="./captured_images", name=f"{img_name}_1", save=True, save_txt=True, save_conf=True, imgsz=640, conf=conf, device=device)
    bboxes = []
    
    for r in results:
        for c in r:
            label = c.names[c.boxes.cls.tolist().pop()].split("_")[0] # First model label name
            # If label previously detected, skip
            if label in image_id_map and not task_2:
                continue
            bboxes.append({"label": label, "xywh": c.boxes.xywh.tolist().pop()})
    # To make it display, useful for testing
    # results[0].show()

    largest_bbox_label, largest_bbox_area = find_largest_bbox_label(bboxes)

    # If no label picked up, run backup model
    if largest_bbox_label is None and model_2:
        model_2.to(device)
        bboxes_2 = []
        results_2 = model_2.predict(source=image_or_path, verbose=False, project="./captured_images", name=f"{img_name}_2", save=True, save_txt=True, save_conf=True, imgsz=640, conf=conf_2, device=device)
        
        for r2 in results_2:
        # Iterate over each object
            for c2 in r2:
                label = c2.names[c2.boxes.cls.tolist().pop()][0:2] # 2nd model label name
                if label[0]=="0":
                    label = label[0]
                # If label previously detected, skip
                if label in image_id_map and not task_2:
                    continue
                bboxes_2.append({"label": label, "xywh": c2.boxes.xywh.tolist().pop()})
        
        largest_bbox_label_2, largest_bbox_area_2 = find_largest_bbox_label(bboxes_2)

    # take model 1 if there is results, since it's better.
    if largest_bbox_area:
        img_name = img_name + "_1"
    else:
        largest_bbox_label = largest_bbox_label_2
        largest_bbox_area = largest_bbox_area_2
        img_name = img_name + "_2"

    if task_2:
        name_of_image = f"task2_obs_id_{obs_id}_{image_counter}.jpg"
    else:
        name_of_image = f"task1_obs_id_{obs_id}_{image_counter}.jpg"

    image_prediction = {
        "type": "IMAGE_RESULTS",
        "data": {
            "obs_id": obs_id, 
            "img_id": largest_bbox_label, 
            "bbox_area": largest_bbox_area
            },
        "image_path": Path("captured_images") / img_name / name_of_image
        }

    return image_prediction

    
if __name__ == '__main__':
    current_dir = Path(__file__).resolve().parent
    image_path = Path("captured_images") / "obs_id_00_1.jpg"
    # folder_path = Path("image recognition") / "dataset" / "MDP CV.v7i.yolov8"
    # predict_multiple_images(folder_path)
    _ = image_inference(image_path, "00", [])