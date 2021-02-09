class Robot:
    def __init__(self, initial_x, initial_y, initial_direction):
        self.x = initial_x
        self.y = initial_y
        self.direction = initial_direction

    def run_fastest_path_with_waypoint(self):
        pass

    def move(self):
        raise NotImplementedError
