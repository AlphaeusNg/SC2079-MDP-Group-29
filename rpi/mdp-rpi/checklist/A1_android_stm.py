# Checklist item A1: A button pressed from Android tablet (example button to move forward) will be transferred to STM board via RPi and the nano robot is able to execute the motion.

import json
from A13 import STMInterface
from bluetooth import *
import subprocess

subprocess.call(['sudo', 'chmod', 'o+rw', '/var/run/sdp'])
server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))

server_sock.listen(1)
print("getsockname:", server_sock.getsockname())
port = server_sock.getsockname()[1]
#subprocess.call(['sudo', 'sdptool', 'add', '--channel='+str(port), 'SP'])

uuid = "00001101-0000-1000-8000-00805f9b34fb"
advertise_service( server_sock, "MDP-Server",
 service_id = uuid,
 service_classes = [ uuid, SERIAL_PORT_CLASS ],
 profiles = [ SERIAL_PORT_PROFILE ],
# protocols = [ OBEX_UUID ]
 )
print("Waiting for connection on RFCOMM channel %d" % port)
client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

print("Connecting to STM...")
stm = STMInterface()
retry_count = 0
stm.connect()
while stm.connected == False: 
  retry_count += 1
  print("Failed to connect, retrying... (attempt: retry_count)")
  stm.connect()
  if retry_count >= 3:
    break

if retry_count < 3:
  try:
    while True:
      print("Waiting for messages from Android...")
      message = client_sock.recv(1024)
      if len(message) == 0: break

      message_str = message.decode("utf-8")
      print("Received %s" % message_str)
      message_json = json.loads(message_str)
      message_type = message_json["type"]

      if message_type == "NAVIGATION":
        command = message_json["data"][0] #["commands"][0]
        print("Sending command [%s] to STM" % command)
        encoded_string = command.encode()
        byte_array = bytearray(encoded_string)
        stm.send(byte_array)

  except IOError:
    pass
else: 
  print("Giving up")
  
client_sock.close()
server_sock.close()
print("All done")
