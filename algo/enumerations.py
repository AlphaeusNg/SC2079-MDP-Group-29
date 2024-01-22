from enum import Enum

class AgentState(Enum):
    END = 0
    PARK = 1
    DRIVE = 2
    IMAGEREC = 3
    SELFDRIVE = 4