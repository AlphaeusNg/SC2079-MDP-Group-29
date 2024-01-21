import numpy as np

class Obstacle:
    def __init__(self, x, y, face):
        '''
        Parameters:
        x (float32): x coordinate of obstacle
        y (float32): y coordinate of obstacle
        face (string): {'N', 'S', 'E', 'W'} direction of image
        '''
        self.x = x
        self.y = y
        self.face = face
        if face == 'E':
            self.theta = 0
        elif face == 'N':
            self.theta = np.pi/2
        elif face == 'W':
            self.theta = np.pi
        elif face == 'S':
            self.theta = -np.pi/2