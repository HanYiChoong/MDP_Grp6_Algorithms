from utils import constants

INFINITE_COST = 999999


class Node:
    """
    A class to keep track of the fastest path from start to end goal
    """

    def __init__(self,
                 position: list,
                 direction_facing: int = None,
                 parent_node=None,
                 g: int = INFINITE_COST,
                 h: int = INFINITE_COST) -> None:
        self.parent = parent_node
        self.position = position
        self.direction_facing = direction_facing

        self.g = g
        self.h = h
        self.f = 0

    def __eq__(self, other: dict):
        return self.position[0] == other[0] and self.position[1] == other[1]


class AStarAlgorithm:
    def __init__(self, arena: list) -> None:
        self.open_list = []
        self.closed_list = []
        # self.robot_initial_position = None
        # self.robot_destination_position = None
        self.way_point_node = None
        self.start_node = None
        self.goal_node = None
        self.arena = arena

    def run_algorithm(self, start_point: list, way_point: list, goal_point: list, direction_facing: int):
        self.start_node = Node(start_point, direction_facing)
        self.goal_node = Node(goal_point)
        self.way_point_node = Node(way_point)

        self.start_node.g = 0
        self.start_node.h = 0

        self.open_list.append(self.start_node)

        self._find_fastest_path(self.way_point_node)

    def _find_fastest_path(self, goal_node):
        while len(self.open_list) > 0:
            visiting_node = self.open_list[0]
            best_neighbour_path_index = self._find_index_of_best_neighbour_node(visiting_node)

            visited_node = self.open_list.pop(best_neighbour_path_index)
            self.closed_list.append(visited_node)

            if visited_node == goal_node:
                # collect fastest path nodes and return the information
                pass

            neighbouring_nodes = []
            self._get_valid_neighbouring_nodes(neighbouring_nodes, visited_node)

            for neighbour_node in neighbouring_nodes:
                # generate g and h cost
                # populate the node into the open list
                pass

    def _find_index_of_best_neighbour_node(self, visiting_node) -> int:
        best_neighbour_path_index = 0

        visiting_node_f_cost = visiting_node.g + visiting_node.h

        for index, node in enumerate(self.open_list):
            # TODO: include other costs like turn delay and bearing checks
            node_f_cost = node.g + node.h

            if node_f_cost >= visiting_node_f_cost:
                continue

            best_neighbour_path_index = index

        return best_neighbour_path_index

    def _get_valid_neighbouring_nodes(self, neighbouring_nodes, visited_node):
        for position in constants.NEIGHBOURING_POSITIONS:
            neighbour_position = [visited_node.position[0] + position[0],
                                  visited_node.position[1] + position[1]]

            # TODO: Include direction as well
            if self._is_not_a_valid_path(neighbour_position):
                continue

            # TODO: Include direction as well
            new_node = Node(neighbour_position, parent_node=visited_node)
            neighbouring_nodes.append(new_node)

    def _is_not_a_valid_path(self, neighbour_position: list) -> bool:
        # must be within arena range
        # must not be an obstacle or virtual wall
        # TODO: Include direction as well
        if (0 < neighbour_position[0] < constants.ARENA_HEIGHT) or \
                (0 < neighbour_position[1] < constants.ARENA_WIDTH):
            return True

        x, y = neighbour_position

        if self.arena[x][y] != constants.FREE_AREA:
            return True

        return False

    def _get_g_cost(self):
        raise NotImplementedError

    def _get_h_cost(self, current_node, destination_node):
        return abs(current_node.position[0] - destination_node.position[0]) + abs(
            current_node.position[1] - destination_node.position[1])
