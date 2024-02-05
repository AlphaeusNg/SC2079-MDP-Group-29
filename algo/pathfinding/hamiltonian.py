import random
from algo.objects.Obstacle import Obstacle


def find_nearest_neighbor_path(obstacles):
    path = []
    current_pos = (15, 15)

    while obstacles:
        nearest_neighbor = min(obstacles, key=lambda obstacle: abs(obstacle.x_g - current_pos[0] + offset_x(obstacle.facing)) + abs(obstacle.y_g - current_pos[1] + offset_y(obstacle.facing)))
        obstacles.remove(nearest_neighbor)
        path.append((nearest_neighbor.x_g + offset_x(nearest_neighbor.facing), nearest_neighbor.y_g + offset_y(nearest_neighbor.facing)))
        current_pos = (nearest_neighbor.x_g + offset_x(nearest_neighbor.facing), nearest_neighbor.y_g + offset_y(nearest_neighbor.facing))

    return path


def offset_x(facing):
    if facing == 'N':
        return 10
    elif facing == 'S':
        return -10
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
        return -10
    elif facing == 'W':
        return 10


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
    grid = 200
    obstacle_number = 5

    obstacles = generate_random_obstacles(grid, obstacle_number)
    print("\nGrid:")
    print_grid(grid, obstacles)

    path = find_nearest_neighbor_path(obstacles)
    print("\nNearest Neighbor Path:")
    print(path)
