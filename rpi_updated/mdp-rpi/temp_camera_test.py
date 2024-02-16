import socket
import picamera
import threading
import time

def capture_and_send_image(client_socket):
    try:
        with picamera.PiCamera() as camera:
            # Adjust camera settings as needed
            camera.resolution = (640, 480)
            camera.start_preview()
            time.sleep(2)  # Allow the camera to warm up

            # Capture the image
            image_path = "captured_image.jpg"
            camera.capture(image_path)

            # Send the image to the PC
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                client_socket.sendall(image_data)

    except Exception as e:
        print("Error capturing or sending image:", str(e))

def start_server():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print("Server listening on {}:{}".format(host, port))

    while True:
        client_socket, addr = server_socket.accept()
        print("Accepted connection from:", addr)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=capture_and_send_image, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
