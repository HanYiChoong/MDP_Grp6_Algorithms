from re import match
from typing import List, Optional, Union

_COORDINATE_POINT_REGEX_PATTERN = r'\d+\s\d+'


def validate_and_decode_point(message: str) -> Optional[List[str]]:
    """
    Validate the coordinate points sent from the Android via RPI

    :param message: Coordinate point from Android
    :return: The coordinate point string if the coordinate point is valid. Else none
    """
    matched_pattern = match(_COORDINATE_POINT_REGEX_PATTERN, message)

    if matched_pattern is None:
        return None

    return matched_pattern.group().split(' ')


def validate_and_convert_sensor_values_from_arduino(message: str) -> List[Union[None, int]]:
    """
    Validate the sensor values and converts them to suit the exploration algorithm

    :param message: The sensor values from the Arduino via RPI
    :return: List of sensor values from Arduino
    """
    sensor_values_string: List[str] = message.split(' ')

    return _convert_sensor_value_string_to_integer_list(sensor_values_string)


def _convert_sensor_value_string_to_integer_list(sensor_values_string: List[str]) -> List[Union[None, int]]:
    sensor_values = []

    for sensor_value in sensor_values_string:
        block_distance: int = int(sensor_value)

        if block_distance < 0:
            sensor_values.append(-1)
            continue

        if block_distance == 0:
            sensor_values.append(None)
            continue

        sensor_values.append(block_distance)

    return sensor_values


if __name__ == '__main__':
    print(validate_and_convert_sensor_values_from_arduino('11212 12121 12121 12112 121212 121'))
    print(validate_and_convert_sensor_values_from_arduino('11212 12121 12121 12112 121212 dajdd'))
    print(validate_and_convert_sensor_values_from_arduino('11212 12121 12121 12112 121212 -1212'))
    print(validate_and_convert_sensor_values_from_arduino('11212 12121.313 -1.2002121 12112 121212 -1212'))
