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
2. distance moved from last command 
   ```100```
   - 3 digit number, read 1 character at a time by RPi

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