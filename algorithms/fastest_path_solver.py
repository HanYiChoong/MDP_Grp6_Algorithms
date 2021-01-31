class AStar:
    def __init__(self):
        self.open_list = []
        self.closed_list = []
        self.way_point = None
        self.start_point = None
        self.goal_point = None

    def run_algorithm(self):
        raise NotImplementedError

    def _find_best_move_to_next_node(self):
        raise NotImplementedError

    def _get_g_cost(self):
        raise NotImplementedError

    def _get_h_cost(self):
        raise NotImplementedError
