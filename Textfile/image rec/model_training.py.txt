from ultralytics import YOLO
import torch

def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # Load a model
    model = YOLO("yolov8n.pt")
    # model = YOLO(r"image_recognition\runs\detect\train task_1\weights\best.pt")
    model.train(
        # resume=True,
        seed=42,
        data=r"image_recognition\dataset\MDP Image Recognition V4.v1i.yolov8\data.yaml",
        imgsz=640,
        batch=16,
        epochs=300,
        patience=50,
        device=device,
        name="train task_1")  # train the model

    metrics = model.val(
        name="valid task_1",
        device=device,
        plots=True
    )  # evaluate model performance on the validation set

    model = YOLO("yolov8n.pt")
    # model = YOLO(r"image_recognition\runs\detect\train task_2\weights\best.pt")
    model.train(
        # resume=True,
        seed=42,
        data=r"image_recognition\dataset\MDP_Task2.v6i.yolov8\data.yaml",
        imgsz=640,
        batch=16,
        epochs=300,
        patience=50,
        device=device,
        name="train task_2")  # train the model

    metrics = model.val(
        name="valid task_2",
        device=device,
        plots=True
    )  # evaluate model performance on the validation set

if __name__ == '__main__':
    main()
