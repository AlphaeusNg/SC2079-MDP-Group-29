from algo.objects.Obstacle import Obstacle
from algo.simulator.simulator import Simulator

if __name__ == "__main__":

    obstacles1 = [Obstacle(10, 38, 'S'), Obstacle(38, 10, 'W'),
                  Obstacle(10, 5, 'E'), Obstacle(2,20,'E')]

    obstacles2 = [Obstacle(15, 20, 'N'), Obstacle(15, 15, 'S'),
                  Obstacle(20, 15, 'S'), Obstacle(20,20,'N')]

    Simulator(obstacles2).start_simulation()
    