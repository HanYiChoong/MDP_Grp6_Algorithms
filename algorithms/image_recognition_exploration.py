from typing import Callable

from algorithms.exploration import Exploration


class ImageRecognitionExploration(Exploration):
    def __init__(self,
                 robot,
                 explored_map: list,
                 obstacle_map: list,
                 on_update_map: Callable = None,
                 on_calibrate: Callable = None,
                 on_take_photo: Callable = None,
                 coverage_limit: float = 1,
                 time_limit: float = 6):
        super().__init__(robot,
                         explored_map,
                         obstacle_map,
                         on_update_map,
                         on_calibrate,
                         coverage_limit,
                         time_limit)
