from PIL import Image
import os
import math


def stitching_images(image_folder_path, output_img_path):
    print("Stitching images...")
    # Initialize the big image
    big_img = Image.new('RGB', (2400, 2400))

    # Get a list of all image files in the input folder
    image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
    image_num = len(image_files)

    num_cols = 3
    num_rows = 3

    # Calculate the size of each grid cell
    grid_cell_width = 800
    grid_cell_height = 800

    # Iterate through the image files and paste them onto the big image in a grid
    for i in range((num_rows * num_cols)):
        x = (i % num_cols) * grid_cell_width
        y = (i // num_cols) * grid_cell_height
        
        if i<image_num:
            # Open the image
            img = Image.open(os.path.join(image_folder_path, image_files[i]))
            # Resize the image to fit the grid cell size
            img = img.resize((grid_cell_width, grid_cell_height))
        else:
            gray_color = 128
            img = Image.new('L', (grid_cell_width, grid_cell_height ), gray_color)

        # Paste the image onto the big image
        big_img.paste(img, (x, y))

    # Save the stitched image
    big_img.save(output_img_path)

    print(f'Stitched image saved to {output_img_path}')
    
if __name__ == "__main__":
    stiching_images(r'images_result', r'image_recognition\stitched_image.jpg')