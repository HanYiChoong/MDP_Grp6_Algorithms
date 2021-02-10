from utils import constants


class Robot:
    def __init__(self,
                 initial_x,
                 initial_y,
                 sample_map,
                 direction_facing=constants.BEARING['north']):
        self.x = initial_x
        self.y = initial_y
        self.sample_map = sample_map
        self.direction = direction_facing

        # ASSUMPTIONS: Sensors are placed in the position below (5 sensors)
        # S1  | S2 | S3
        # S4  | X  | S5
        #     | S  |
        #
        self.front_facing_sensor_offset = [1, 0]
        self.front_left_facing_sensor_offset = [1, -1]
        self.front_right_facing_sensor_offset = [1, 1]
        self.left_facing_sensor_offset = [0, -1]
        self.right_facing_sensor_offset = [0, 1]

    def sense_left(self, map_object_reference):
        raise NotImplementedError

    def sense_right(self):
        raise NotImplementedError

    def sense_forward(self):
        raise NotImplementedError

    def move(self):
        raise NotImplementedError

    def turn_left(self):
        raise NotImplementedError

    def turn_right(self):
        raise NotImplementedError
