from configs.logger_config import get_algo_logger, get_image_recognition_logger

__algo_logger = get_algo_logger()
__image_recognition_logger = get_image_recognition_logger()


# Algorithm logger functions
def print_error_log(message):
    __algo_logger.error(message)


def print_exception_log(message):
    __algo_logger.exception(message)


def print_general_log(message):
    __algo_logger.info(message)


def print_warning_log(message):
    __algo_logger.warning(message)


# Image recognition logger functions
def print_img_rec_error_log(message):
    __image_recognition_logger.error(message)


def print_img_rec_exception_log(message):
    __image_recognition_logger.exception(message)


def print_img_rec_general_log(message):
    __image_recognition_logger.info(message)


def print_img_rec_warning_log(message):
    __image_recognition_logger.warning(message)
