import socket

GRID_SIZE = 40

# simulation parameters
WIDTH = 1200
HEIGHT = 900

MAP_WIDTH = 800
MAP_HEIGHT = 800
MAP_X0 = 50
MAP_Y0 = 50

BORDER_THICKNESS = 5

TURNING_RADIUS = 25

# RPI & PC connection
RPI_HOST: str = "192.168.29.29"
RPI_PORT: int = 3001
PC_HOST: str = socket.gethostbyname(socket.gethostname())
PC_PORT: int = 3000
