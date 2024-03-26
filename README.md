# SC2079-MDP-Group-29

## Folder Structure

### image_recognition
This folder contains scripts for training and inference related to image recognition.

### STM32
This folder contains STM32 program code for managing and controlling the robot.

## Serial Communication: STM to RPi

When communicating serially between the STM32 and Raspberry Pi (RPi), the following protocol is used:

1. Acknowledgment of Command:
   - Character: `A`
   - Description: Acknowledges that a command has been received and completed.

2. Distance Moved from Last Command:
   - Format: 3-digit number (e.g., `100`)
   - Description: The distance moved from the last command, read one character at a time by the RPi.

## Setup

To set up a new virtual environment for Python and install the required libraries, follow these steps (assuming a Windows environment):

1. Create a virtual environment:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install CUDA-supported PyTorch. (example for CUDA 12.1):
   ```cmd
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```
   See [reference](https://pytorch.org/get-started/locally/) if more help is needed.

3. Install the ultralytics package along with its requirements and the Pygame library:
   ```cmd
   pip install ultralytics pygame
   ```
   **Note**: The instructions provided above assume a Python environment with version 3.8 or higher and PyTorch version 1.8 or higher.

   For more information on the ultralytics package, visit their GitHub repository.

   See [requirements](https://github.com/ultralytics/ultralytics/blob/main/pyproject.toml) in a [**Python>=3.8**](https://www.python.org/) environment with [**PyTorch>=1.8**](https://pytorch.org/get-started/locally/).

   [![PyPI version](https://badge.fury.io/py/ultralytics.svg)](https://badge.fury.io/py/ultralytics) [![Downloads](https://static.pepy.tech/badge/ultralytics)](https://pepy.tech/project/ultralytics)

   Note: _Reference taken from [here](https://github.com/ultralytics/ultralytics/blob/main/README.md)._
   
### Hyperparameter
For training purposes, it's recommended to adjust the `fliplr` hyperparameter in the `default.yaml` file located at `.venv/Lib/site-packages/ultralytics/cfg/default.yaml`. Set `fliplr` to `0.0` to disable flipping. This ensures that directional arrows (left & right) are not learned incorrectly.




## Evolution of SC2079-MDP-Group-29
### Inception and Initial State
The project began with a fork from the repository https://github.com/dhairyarungta/mdp-death/tree/main. This initial version provided a basic framework for robot control, image recognition, and algorithm implementation.

### Significant Changes and Enhancements
#### Camera Positioning
The camera was moved to the left side of the robot for quicker movement and better visibility during navigation and image recognition tasks.

#### Image Recognition
We added a second model fine-tuned for task 2, improving accuracy and robustness.

#### RPI Side Improvements
Enhancements included a backup secondary model inference mechanism for continuity, a retry mechanism for failed image capture attempts, and a mapping list to track encountered images for better predictions.

#### Algorithmic Refinements
We modified the robot's movement pattern to include sideways maneuvers, enhancing adaptability and agility.

## Areas for Improvement
1. Increase STM Wheel Speed: Explore options to boost wheel speed for quicker navigation.
2. Optimize Communication Protocol: Evaluate disabling acknowledgment communication between the STM and RPI for faster movement.