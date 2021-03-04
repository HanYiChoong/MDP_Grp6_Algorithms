from re import match
from typing import List, Optional, Union

_COORDINATE_POINT_REGEX_PATTERN = r'\d+\s\d+'
_SENSOR_VALUES_REGEX_PATTERN = r'\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+\s\-?\d+\.?\d+'


def validate_and_decode_point(message: str) -> Optional[List[str]]:
    matched_pattern = match(_COORDINATE_POINT_REGEX_PATTERN, message)

    if matched_pattern is None:
        return None

    return matched_pattern.group().split(' ')


def validate_and_convert_sensor_values_from_arduino(message: str) -> List[Union[None, int]]:
    matched_pattern = match(_SENSOR_VALUES_REGEX_PATTERN, message)

    if matched_pattern is None:
        return []

    sensor_values_string: List[str] = matched_pattern.group().split(' ')

    return _convert_sensor_value_string_to_integer_list(sensor_values_string)


def _convert_sensor_value_string_to_integer_list(sensor_values_string: List[str]) -> List[Union[None, int]]:
    sensor_values = []

    for sensor_value in sensor_values_string:
        block_distance = round(float(sensor_value) / 10)

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
