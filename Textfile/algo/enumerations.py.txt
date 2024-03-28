from enum import IntEnum

class CarState(IntEnum):
    END = 0
    START = 1
    DRIVE = 2
    IMAGEREC = 3
    SELFDRIVE = 4

class Gear(IntEnum):
    FORWARD = 1
    PARK = 0
    REVERSE = -1

class Steering(IntEnum):
    LEFT = -1
    STRAIGHT = 0
    RIGHT = 1