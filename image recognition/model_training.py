from ultralytics import YOLO


if __name__ == '__main__':
    # Load a model
    model = YOLO("yolov8n.pt")
    # model = YOLO("../runs/detect/train/weights/last.pt") # if training stopped halfway

    # Start transfer learning on old_batch_image
    model.train(
        resume=True,
        seed=42,
        data="dataset/old_batch_image/custom_data_yolov8.yaml",
        imgsz=640,
        batch=16,
        epochs=100,
        device='cuda')  # train the model

    # Fine-tune on current_batch_image
    # model = YOLO("../runs/detect/train2/weights/last.pt") # if training stopped halfway
    model.train(
        resume=True,
        seed=42,
        data="image archive/MDP Image Recognition V4.v1i.yolov8/data.yaml",
        imgsz=640,
        batch=16,
        epochs=200,
        device='cuda')

    metrics = model.val()  # evaluate model performance on the validation set
