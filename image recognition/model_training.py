from ultralytics import YOLO


if __name__ == '__main__':
    # Load a model
    # model = YOLO("../runs/detect/train/weights/last.pt")
    #
    # # Use the model
    # model.train(
    #     resume=True,
    #     seed=42,
    #     data="dataset/custom_data_yolov8.yaml",
    #     imgsz=640,
    #     batch=16,
    #     epochs=100,
    #     device='cuda')  # train the model

    model = YOLO("../runs/detect/train2/weights/last.pt")

    # Use the model
    model.train(
        resume=True,
        seed=42,
        data="image archive/MDP Image Recognition V4.v1i.yolov8/data.yaml",
        imgsz=640,
        batch=16,
        epochs=200,
        device='cuda')
    metrics = model.val()  # evaluate model performance on the validation set
    # test_results = model(
    #     r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\rpi\images\marcus\images"
    #     r"\7\img8_1_2_0.jpg")  # predict on an image
