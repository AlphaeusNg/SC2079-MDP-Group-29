from ultralytics import YOLO
from config import MODEL_PATH
import os

# Load a pretrained YOLOv8n model
model = YOLO(MODEL_PATH)

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


def predict_single_image(image_path):
    # Define path to the image file
    source = image_path

    # Run inference on an image
    results = model(source)  # results list

    # View results
    for r in results:
        print(r.boxes)  # print the Boxes object containing the detection bounding boxes
        
    
if __name__ == '__main__':
    folder_path = r"image recognition\dataset\MDP CV.v7i.yolov8"
    # predict_multiple_images(folder_path)
    predict_single_image(r"image recognition\dataset\MDP CV.v7i.yolov8\test\images\20240202_112633_jpg.rf.6656a124bb3d9b05821810cb27bd8ebc.jpg")