"""
Contain functions to detect object position
"""
import math


# Using PICamera v2.1
def distance_to_camera(per_width: float, known_width: float = 60, focal_length: float = 3.04) -> float:
    """
    Gets the distance of the object based on bounding box size.
    @param known_width: The known width of the symbol in mm
    @param focal_length: The focal length of the camera in mm, an established value
    @param per_width: The width of the bounding box in mm
    @return: The distance to the camera
    """
    dist = (known_width * focal_length) / per_width
    print(per_width, dist)
    return dist


def get_focal_length(known_dist: float, known_width: float, per_width: float) -> float:
    """
    Call this function once to calibrate the focal length of the camera.
    @param known_dist: The known distance of the symbol to the camera
    @param known_width: The known width of the symbol
    @param per_width: The width of the bounding box
    @return: The focal length of the camera
    """
    return (per_width * known_dist) / known_width


def get_obj_pos(dist: float, bbox_centre_x: float, camera_width: float = 720, camera_fov: float = 62.2) -> [int, int]:
    """
    Gets the object position relative to robot in terms of a vector transform
    @param bbox_centre_x: The bounding box's centre x coordinate
    @param camera_width: The camera's horizontal resolution
    @param camera_fov: The camera's FOV in terms of angle
    @param dist: The object's distance from the camera
    @return: An x-y vector of how many squares the object is in front of the camera, \
    where the y-axis is projected directly ahead of the camera
    """
    # Note: PiCamera V1 has a horizontal FOV of 53.50 degrees, V2 has 62.2 degrees
    # https://www.raspberrypi.org/documentation/hardware/camera/

    # The object's relative position across the screen from the leftmost edge
    obj_screen_pos = bbox_centre_x / camera_width

    # The object's angle from the camera's leftmost edge
    obj_angle = camera_fov * obj_screen_pos

    # The object's angle from the centre line
    obj_angle -= camera_fov / 2

    # Get object's absolute x-y position about camera
    # Make angle +ve
    abs_angle = abs(obj_angle)

    # X coordinate cos(angle) = x / dist ; x = dist * cos(angle)
    x_dist = dist * math.cos(abs_angle)

    # Is x on left or right of camera?
    if obj_angle < 0:
        x_dist = -x_dist

    # Y coordinate sin(angle) = y / dist ; y = dist * sin(angle)
    y_dist = dist * math.cos(abs_angle)

    return [round(x_dist / 10, 0), round(y_dist / 10, 0)]
