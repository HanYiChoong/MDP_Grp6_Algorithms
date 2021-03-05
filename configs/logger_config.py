import logging
from datetime import datetime
from os.path import exists
from pathlib import Path
from sys import stdout

_logger = logging.getLogger(__name__)
_logger.setLevel('DEBUG')

_stderr_logger = logging.StreamHandler(stdout)

_logger.addHandler(_stderr_logger)

_LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_stderr_logger.setFormatter(_LOG_FORMATTER)


def get_logger():
    _create_and_register_log_file()

    return _logger


def _create_and_register_log_file():
    _directory_path = create_log_file()
    _file_logger = logging.FileHandler(_directory_path)
    _file_logger.setFormatter(_LOG_FORMATTER)
    _logger.addHandler(_file_logger)


def create_log_file() -> str:
    datetime_format = '%Y-%m-%d_%H_%M_%S'
    datetime_now_in_string = datetime.now().strftime(datetime_format)
    log_file_directory = f'{Path(__file__).parent.parent}/logs/{datetime_now_in_string}.txt'

    if not exists(log_file_directory):
        # create file
        Path(log_file_directory).touch(mode=0o777)

    return log_file_directory
