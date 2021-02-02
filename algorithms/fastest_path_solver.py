import heapq

from logger import print_general_log, print_error_log
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
        self.parent_node = parent_node
        self.position = position
        self.direction_facing = direction_facing

        self.g = g
        self.h = h
        self.f = INFINITE_COST

    def __eq__(self, other: dict) -> bool:
        return self.position[0] == other[0] and self.position[1] == other[1]

    def __lt__(self, other) -> bool:
        # for heapq priority queue usage
        # TODO: include other costs like turn delay and bearing checks
        # Might compute f cost outside of this function and use it for comparison instead
        current_node_f = self.g + self.h
        other_node_f = other.g + other.h

        return current_node_f < other_node_f

    def __gt__(self, other) -> bool:
        # for heapq priority queue usage
        # TODO: include other costs like turn delay and bearing checks
        # Might compute f cost outside of this function and use it for comparison instead
        current_node_f = self.g + self.h
        other_node_f = other.g + other.h

        return current_node_f > other_node_f

    # For printing purposes
    def __repr__(self) -> str:
        return 'Node information: ' \
               f'(x, y) - ({self.position[0]}, {self.position[1]}) ' \
               f'g - {self.g} ' \
               f'h - {self.h} ' \
               f'Has parent: {self.parent_node is not None}'


class AStarAlgorithm:
    def __init__(self, arena: list) -> None:
        self.open_list = []
        self.closed_list = []
        self.path = []
        self.robot_movements = []
        # self.robot_initial_position = None
        # self.robot_destination_position = None
        self.way_point_node = None
        self.start_node = None
        self.goal_node = None
        self.includes_diagonal = None
        self.arena = arena

    def run_algorithm(self,
                      start_point: list,
                      way_point: list,
                      goal_point: list,
                      direction_facing: int,
                      includes_diagonal: bool):
        # TODO: Validate waypoint before doing anything!
        # TODO: Consider cases such as start point = way point or way point = end point
        self.start_node = Node(start_point, direction_facing)
        self.goal_node = Node(goal_point)
        self.way_point_node = Node(way_point)

        self.start_node.g = 0
        self.start_node.h = 0
        self.start_node.f = 0
        self.includes_diagonal = includes_diagonal

        # Convert list to a priority queue
        # heapq.heapify(self.open_list)
        heapq.heappush(self.open_list, self.start_node)

        path_found = self._find_fastest_path(goal_node=self.way_point_node)

        if not path_found:
            print_error_log('No fastest path found from start to waypoint :(')
            return

        self.start_node = self.way_point_node
        self.open_list.clear()
        heapq.heappush(self.open_list, self.closed_list.pop())
        self.closed_list.clear()

        goal_found = self._find_fastest_path(goal_node=self.goal_node)

        if not goal_found:
            print_error_log('No fastest path found from waypoint to end :(')
            return

        self._rebuild_fastest_path_route()

    def _find_fastest_path(self, goal_node) -> bool:
        while len(self.open_list) > 0:
            visiting_node = heapq.heappop(self.open_list)
            self.closed_list.append(visiting_node)

            if visiting_node == goal_node:
                print_general_log('Fastest path found!')
                return True

            self._add_neighbouring_nodes_to_open_list(visiting_node)

        print_error_log("Fastest path not found! D':")
        return False

    def _add_neighbouring_nodes_to_open_list(self, visiting_node) -> None:
        if self.includes_diagonal:
            possible_neighbouring_positions = constants.NEIGHBOURING_POSITIONS_WITH_DIAGONALS
        else:
            possible_neighbouring_positions = constants.NEIGHBOURING_POSITIONS

        for position in possible_neighbouring_positions:
            neighbour_position = [visiting_node.position[0] + position[0],
                                  visiting_node.position[1] + position[1]]

            # TODO: Include direction as well
            neighbour_node = Node(neighbour_position, parent_node=visiting_node)

            # TODO: Include direction as well
            if self._is_not_a_valid_path(neighbour_node):
                continue

            # TODO: Include direction as well
            self._update_neighbour_node_costs(visiting_node, neighbour_node)

    def _update_neighbour_node_costs(self, visiting_node, neighbour_node) -> None:
        # update neighbour's g, h and f
        # TODO: Include direction as well
        neighbour_node.g = self._get_g_cost() + visiting_node.g
        neighbour_node.h = self._get_h_cost(visiting_node, neighbour_node)

        if neighbour_node not in self.open_list:
            # TODO: Include direction as well
            heapq.heappush(self.open_list, neighbour_node)

        else:
            node_index = self.open_list.index(neighbour_node)
            neighbour_node_from_open_list = self.open_list[node_index]

            old_neighbour_f_cost = neighbour_node_from_open_list.g + neighbour_node_from_open_list.h
            new_neighbour_f_cost = neighbour_node.g + neighbour_node.h

            if old_neighbour_f_cost < new_neighbour_f_cost:
                return

            self.open_list[node_index].g = neighbour_node.g
            self.open_list[node_index].h = neighbour_node.h
            self.open_list[node_index].parent_node = neighbour_node.parent_node
            # TODO: Include direction as well

    def _is_not_a_valid_path(self, neighbour_node) -> bool:
        # must not be in closed list
        # must be within arena range
        # must not be an obstacle or virtual wall
        if neighbour_node in self.closed_list:
            return True

        # TODO: Include direction as well
        if (0 < neighbour_node.position[0] < constants.ARENA_HEIGHT) or \
                (0 < neighbour_node.position[1] < constants.ARENA_WIDTH):
            return True

        x, y = neighbour_node.position

        if self.arena[x][y] != constants.FREE_AREA:
            return True

        return False

    def _rebuild_fastest_path_route(self):
        # Get the goal node from the closed list
        node = self.closed_list.pop()

        while node is not None:
            self.path.insert(0, node)

            node = node.parent_node
            # TODO: Include direction as well

    def _get_g_cost(self):
        raise NotImplementedError

    def _get_h_cost(self, current_node, destination_node):
        return abs(current_node.position[0] - destination_node.position[0]) + abs(
            current_node.position[1] - destination_node.position[1])
