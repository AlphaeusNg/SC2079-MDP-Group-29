import os
import cv2
from ultralytics import YOLO
import time

class ImagePredictor:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.names = self.model.names

    def predict_image(self, img_np_array, slug):
        project_dir = "runs/detect"
        name_dir = f"predict{slug}"

        results = self.model(
            img_np_array,
            imgsz=416,
            conf=0.2,
            save=False,
            show_conf=False,
            project=project_dir,
            name=name_dir
        )

        predicted_class = "99"
        max_prob = 0
        max_area = 0
        max_bbox = None

        # Tolerance for bounding box area
        AREA_TOLERANCE = 4

        for result in results:
            confidences = result.boxes.conf
            classes = result.boxes.cls
            bboxes = result.boxes.xyxy

            for i, confidence in enumerate(confidences):
                bbox = bboxes[i]
                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                current_class = self.names[int(classes[i])]
                print(f"Predicted Class: {current_class}, Confidence: {confidence:.2f}")  # <-- New print statement here

                if abs(area - max_area) <= AREA_TOLERANCE:
                    if confidence > max_prob:
                        max_prob = confidence
                        predicted_class = current_class
                        max_bbox = bboxes[i]
                        max_area = area
                elif area > max_area:
                    max_area = area
                    predicted_class = current_class
                    max_bbox = bboxes[i]
                    max_prob = confidence

        return predicted_class, max_bbox, max_prob


def post_process_image(image, bboxes, max_prob, predicted_class):
    x1, y1, x2, y2,  = map(int, bboxes)
    label = f"{int(predicted_class)} {max_prob:.2f}"
    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (45, 225, 235), 2)

    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
    background_rect_top_left = int(x1), int(y1) - label_size[1] - 10
    background_rect_bottom_right = int(x1) + label_size[0], int(y1)

    cv2.rectangle(image, background_rect_top_left, background_rect_bottom_right, (45, 225, 235), -1)
    cv2.putText(image, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
    
    return image

def main():
    current_directory = os.getcwd()
    model_path = os.path.join(current_directory, "YoloV8 Inference Server", "Weights", "bestv4.pt")
    predictor = ImagePredictor(model_path)

    test_images_dir = os.path.join(os.getcwd(), "test_images")
    for filename in os.listdir(test_images_dir):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            filepath = os.path.join(test_images_dir, filename)
            
            print(f"Reading file: {filepath}")
            original_img = cv2.imread(filepath)
            # Resize the image to 416x416
            resized_img = cv2.resize(original_img, (416, 416))

            slug = str(int(time.time()))
            predicted_class, max_bbox, max_prob = predictor.predict_image(resized_img, slug)

            print(f'Predicted Class: {predicted_class}, Max Probability: {max_prob:.2f}, max_bbox: {max_bbox}')
            post_processed_img = post_process_image(resized_img, max_bbox, max_prob, predicted_class)

            print(f"Image {filename} - Predicted Class: {predicted_class} ({max_prob:.2f})")

            saved_filename = f"predicted_{slug}_{filename}"
            saved_filepath = os.path.join(test_images_dir, saved_filename)
            cv2.imwrite(saved_filepath, post_processed_img)

            cv2.imshow(filename, post_processed_img)
            cv2.waitKey(0)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
