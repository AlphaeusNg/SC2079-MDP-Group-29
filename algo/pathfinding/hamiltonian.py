import random


def generate_random_obstacles(grid_size, obstacle_count):
    obstacles = {}
    directions = ['N', 'S', 'E', 'W']

    while len(obstacles) < obstacle_count:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        direction = random.choice(directions)
        obstacles[(x, y)] = direction

    return obstacles


def find_nearest_neighbor_path(start, targets, obstacles):
    path = []
    current_position = start

    while targets:
        nearest_neighbor = min(targets,
                               key=lambda pos: abs(pos[0] - current_position[0]) + abs(pos[1] - current_position[1]))
        targets.remove(nearest_neighbor)

        if nearest_neighbor in obstacles:
            direction = obstacles[nearest_neighbor]
            if direction == 'N':
                path.append((nearest_neighbor[0] + 1, nearest_neighbor[1] + 4))
            elif direction == 'S':
                path.append((nearest_neighbor[0] - 1, nearest_neighbor[1] - 4))
            elif direction == 'E':
                path.append((nearest_neighbor[0] + 4, nearest_neighbor[1] - 1))
            elif direction == 'W':
                path.append((nearest_neighbor[0] - 4, nearest_neighbor[1] + 1))

    return path


def print_grid(grid_size, obstacles, path=[]):
    for y in range(grid_size - 1, -1, -1):
        for x in range(grid_size):
            position = (x, y)
            if (0 <= x <= 2) and (0 <= y <= 2):
                print("C", end=" ")  # Starting point
            elif position in obstacles:
                direction = obstacles[position]
                print(direction, end=" " if direction else ".")  # Obstacle facing direction
            else:
                print(".", end=" ")  # Empty space
        print()


if __name__ == "__main__":
    grid_size = 20
    obstacle_count = 3

    start_position = (0, 0)
    obstacle_positions = generate_random_obstacles(grid_size, obstacle_count)

    hamiltonian_path = find_nearest_neighbor_path(start_position, set(obstacle_positions.keys()), obstacle_positions)
    print("Obstacle Positions in the Order of Shortest Path:", hamiltonian_path)

    print("\nGrid with Obstacles and Facing Directions:")
    print_grid(grid_size, obstacle_positions, hamiltonian_path)
