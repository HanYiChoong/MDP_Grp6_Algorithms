from math import ceil
from re import match
from typing import List, Optional

_COORDINATE_POINT_REGEX_PATTERN = r'\d+\s\d+'
_SENSOR_VALUES_REGEX_PATTERN = r'\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+'


def validate_and_decode_point(message: str) -> Optional[List[str]]:
    matched_pattern = match(_COORDINATE_POINT_REGEX_PATTERN, message)

    if matched_pattern is None:
        return None

    return matched_pattern.group().split(' ')


def validate_sensor_values_from_arduino(message: str) -> Optional[List[int]]:
    matched_pattern = match(_SENSOR_VALUES_REGEX_PATTERN, message)

    if matched_pattern is None:
        return None

    sensor_values = matched_pattern.group().split(' ')

    return [ceil(float(sensor_value) / 10) for sensor_value in sensor_values]


if __name__ == '__main__':
    print(validate_sensor_values_from_arduino('11212 12121 12121 12112 121212 121'))
    print(validate_sensor_values_from_arduino('11212 12121 12121 12112 121212 dajdd'))
    print(validate_sensor_values_from_arduino('11212 12121 12121 12112 121212 -1212'))
    print(validate_sensor_values_from_arduino('11212 12121.313 -1.2002121 12112 121212 -1212'))
