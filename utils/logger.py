from configs.logger_config import get_logger

_logger = get_logger()


def print_error_log(message):
    _logger.error(message)


def print_exception_log(message):
    _logger.exception(message)


def print_general_log(message):
    _logger.info(message)


def print_warning_log(message):
    _logger.warning(message)
