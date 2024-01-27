from algo.enumerations import Gear, Steering

class DriveCommand:
    def __init__(self, gear: Gear=Gear.PARK, steering: Steering=Steering.STRAIGHT, distance: float=0) -> None:
        """DriveCommand constructor 

        Args:
            gear (Gear, optional): Drive gear. Defaults to Gear.PARK.
            steering (Steering, optional): Steering command. Defaults to Steering.STRAIGHT.
            distance (float, optional): Distance to travel in cm. Defaults to 0.
        """
        self.gear = gear
        self.steering = steering
        self.distance = distance