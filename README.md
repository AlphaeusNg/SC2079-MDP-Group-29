# SC2079-MDP-Group-29

## Folder explanation

### image recognition
Contains the scripts for training and inference.

### STM32
Contains STM32 program code for managing and functioning the robot

## SR: STM to RPi
1. Acknowledgement of command
   ```A```
   - acknowledges that command has been received and completed
2. Distance moved from last command 
   ```100```
   - 3 digit number, read 1 character at a time by RPi
   - see RS3 and RS5

## RS: RPi to STM 
1. Movement instructions from PC/Android: direction + forward/backward + distance
    ```SF010```
    - while RPi receives a list of commands from PC (see `NAVIGATION` messages - AR1 and PR1), it sends each 5 character command 1 at a time to STM
      - each command is a 5 character code: <L/R/S><F/B>XXX 
      - S/L/R: the first character indicates Straight / Left / Right 
      - F/B: the second character indicates Forward / Backward
      - XXX: the last 3 digits indicate distance in cm for S, or rotation angle for L/R
      - e.g. SB010 is move backwards 10cm, LF090 is turn 90 degrees to the left in the forward direction
    - on completion, STM acknowledges with A
2. Movement until ultrasonic sensor output indicates imminent obstacle
    ```UF100, VF100```
    - move Forward (this is the only valid direction since our ultrasonic sensor is front mounted)
    - end the movement based on the ultrasonic sensor
      - U is a bigger threshold used for the first part of task 2
      - V is a smaller threshold used for ensuring the robot fully enters the parking zone 
    - XXX: the last 3 digits indicate distance in cm which is the upper limit of how far to move if the ultrasonic sensor is not triggered
    - e.g. UF100 is to move foward 100cm, or until the ultrasonic sensor indicates that an obstacle is ahead
    - on completion, STM acknowledges with A
3. Read distance of movement until ultrasonic sensor output indicates imminent obstacle
    ```YF100```
    - move Forward (this is the only valid direction since our ultrasonic sensor is front mounted)
    - end the movement based on the ultrasonic sensor
    - measure the distance moved
    - XXX: the last 3 digits indicate distance in cm which is the upper limit of how far to move if the ultrasonic sensor is not triggered
    - e.g. YF100 is to move foward 100cm, or until the ultrasonic sensor indicates that an obstacle is ahead, and return the actual distance moved
    - on completion, STM acknowledges with a 3 digit distance in cm
4. Read distance of movement until ultrasonic sensor output indicates imminent obstacle
    ```XL100, XR100```
    - move forward until side-mounted IR sensor shows no obstacle to side
    - check for end of obstacle to Left or Right 
    - XXX: the last 3 digits indicate distance in cm which is the upper limit of how far to move if the ultrasonic sensor is not triggered
    - e.g. XL100 is to move foward 100cm, or until the left ultrasonic sensor indicates that there is no obstacle to the left, and return the actual distance moved
    - on completion, STM acknowledges with a 3 digit distance in cm

## Setup

The following instructions setups a new virtual environment for python and installs the needed libraries.  
These instructions assumes that the user is using a Windows machine.

```cmd
python -m venv .venv
.venv\Scripts\activate
```

To install CUDA-supported PyTorch: [reference](https://pytorch.org/get-started/locally/).

(12.1 in this example)

```cmd
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Pip install the ultralytics package including all [requirements](https://github.com/ultralytics/ultralytics/blob/main/pyproject.toml) in a [**Python>=3.8**](https://www.python.org/) environment with [**PyTorch>=1.8**](https://pytorch.org/get-started/locally/).

[![PyPI version](https://badge.fury.io/py/ultralytics.svg)](https://badge.fury.io/py/ultralytics) [![Downloads](https://static.pepy.tech/badge/ultralytics)](https://pepy.tech/project/ultralytics)

Note: _Reference taken from [here](https://github.com/ultralytics/ultralytics/blob/main/README.md)._

```bash
pip install ultralytics
```

### Hyperparameter
Change hyperparameter `fliplr` in `default.yaml` file at path `.venv/Lib/site-packages/ultralytics/cfg/default.
yaml` to `0.0` to switch off flipping, this is to ensure that the direction of the arrows are not learnt wrongly.
