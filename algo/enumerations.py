from enum import Enum

class CarState(Enum):
    END = 0
    START = 1
    DRIVE = 2
    IMAGEREC = 3
    SELFDRIVE = 4

class Gear(Enum):
    FORWARD = 1
    PARK = 0
    REVERSE = -1

class Steering(Enum):
    LEFT = -1
    STRAIGHT = 0
    RIGHT = 1