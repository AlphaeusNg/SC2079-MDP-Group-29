# Configuration constants
# LOCATION = "OUT" # IN (indoors) / OUT (outdoors) / NONE (disable turn adjustment)
LOCATION = "NONE" # IN (indoors) / OUT (outdoors) / NONE (disable turn adjustment)

RPI_IP = "192.168.29.29"
MSG_LOG_MAX_SIZE = 150 # characters

# PC Interface
PC_PORT = 8888
PC_BUFFER_SIZE = 2048

# Camera Interface
NUM_IMAGES = 1

# Android Interface
BT_UUID = "00001101-0000-1000-8000-00805f9b34fb"
BT_BUFFER_SIZE = 2048

# STM Interface
STM_BAUDRATE = 115200
STM_ACK_MSG = "A"
STM_NAV_COMMAND_FORMAT = '^[SLR][FB][0-9]{3}$' # task 1
# STM_NAV_COMMAND_FORMAT = '^(([SLR][FB])|([UYV]F)|([IXT][LR]))[0-9]{3}$' # task 2
STM_GYRO_RESET_COMMAND = "GYROR"
STM_GYRO_RESET_DELAY = 4 # time to wait for gyro reset
STM_GYRO_RESET_FREQ = 3 # number of obstacles before GRYO RESET command is sent

# Task 1: adjust commands for turns to correct turning radius to 30cm, as expected by PC-algo
STM_COMMAND_ADJUSTMENT_DICT = {
    "OUT": {
        # 90 degree turns: manually calibrated
        "RF090": ["SF007", "RF090", "SB008"],
        "LF090": ["SF007", "LF090", "SB011"],
        "RB090": ["SF009", "RB090", "SB009"],
        "LB090": ["SF009", "LB090", "SB006"],
        # 180 degree turns: manually calibrated
        "RF180": ["SF008", "RF180", "SB008"],
        "LF180": ["SF007", "LF090", "SB004", "LF090", "SB011"],
        "RB180": ["SF009", "RB180", "SB009"],
        "LB180": ["SF009", "LB090", "SF002", "LB090", "SB009"],
        # 270 degree turns: approximated using 180 degree turn + 90 degree turn
        "RF270": ["SF008", "RF270", "SB008"], 
        "LF270": ["SF007", "LF090", "SB004", "LF090", "SB004", "LF090", "SB011"],
        "RB270": ["SF009", "RB270", "SB009"],
        "LB270": ["SF009", "LB090", "SF002", "LB180", "SB006"]
    },
    "IN": {
        # 90 degree turns: manually calibrated
        "RF090": ["SF008", "RF090", "SB008"],
        "LF090": ["SF006", "LF090", "SB011"],
        "RB090": ["SF009", "RB090", "SB009"],
        "LB090": ["SF010", "LB090", "SB006"],
        # 180 degree turns: manually calibrated
        "RF180": ["SF006", "RF180", "SB012"],
        "LF180": ["SF006", "LF090", "SB005", "LF090", "SB012"],
        "RB180": ["SF009", "RB180", "SB008"],
        "LB180": ["SF009", "LB090", "SF003", "LB090", "SB007"],
        # 270 degree turns: approximated using 180 degree turn + 90 degree turn
        "RF270": ["SF006", "RF180", "SB004", "RF090", "SB008"], 
        "LF270": ["SF006", "LF090", "SB005", "LF090", "SB006", "LF090", "SB011"],
        "RB270": ["SF009", "RB270", "SB009"],
        "LB270": ["SF009", "LB090", "SF003", "LB090", "SF003", "LB090", "SB006"]
    },
    "NONE": {}
}
STM_COMMAND_ADJUSTMENT_MAP = STM_COMMAND_ADJUSTMENT_DICT[LOCATION]

# Task 2: translate PC commands for moving around obstacles to STM_NAV_COMMAND_FORMAT
STM_OBS_ROUTING_MAP = {
    "FIRSTLEFT": ["LF056", "RF056", "SF010", "RF056", "LF056"],
    "FIRSTRIGHT": ["RF056", "LF056", "SF010", "LF056", "RF056"],
    # "FIRSTRIGHT": ["RF090", "RF090", "RF090", "RF090"], # testing
    "SECONDLEFT": ["RF090", "SB056", "IB100", "RB090", "SF036", "RF090"],
    "SECONDRIGHT": ["RF090", "SF004", "IF100", "LF090", "SF010", "LF090"],
    # "SECONDLEFT": ["LF090", "XF300", "RF090", "SF020", "RF090", "XF300", "RF090"], # ref code
    # "SECONDRIGHT": ["RF090", "XF300", "LF090", "SF020", "LF090", "XF300", "LF090",]
}
STM_XDIST_COMMAND_FORMAT = "^XF[0-9]{3}$"
STM_YDIST_COMMAND_FORMAT = "^YF[0-9]{3}$"