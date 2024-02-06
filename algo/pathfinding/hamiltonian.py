import random
import itertools
import numpy
import algo.utils as u
from algo.objects.Obstacle import Obstacle


def find_brute_force_path(obstacles):
    obstacle_permutations = itertools.permutations(obstacles)
    shortest_path = None
    shortest_distance = float('inf')
    for obstacle_order in obstacle_permutations:
        path = []
        current_pos = (15, 15)
        total_distance = 0
        for obstacle in obstacle_order:
            x_coord, y_coord = u.grid_to_coords(obstacle.x_g, obstacle.y_g)
            distance = abs(x_coord - current_pos[0] + offset_x(obstacle.facing)) + abs(y_coord - current_pos[1] + offset_y(obstacle.facing))
            total_distance += distance
            path.append((x_coord + offset_x(obstacle.facing), y_coord + offset_y(obstacle.facing), obstacle.facing))
            current_pos = (x_coord + offset_x(obstacle.facing), y_coord + offset_y(obstacle.facing))
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            shortest_path = path[:]
    return shortest_path


def find_nearest_neighbor_path(obstacles):
    path = []
    current_pos = (15, 15)

    while obstacles:
        x_coord, y_coord = u.grid_to_coords(obstacles[0].x_g, obstacles[0].y_g)
        nearest_neighbor = min(obstacles, key=lambda obstacle: abs(x_coord - current_pos[0] + offset_x(obstacle.facing)) + abs(y_coord - current_pos[1] + offset_y(obstacle.facing)))
        obstacles.remove(nearest_neighbor)
        path.append((x_coord + offset_x(nearest_neighbor.facing), y_coord + offset_y(nearest_neighbor.facing), nearest_neighbor.facing))
        current_pos = (x_coord + offset_x(nearest_neighbor.facing), y_coord + offset_y(nearest_neighbor.facing))

    return path


def theta_goal(facing):
    if facing == 'N':
        return -(numpy.pi/2)
    elif facing == 'S':
        return numpy.pi/2
    elif facing == 'E':
        return numpy.pi
    elif facing == 'W':
        return 0


def offset_x(facing):
    if facing == 'N':
        return 0
    elif facing == 'S':
        return 0
    elif facing == 'E':
        return 40
    elif facing == 'W':
        return -40


def offset_y(facing):
    if facing == 'N':
        return 40
    elif facing == 'S':
        return -40
    elif facing == 'E':
        return 0
    elif facing == 'W':
        return 0


def generate_random_obstacles(grid_size, obstacle_count):
    if grid_size < 100:
        offset = 5
    else:
        offset = 50
    obstacles = []
    directions = ['N', 'S', 'E', 'W']

    while len(obstacles) < obstacle_count:
        x = random.randint(offset, grid_size - offset)
        y = random.randint(offset, grid_size - offset)
        direction = random.choice(directions)
        obstacles.append(Obstacle(x, y, direction))

    return obstacles


def print_grid(grid_size, obstacles):
    path = []
    for y in range(grid_size - 1, -1, -1):
        for x in range(grid_size):
            position = (x, y)
            if (0 <= x <= 2) and (0 <= y <= 2):
                print("C", end=" ")  # Starting point
            elif any(obstacle.x_g == x and obstacle.y_g == y for obstacle in obstacles):
                direction = next(
                    (obstacle.facing for obstacle in obstacles if (obstacle.x_g, obstacle.y_g) == position), None)
                print(direction, end=" " if direction else ".")  # Obstacle facing direction
            elif (x, y) in path:
                print("*", end=" ")  # Mark the path with "*"
            else:
                print(".", end=" ")  # Empty space
        print()


if __name__ == "__main__":
    grid = 40
    obstacle_number = 5

    obstacles = generate_random_obstacles(grid, obstacle_number)
    print("\nGrid:")
    print_grid(grid, obstacles)

    path = find_brute_force_path(obstacles)
    print("\nShortest Path:")
    print(path)

