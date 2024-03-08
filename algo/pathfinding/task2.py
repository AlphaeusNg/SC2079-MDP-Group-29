FRONT_TO_REAR = 21
MIN_TURN_RADIUS = 26.5
STOP_THRESHOLD = 40
SIDE_WALL_THRESHOLD = 50 - FRONT_TO_REAR
PARK_THRESHOLD = 10
MEASURED_DIST_AFTER_OBS1 = 37.5
NORMAL_TURN_OFFSET_X = 0
NORMAL_TURN_OFFSET_Y = 0
REVERSE_TURN_OFFSET_X = 0
REVERSE_TURN_OFFSET_Y = 0

def measure_distance():
    """Measures distance from front of car to wall.
    Not implemented
    """
    return 

def image_rec_direction():
    """Takes photo and determine to move left or right
    Not implemented

    Returns 'LEFT' or 'RIGHT'
    """
    return

def move_until(threshold):
    """Moves car until threshold is reached
    Not implemented
    Args:
        threshold (float): distance threshold (front of car to wall)
    """
    return

def left_around_obs1():
    """Moves car around left of obstacle 1
    Not implemented
    """

    # Forward left 45 degrees
    # Forward right 45 degrees
    # Forward forward 13 cm (front of car slightly in front of obstacle)
    # Forward right 45 degrees
    # Forward left 45 degrees

    return

def right_around_obs1():
    """Moves car around right of obstacle 1
    Not implemented
    """
    # Forward right 45 degrees
    # Forward left 45 degrees
    # Move forward 13 cm (front of car slightly in front of obstacle)
    # Forward left 45 degrees
    # Forward right 45 degrees

    return

def main():
    obs1_dist = measure_distance() - 5
    move_until(STOP_THRESHOLD)
    turning = image_rec_direction()

    if turning == 'LEFT':       # Go left around obstacle 1
        left_around_obs1()
    elif turning == 'RIGHT':    # Go right around obstacle 1
        right_around_obs1()

    obs2_dist = measure_distance() + MEASURED_DIST_AFTER_OBS1
    needReverse = False

    if obs2_dist - MEASURED_DIST_AFTER_OBS1 < STOP_THRESHOLD:
        needReverse = True
    
    else:
        move_until(STOP_THRESHOLD)

    turning = image_rec_direction()

    if turning == 'LEFT':       # Go left around obstacle 2
        if needReverse:
            # Reverse right 45 degrees
            # Forward left 45 degrees
            obs2_max_width = 2*(measure_distance() + REVERSE_TURN_OFFSET_X)
            pass
        else:
            # Forward left 90 degrees
            obs2_max_width = 2*(measure_distance() + NORMAL_TURN_OFFSET_X)
            pass

        move_until(SIDE_WALL_THRESHOLD) # reverse until threshold if necessary
        # Forward right 90 degrees
        
        if needReverse:
            # Move forward 20 cm (to be calibrated)
            pass

        # Forward right 90 degrees
        # Forward for obs2_max_width cm (rear axle should line up with right side of obstacle 2)
        # Forward right 90 degrees
        
        if needReverse:
            # Move forward (MEASURED_DIST_AFTER_OBS1 - FRONT_TO_REAR + 10 + REVERSE_TURN_OFFSET_Y + 20 + MIN_TURN_RADIUS) cm (rear axle should line up with bottom of obstacle 1)
            pass
        else:
            # Move forward (obs2_dist + 20 - (STOP_THRESHOLD + FRONT_TO_REAR - 2*MIN_TURN_RADIUS)) cm (rear axle should line up with bottom of obstacle 1)
            pass
        
        # Forward right 90 degrees  (rear axle should line up with right side of obstacle 2)
        # Move forward (obs2_width/2 - MIN_TURN_RADIUS) cm (Reverse if necessary)
        # Forward left 90 degrees (car should be centered)
        # Move forward (obs1_dist + 10 - 2*MIN_TURN_RADIUS) cm (Use ultrasonic threshold 10cm for safety if necessary)


    elif turning == 'RIGHT':    # Go right around obstacle 2 (not implemented)
        if needReverse:
            pass
        else:
            pass
