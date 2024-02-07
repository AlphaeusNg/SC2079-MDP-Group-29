from algo.objects.Obstacle import Obstacle
from algo.simulator.simulator import Simulator

if __name__ == "__main__":
    obstacles1 = [Obstacle(10, 38, 'S')]

    # Two image in same spot, can be solved with deviation function
    obstacles2 = [Obstacle(15, 20, 'N'), Obstacle(20, 20, 'N')]

    # Last obstacle path not found, need create deviation in algo
    obstacles3 = [Obstacle(10, 38, 'S'), Obstacle(38, 10, 'W'), Obstacle(10, 5, 'E'),
                 Obstacle(2,20,'E'), Obstacle(38, 38, 'W')]

    # Car slam into obstacle, too many tight corners
    obstacles4 = [Obstacle(10, 17, 'N'), Obstacle(17, 5, 'S'), Obstacle(27, 26, 'W'), Obstacle(29, 26, 'N'),
                  Obstacle(16, 17, 'S'), Obstacle(14, 32, 'W'), Obstacle(29, 37, 'N'), Obstacle(27, 3, 'E')]

    # Car can't get out, turning radius too high
    obstacles5 = [Obstacle(25, 1, 'S'), Obstacle(37, 5, 'W'), Obstacle(5, 8, 'E'), Obstacle(10, 30, 'S'),
                  Obstacle(25, 24, 'W'), Obstacle(5, 17, 'E'), Obstacle(22, 17, 'E'), Obstacle(7, 22, 'W')]

    # Obstacle blocking starting position
    obstacles6 = [Obstacle(4, 38, 'N'), Obstacle(15, 15, 'E'), Obstacle(6, 6, 'S'), Obstacle(10, 30, 'S'),
                  Obstacle(25, 24, 'W'), Obstacle(38, 15, 'N'), Obstacle(38, 3, 'W'), Obstacle(38, 38, 'N')]

    Simulator(obstacles3).start_simulation()
