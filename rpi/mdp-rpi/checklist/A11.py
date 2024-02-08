# Test socket connection to PC

import socket
import sys

class PCInterface:
    def __init__(self):
        self.host = "192.168.14.1"
        self.port = 8888

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket established successfully.")

        try:
            self.socket.bind((self.host, self.port))
            print("Socket binded successfully.")
        except socket.error as e:
            print("Socket binding failed: %s" %str(e))
            sys.exit()

        print("Waiting for PC connection...")
        self.socket.listen(128)
        self.client_socket, self.address = self.socket.accept()
        print("PC connected successfully.")

    def listen(self):
        while True:
            print("Listening for messages from PC...")
            try:
                message = self.client_socket.recv(1024)

                if not message:
                    print("PC disconnected remotely.")
                    break

                decodedMsg = message.decode("utf-8")
                if len(decodedMsg) <= 1:
                    continue
                print("Received from PC: " + decodedMsg)
               
            except socket.error as e:
                print("Failed to read from PC: %s" %str(e))
                break
            except IOError as ie:
                print("Failed to read from PC: %s" %str(ie))
                break
            except Exception as e2:
                print("Failed to read from PC: %s" %str(e2))
                break
            except ConnectionResetError:
                print("ConnectionResetError")
                break
            except:
                print("Unknown error")
                break

    def send(self, message):
        try:
            encoded_string = message.encode()
            byte_array = bytearray(encoded_string)
            self.client_socket.send(byte_array)
            print("Send to PC: " + message)
        except ConnectionResetError:
            print("Failed to send to PC: ConnectionResetError")
        except socket.error:
            print("Failed to send to PC: socket.error")
        except IOError as e:
            print("Failed to send to PC: %s" %str(e))


#def main():
#    pc = PCInterface()
#    pc.connect()
#    pc.send("hello from RPi to PC")
#    pc.listen()
#main()
