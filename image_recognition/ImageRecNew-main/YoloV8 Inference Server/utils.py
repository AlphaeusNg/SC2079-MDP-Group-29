from PIL import Image
import shutil
import os
import time
import config

def get_latest_directory(base_dir):

    # Get all the directories in base_dir
    all_subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    # Return the latest directory (by creation time)
    latest_subdir = max(all_subdirs, key=lambda d: os.path.getctime(os.path.join(base_dir, d)))
    return os.path.join(base_dir, latest_subdir)
    
def move_images_to_latest_directory(base_dir, filenames):

    latest_dir = get_latest_directory(base_dir)
    for filename in filenames:
        shutil.move(filename, latest_dir)


def stitch_images():
    """
    Stitches the images in the predict folders together in two rows and saves it into runs/stitched folder
    """
    # Initialize path to save stitched image

    if config.TASK_NO == 1:
        imgFolder = 'YoloV8 Inference Server/runs/detect' # This is for task 1
    elif config.TASK_NO == 2:
        imgFolder = 'YoloV8 Inference Server/runs/detect/Task2' # This is for task 2

    stitchedPath = os.path.join('YoloV8 Inference Server', 'runs', f'stitched-{int(time.time())}.jpeg')
    
    # List all directories inside runs/detect
    dirPaths = [d for d in os.listdir(imgFolder) if os.path.isdir(os.path.join(imgFolder, d))]
    
    imgPaths = []

    if config.TASK_NO == 1:
        for dir in dirPaths:
            image0Path = os.path.join(imgFolder, dir, "image0.jpg")
            if os.path.exists(image0Path):
                imgPaths.append(image0Path)
    elif config.TASK_NO == 2:
        imgPaths = [os.path.join(imgFolder, img) for img in os.listdir(imgFolder) if img.endswith('.jpg')]

    images = [Image.open(x) for x in imgPaths]
    
    num_images = len(images)
    num_images_row1 = num_images // 2 + (num_images % 2)  # If odd number, row 1 gets one more image
    num_images_row2 = num_images // 2

    # Calculate width and height of each image
    width, height = zip(*(i.size for i in images))
    
    # Calculate the total width (max of widths from row 1 and row 2) 
    # and total height (sum of heights from two rows)
    total_width = max(sum(width[:num_images_row1]), sum(width[-num_images_row2:]))
    total_height = 2 * max(height)
    
    stitchedImg = Image.new('RGB', (total_width, total_height))
    
    x_offset = 0
    y_offset = 0
    
    # Stitch the images
    for idx, im in enumerate(images):
        stitchedImg.paste(im, (x_offset, y_offset))
        x_offset += im.size[0]
        
        # If the current image is the last in the first row, reset x_offset and update y_offset
        if idx == num_images_row1 - 1:
            x_offset = 0
            y_offset += max(height)

    stitchedImg.save(stitchedPath)
    return stitchedImg

def get_model_path(current_directory: str) -> str:
    """
    Returns the path to the model based on the current directory.
    """
    if "ImageRec" in current_directory and not current_directory.endswith("YoloV8 Inference Server"):
        model_path = os.path.join(current_directory, "YoloV8 Inference Server", "Weights", "bestv2.pt")
    else:
        model_path = os.path.join(current_directory, "Weights", "bestv2.pt")

    return model_path

def get_latest_image_path(directory: str) -> str:
    """
    Returns the path to the latest image in the directory.
    """
    subdirs = sorted(
        [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))],
        key=lambda d: os.path.getctime(os.path.join(directory, d)),
    )
    # print(f'Subdirs: {subdirs}')
    latest_subdir = os.path.join(directory, subdirs[-1])
    all_jpg_files = [f for f in os.scandir(latest_subdir) if f.name.endswith(".jpg")]
    latest_img_file = sorted(all_jpg_files, key=lambda f: f.stat().st_ctime)[-1].name if all_jpg_files else None

    return os.path.join(latest_subdir, latest_img_file) if latest_img_file else None