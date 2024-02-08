# for testing: sending path message to android

import json
import sys
sys.path.append("../rpi_mdp")
from Android import AndroidInterface
from rpi_config import *

def create_path_message(path):
    message = {
        "type": "PATH",
        "data": {
            "path": path
        }
    }
    return json.dumps(message).encode("utf-8")

android = AndroidInterface(None)
android.connect()
path_msg = create_path_message([[0,1], [1,1], [2,1], [3,1]])
android.msg_queue.put(path_msg)
android.send()
