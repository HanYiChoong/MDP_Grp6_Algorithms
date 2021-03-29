import logging
from datetime import datetime
from os.path import exists
from pathlib import Path
from sys import stdout

_BASE_LOGGER_DIRECTORY_PATH = f'{Path(__file__).parent.parent}/logs/'
_LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_STREAM_HANDLER_LOGGER = logging.StreamHandler(stdout)
_STREAM_HANDLER_LOGGER.setFormatter(_LOG_FORMATTER)

# Algorithm logger config
_algo_logger = logging.getLogger(__name__)
_algo_logger.setLevel('DEBUG')
_algo_logger.addHandler(_STREAM_HANDLER_LOGGER)

# Image Recognition logger config
_image_recognition_logger = logging.getLogger(__name__ + 'image_recognition_service')
_image_recognition_logger.setLevel('DEBUG')
_image_recognition_logger.addHandler(_STREAM_HANDLER_LOGGER)


def get_algo_logger():
    algo_logger_directory_path = f'{_BASE_LOGGER_DIRECTORY_PATH}/algo'

    # Uncomment the following lines to log the output to a file
    # created_directory_path = create_log_file(algo_logger_directory_path)
    # _create_and_register_log_file(_algo_logger, created_directory_path)

    return _algo_logger


def get_image_recognition_logger():
    image_recognition_logger_directory_path = f'{_BASE_LOGGER_DIRECTORY_PATH}/img_rec'

    # Uncomment the following lines to log the output to a file
    # created_directory_path = create_log_file(image_recognition_logger_directory_path)
    # _create_and_register_log_file(_image_recognition_logger, created_directory_path)

    return _image_recognition_logger


def _create_and_register_log_file(logger, directory_path):
    logger_file_handler = logging.FileHandler(directory_path)
    logger_file_handler.setFormatter(_LOG_FORMATTER)

    logger.addHandler(logger_file_handler)


def create_log_file(directory_path) -> str:
    datetime_format = '%Y-%m-%d_%H_%M_%S'
    datetime_now_in_string = datetime.now().strftime(datetime_format)

    log_file_directory = f'{directory_path}/{datetime_now_in_string}.txt'

    if not exists(log_file_directory):
        # create file
        Path(log_file_directory).touch(mode=0o777)

    return log_file_directory
