from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    # model = YOLO("yolov8n.pt")
    # model = YOLO("../runs/detect/train/weights/last.pt") # if training stopped halfway

    # Start transfer learning on old_batch_image
    # model.train(
    #     resume=True, # if training stopped halfway
    #     seed=42,
    #     data="dataset/old_batch_image/custom_data_yolov8.yaml",
    #     imgsz=640,
    #     batch=16,
    #     epochs=100,
    #     device='cuda')  # train the model

    # Fine-tune on current_batch_image
    # model = YOLO("../runs/detect/valid (train2 + MDP CV.v7)/weights/last.pt") # if training stopped halfway
    # model.train(
    #     resume=True, # if training stopped halfway
    #     seed=42,
    #     data="image_recognition/dataset/image archive/MDP Image Recognition V4.v1i.yolov8/data.yaml",
    #     imgsz=640,
    #     batch=16,
    #     epochs=200,
    #     device='cuda',
    #     name="train (old_batch_image + current_batch_image)",
    #     exist_ok=True)

    # Further fine-tuning on MDP CV.v8i.yolov8 (personally curated dataset)
    # model = YOLO("../runs/detect/train (old_batch_image + current_batch_image)/weights/best.pt")  # if training stopped
    # halfway
    # model.train(
    #     # resume=True, # if training stopped halfway
    #     seed=42,
    #     data=r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\image_recognition\dataset\MDP "
    #          r"CV.v8i.yolov8\data.yaml",
    #     imgsz=640,
    #     batch=16,
    #     epochs=200,
    #     device='cuda',
    #     name="train (old + current + MDP CV.v8)",
    #     exist_ok=True
    # )

    # metrics = model.val(
    #     name="valid (old + current + MDP CV.v8)"
    # )  # evaluate model performance on the validation set

    # model = YOLO("image_recognition/runs/detect/train (MDP CV.v8 only)/weights/last.pt")
    # model.train(
    #     resume=True,
    #     seed=42,
    #     data=r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\image_recognition\dataset\MDP "
    #          r"CV.v8i.yolov8\data.yaml",
    #     imgsz=640,
    #     batch=16,
    #     epochs=300,
    #     device='cuda',
    #     name="train (MDP CV.v8 only)")  # train the model

    # metrics = model.val(
    #     name="valid (MDP CV.v8 only)"
    # )  # evaluate model performance on the validation set
    model = YOLO(r"image_recognition\runs\detect\train task 23\weights\last.pt")
    model.train(
        resume=True,
        seed=42,
        data=r"C:\Users\alpha\OneDrive\Desktop\Life\NTU\Y4S2\MDP\SC2079-MDP-Group-29\image_recognition\dataset\MDP_Task2.v6i.yolov8\data.yaml",
        imgsz=640,
        batch=16,
        epochs=300,
        device='cuda',
        name="train task 2")  # train the model

    metrics = model.val(
        name="valid task 2" 
    )  # evaluate model performance on the validation set
