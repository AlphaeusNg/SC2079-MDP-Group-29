import os
from pathlib import Path

"""
Just to generate blank yolovx annotations for background shots
"""

def generate_empty_txt_files(image_folder):
    # Get a list of all image files in the specified folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

    # Create an empty text file for each image
    for image_file in image_files:
        # Create the corresponding text file name by replacing the image file extension with '.txt'
        txt_file = os.path.splitext(image_file)[0] + '.txt'

        # Construct the full paths for the image and text files
        image_path = os.path.join(image_folder, image_file)
        txt_path = os.path.join(image_folder, txt_file)

        # Check if the text file already exists before creating it
        if not os.path.exists(txt_path):
            with open(txt_path, 'w'):
                pass  # This creates an empty text file

            print(f"Empty text file created for: {image_file}")


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    folder_location = os.path.join(current_dir, 'images', 'marcus', 'Noise Photo')
    generate_empty_txt_files(folder_location)
