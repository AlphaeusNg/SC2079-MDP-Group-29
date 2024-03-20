import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from objects.Obstacle import Obstacle

def get_maps():
    maps = []

    maps.append([Obstacle(10, 18, 'N'), Obstacle(16, 6, 'S'), Obstacle(28, 26, 'W'), Obstacle(28, 24, 'N'), 
                    Obstacle(18, 18, 'S'), Obstacle(14, 32, 'W'), Obstacle(30, 38, 'N'), Obstacle(30, 4, 'E')])

    maps.append([Obstacle(24, 2, 'S'), Obstacle(36, 6, 'E'), Obstacle(12, 18, 'E'), Obstacle(10, 28, 'S'), 
                    Obstacle(24, 24, 'W'), Obstacle(36, 18, 'E'), Obstacle(24, 18, 'E'), Obstacle(2, 34, 'W')])

    maps.append([Obstacle(4, 38, 'N'), Obstacle(14, 14, 'E'), Obstacle(6, 22, 'S'), Obstacle(32, 28, 'S'), 
                    Obstacle(26, 14, 'N'), Obstacle(28, 14, 'W'), Obstacle(38, 4, 'E'), Obstacle(38, 34, 'E')])

    maps.append([Obstacle(10, 10, 'N'), Obstacle(1, 30, 'W'), Obstacle(38, 32, 'E'), Obstacle(10, 25, 'S'), 
                    Obstacle(16, 30, 'E'), Obstacle(30, 10, 'S'), Obstacle(24, 26, 'W'), Obstacle(4, 18, 'N')])

    maps.append([Obstacle(2, 20, 'N'), Obstacle(1, 27, 'W'), Obstacle(20, 20, 'N'), Obstacle(32, 10, 'E'), 
                    Obstacle(22, 22, 'W'), Obstacle(20, 22, 'S'), Obstacle(20, 2, 'S'), Obstacle(36, 34, 'E')])

    maps.append([Obstacle(1, 15, 'W'), Obstacle(6, 34, 'N'), Obstacle(18, 20, 'N'), Obstacle(26, 10, 'W'), 
                    Obstacle(32, 32, 'N'), Obstacle(20, 32, 'W'), Obstacle(34, 4, 'S'), Obstacle(16, 30, 'N')])

    maps.append([Obstacle(10, 38, 'N'), Obstacle(17, 32, 'W'), Obstacle(34, 34, 'N'), Obstacle(15, 15, 'E'), 
                    Obstacle(10, 22, 'S'), Obstacle(36, 19, 'E'), Obstacle(32, 5, 'S'), Obstacle(26, 10, 'W')])

    maps.append([Obstacle(10, 38, 'N'), Obstacle(17, 36, 'N'), Obstacle(24, 10, 'S'), Obstacle(38, 20, 'S'), 
                    Obstacle(10, 16, 'S'), Obstacle(18, 17, 'N'), Obstacle(10, 7, 'E'), Obstacle(26, 10, 'W')])

    maps.append([Obstacle(10, 38, 'N'), Obstacle(17, 36, 'N'), Obstacle(25, 30, 'E'), Obstacle(16, 6, 'E'), 
                    Obstacle(10, 15, 'S'), Obstacle(16, 19, 'N'), Obstacle(23, 26, 'W'), Obstacle(30, 10, 'E')])

    maps.append([Obstacle(10, 15, 'W'), Obstacle(17, 20, 'E'), Obstacle(27, 15, 'N'), Obstacle(26, 22, 'S'), 
                    Obstacle(10, 34, 'W'), Obstacle(4, 32, 'N'), Obstacle(22, 28, 'W'), Obstacle(20, 4, 'W')])
    
    return maps