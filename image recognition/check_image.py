from ultralytics import YOLO
import os

def extract_jpg_files(folder_path):
    jpg_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".jpg"):
                jpg_files.append(os.path.join(root, file))
    return jpg_files

# Replace 'your_folder_path' with the path to your target folder
folder_path = r"image recognition\dataset\MDP CV.v7i.yolov8"
jpg_files_list = extract_jpg_files(folder_path)

# Display the list of JPG files
print("List of JPG files:")
for jpg_file in jpg_files_list:
    print(jpg_file)


# Load a pretrained YOLOv8n model
model = YOLO(r"image recognition\runs\detect\train (train2 + MDP CV.v7)\weights\best.pt")

# Define path to the image file
source = jpg_files_list

# Run inference on 'bus.jpg' with arguments
for file in source:
    model.predict(file, save=True, imgsz=640, conf=0.8, device='cuda')

# Run inference on an image
# results = model(source)  # results list
#
# # View results
# for r in results:
#     print(r.boxes)  # print the Boxes object containing the detection bounding boxes