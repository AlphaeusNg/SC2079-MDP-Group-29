import os
import shutil

def main():
    # Define the root directory and other paths
    root_dir = os.getcwd()
    detect_dir = os.path.join(root_dir, 'runs', 'detect')
    output_dir = os.path.join(root_dir, 'rawResizedImages')

    # Create rawResizedImages directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Go through each sub-directory in 'detect'
    for subdir in os.listdir(detect_dir):
        if subdir.startswith('predict'):
            subdir_path = os.path.join(detect_dir, subdir)
            for filename in os.listdir(subdir_path):
                if filename.startswith('resized_image'):
                    src_file = os.path.join(subdir_path, filename)
                    shutil.copy(src_file, output_dir)

if __name__ == '__main__':
    main()
