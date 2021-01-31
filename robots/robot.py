class Robot:
    def __init__(self, initial_x, initial_y, initial_bearing):
        self.x = initial_x
        self.y = initial_y
        self.bearing = initial_bearing

    def move(self):
        raise NotImplementedError
