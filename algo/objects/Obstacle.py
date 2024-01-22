import numpy as np

class Obstacle:
    def __init__(self, x_g, y_g, face):
        '''
        Parameters:
        x_g (int): x coordinate of obstacle (discretized)
        y_g (int): y coordinate of obstacle (discretized)
        face (string): {'N', 'S', 'E', 'W'} direction of image
        '''
        self.x_g = x_g
        self.y_g = y_g
        self.face = face
        if face == 'E':
            self.theta = 0
        elif face == 'N':
            self.theta = np.pi/2
        elif face == 'W':
            self.theta = np.pi
        elif face == 'S':
            self.theta = -np.pi/2