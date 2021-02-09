import heapq
from time import time
from typing import List, Optional

from logger import print_general_log, print_error_log
from utils import constants

INFINITE_COST = 999999
CoordinateList = List[int]  # x, y


class Node:
    """
    A class to keep track of the fastest path from start to end goal
    """

    def __init__(self,
                 point: CoordinateList,
                 direction_facing: int = None,
                 parent_node=None,
                 g: int = INFINITE_COST,
                 h: int = INFINITE_COST) -> None:
        self.parent_node = parent_node
        self.point = point
        self.direction_facing = direction_facing

        self.g = g
        self.h = h
        self.f = INFINITE_COST

    def __eq__(self, other) -> bool:
        return self.point[0] == other.point[0] and self.point[1] == other.point[1]

    def __lt__(self, other) -> bool:
        # for heapq priority queue usage
        return self.f < other.f

    def __gt__(self, other) -> bool:
        # for heapq priority queue usage
        return self.f > other.f

    def __repr__(self) -> str:
        # For printing purposes
        return 'Node information: ' \
               f'(x, y) - ({self.point[0]}, {self.point[1]}), ' \
               f'g - {self.g}, ' \
               f'h - {self.h}, ' \
               f'f - {self.f}, ' \
               f'bearing - {self.direction_facing}, ' \
               f'Has parent: {self.parent_node is not None}'


class AStarAlgorithm:
    def __init__(self, arena: CoordinateList) -> None:
        """
        Initialises the A* algorithm class to find the fastest
        path from the start point to the way point and from the
        way point to the goal point

        :param arena: The arena generated from the MDF String or a sample arena loaded from disk
        """
        self.open_list = []
        self.closed_list = []
        self.path = []
        self.way_point_node = None
        self.start_node = None
        self.goal_node = None
        self.includes_diagonal = None
        self.arena = arena
        self.time_taken = None

    def run_algorithm(self,
                      start_point: CoordinateList,
                      way_point: CoordinateList,
                      goal_point: CoordinateList,
                      direction_facing: int,
                      includes_diagonal: bool) -> Optional[list]:
        """
        Finds the fastest path from the start point to the way point
        and from the way point to the end point.

        :param start_point: The starting point of the robot
        :param way_point: The way point provided by the Android device
        :param goal_point: The goal point
        :param direction_facing: Current facing direction of the robot
        :param includes_diagonal: A boolean flag to consider diagonal neighbouring points
        :return: A list of nodes for the fastest path search OR None if the provided points are out of range
        """

        # TODO: Consider cases such as start point = way point or way point = end point
        if self._given_points_are_out_of_range(start_point, way_point, goal_point):
            print_error_log('Start, Way Point or Goal coordinates are out of range')
            return

        self.start_node = Node(start_point, direction_facing)
        self.goal_node = Node(goal_point)
        self.way_point_node = Node(way_point)

        self.start_node.g = 0
        self.start_node.h = self._get_h_cost(self.start_node, self.way_point_node)
        self.start_node.f = self.start_node.g + self.start_node.h
        self.includes_diagonal = includes_diagonal

        heapq.heappush(self.open_list, self.start_node)

        start_time = time()

        path_found = self._find_fastest_path(goal_node=self.way_point_node)

        if not path_found:
            end_time = time()
            self.time_taken = end_time - start_time

            print_error_log(f'No fastest path found from start to waypoint. {self.time_taken}')
            return

        self.start_node = self.way_point_node
        self.open_list.clear()
        heapq.heappush(self.open_list, self.closed_list.pop())
        # self.closed_list.clear()

        goal_found = self._find_fastest_path(goal_node=self.goal_node)

        if not goal_found:
            end_time = time()
            self.time_taken = end_time - start_time

            print_error_log(f'No fastest path found from waypoint to end. {self.time_taken}')
            return

        end_time = time()
        self.time_taken = end_time - start_time

        self._rebuild_fastest_path_route()

        # reset to base config and other misc
        self.open_list.clear()
        self.closed_list.clear()

        return self.path

    def _find_fastest_path(self, goal_node: Node) -> bool:
        """
         Searches for the best path from a start point to the end point

        :param goal_node: Expects a way point Node object or the goal node object
        :return: True if the fastest path is found. Else, False
        """
        while len(self.open_list) > 0:
            visiting_node = heapq.heappop(self.open_list)
            self.closed_list.append(visiting_node)

            if visiting_node == goal_node:
                print_general_log('Fastest path found!')
                return True

            self._add_neighbouring_nodes_to_open_list(visiting_node, goal_node)

        print_error_log("Fastest path not found! D':")
        return False

    def _add_neighbouring_nodes_to_open_list(self, visiting_node: Node, goal_node: Node) -> None:
        """
        Populate the neighbouring nodes of the current node in
        the open list, A.K.A Priority Queue

        :param visiting_node: The cheapest cost node popped from the priority queue
        :param goal_node: Expects a way point Node object or the goal node object
        """

        if self.includes_diagonal:
            possible_neighbouring_positions = constants.NEIGHBOURING_POSITIONS_WITH_DIAGONALS
        else:
            possible_neighbouring_positions = constants.NEIGHBOURING_POSITIONS

        for position in possible_neighbouring_positions:
            neighbour_point = [visiting_node.point[0] + position[0],
                               visiting_node.point[1] + position[1]]

            neighbour_node = Node(neighbour_point, parent_node=visiting_node)

            if self._is_not_a_valid_path(neighbour_node):
                continue

            self._update_neighbour_node_costs(visiting_node, neighbour_node, goal_node)

    def _update_neighbour_node_costs(self, visiting_node: Node, neighbour_node: Node, goal_node: Node) -> None:
        """
        Updates the neighbour node's g, h and f cost and add to the priority queue.
        Replaces the node if found in the priority queue and the cost is lower

        :param visiting_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :param goal_node: Expects a way point Node object or the goal node object
        """
        neighbour_node.g = self._get_g_cost_and_set_neighbour_facing_direction(visiting_node, neighbour_node)
        neighbour_node.h = self._get_h_cost(neighbour_node, goal_node)
        neighbour_node.f = neighbour_node.g + neighbour_node.h

        if neighbour_node not in self.open_list:
            heapq.heappush(self.open_list, neighbour_node)

        else:
            # Update lowest cost of the node if in open list
            node_index = self.open_list.index(neighbour_node)
            neighbour_node_from_open_list = self.open_list[node_index]

            if neighbour_node_from_open_list.f < neighbour_node.f:
                return

            self._update_node_values(neighbour_node, node_index)

    def _update_node_values(self, neighbour_node: Node, node_index: int) -> None:
        """
        Replaces the node values in the priority queue

        :param neighbour_node: The neighbouring node of the cheapest cost node
        :param node_index: The index of the neighbouring node in the priority queue
        """
        self.open_list[node_index].g = neighbour_node.g
        self.open_list[node_index].h = neighbour_node.h
        self.open_list[node_index].f = neighbour_node.f
        self.open_list[node_index].parent_node = neighbour_node.parent_node
        self.open_list[node_index].direction_facing = neighbour_node.direction_facing

    def _is_not_a_valid_path(self, neighbour_node: Node) -> bool:
        """
        Determines if the neighbouring node is a valid path.

        Criteria:
        1) The node must not be visited
        2) The node must be within the arena range
        3) The node must not be an obstacle or virtual wall

        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: True if the criteria is fulfilled. Else, false
        """

        if neighbour_node in self.closed_list or \
                self.is_not_within_range_with_virtual_wall(neighbour_node.point) or \
                self.node_is_obstacle_or_virtual_wall(neighbour_node.point):
            return True

        return False

    def is_not_within_range_with_virtual_wall(self, point: CoordinateList) -> bool:
        """
        Determines if the coordinate of the node is within the arena range

        :param point: The (x, y) coordinate of the current node
        :return: True if the coordinate is within the range of the arena
        """

        return not (0 < point[0] < constants.ARENA_HEIGHT - 1 and
                    0 < point[1] < constants.ARENA_WIDTH - 1) or \
               self.node_is_obstacle_or_virtual_wall(point)

    def node_is_obstacle_or_virtual_wall(self, point: CoordinateList) -> bool:
        x, y = point

        return self.arena[x][y] != constants.FREE_AREA

    def _rebuild_fastest_path_route(self) -> None:
        """
        Reconstructs the fastest path from the goal node to the start node
        """
        # Get the goal node from the closed list
        node = self.closed_list.pop()

        while node is not None:
            self.path.insert(0, node)

            node = node.parent_node

    def _given_points_are_out_of_range(self,
                                       start_point: CoordinateList,
                                       way_point: CoordinateList,
                                       goal_point: CoordinateList) -> bool:
        """
        Validate the start, goal and way point coordinates before searching the fastest path

        :param start_point: The starting point of the robot
        :param way_point: The way point provided by the Android device
        :param goal_point: The goal point
        :return: True if the validation passes. Else, False
        """

        return self.is_not_within_range_with_virtual_wall(start_point) or \
               self.is_not_within_range_with_virtual_wall(way_point) or \
               self.is_not_within_range_with_virtual_wall(goal_point)

    def _get_g_cost_and_set_neighbour_facing_direction(self, current_node: Node, neighbour_node: Node) -> int:
        """
        The cost to move from the current node to the neighbouring node

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: g cost
        """
        neighbour_node.direction_facing = self._get_neighbour_direction(current_node, neighbour_node)
        turn_cost = self._get_direction_cost_from_bearing(current_node, neighbour_node)

        if neighbour_node.direction_facing % 2 == 1:  # diagonal bearings assigned are always odd number
            return constants.MOVE_COST + turn_cost

        return constants.MOVE_COST + turn_cost

    def _get_neighbour_direction(self, current_node: Node, neighbour_node: Node) -> int:
        """
        Determines the direction required to reach the neighbouring node

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: The constant value of direction required to reach the neighbouring node
        """
        if self.includes_diagonal:
            if neighbour_node.point[0] - current_node.point[0] > 0 and \
                    neighbour_node.point[1] - current_node.point[1] > 0:
                return constants.BEARING['south_east']

            elif neighbour_node.point[0] - current_node.point[0] > 0 and \
                    neighbour_node.point[1] - current_node.point[1] < 0:
                return constants.BEARING['south_west']

            elif neighbour_node.point[0] - current_node.point[0] < 0 and \
                    neighbour_node.point[1] - current_node.point[1] > 0:
                return constants.BEARING['north_east']

            elif neighbour_node.point[0] - current_node.point[0] < 0 and \
                    neighbour_node.point[1] - current_node.point[1] < 0:
                return constants.BEARING['north_west']

        if neighbour_node.point[0] - current_node.point[0] > 0:
            return constants.BEARING['south']

        elif neighbour_node.point[1] - current_node.point[1] > 0:
            return constants.BEARING['east']

        elif neighbour_node.point[0] - current_node.point[0] < 0:
            return constants.BEARING['north']

        else:
            return constants.BEARING['west']

    def _get_direction_cost_from_bearing(self, current_node: Node, neighbour_node: Node) -> int:
        """
        Determines the turn cost required to reach the neighbouring node.
        The larger the turn, the higher the cost.

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: Turn cost to reach the neighbouring node
        """
        if current_node.direction_facing == neighbour_node.direction_facing:
            return constants.NOT_TURN_COST

        if self.includes_diagonal:
            turn_costs = [constants.TURN_COST_DIAGONAL,
                          constants.TURN_COST_PERPENDICULAR,
                          constants.TURN_COST_DIAGONAL_OPPOSITE_DIRECTION,
                          constants.TURN_COST_OPPOSITE_DIRECTION]
        else:
            turn_costs = [constants.TURN_COST_PERPENDICULAR, constants.TURN_COST_OPPOSITE_DIRECTION]

        previous_bearing = self._get_previous_bearing_from_direction(current_node.direction_facing)
        next_bearing = self._get_next_bearing_from_direction(current_node.direction_facing)

        for i in range(len(turn_costs)):
            if previous_bearing == neighbour_node.direction_facing or \
                    next_bearing == neighbour_node.direction_facing:
                return turn_costs[i]

            previous_bearing = self._get_previous_bearing_from_direction(previous_bearing)
            next_bearing = self._get_next_bearing_from_direction(next_bearing)

    def _get_next_bearing_from_direction(self, current_node_direction: int) -> int:
        """
        Determines the next bearing from the current direction that the 'robot' is facing.
        For example, if the current bearing is 6 (West) and the algorithm does not account
        for diagonal directions, the next bearing will be 6 + 2 = 8.

        By taking the mod of the next bearing, 8, we will get North (0).

        :param current_node_direction: Current direction of the 'robot'
        :return: The next bearing direction
        """
        if self.includes_diagonal:
            return (current_node_direction + 1) % 8

        return (current_node_direction + 2) % 8

    def _get_previous_bearing_from_direction(self, current_node_direction: int) -> int:
        """
        Determines the previous bearing from the current direction that the 'robot' is facing.
        For example, if the current bearing is 6 (West) and the algorithm does not account
        for diagonal directions, the next bearing will be 6 + 6 = 12.

        By taking the mod of the next bearing, 8, we will get South (4).

        :param current_node_direction: Current direction of the 'robot'
        :return: The previous bearing direction
        """
        if self.includes_diagonal:
            return (current_node_direction + 7) % 8

        return (current_node_direction + 6) % 8

    def _get_h_cost(self, neighbour_node: Node, goal_node: Node) -> int:
        """
        The distance (heuristic) cost from the neighbouring node to the goal node.

        :param neighbour_node: The neighbouring node of the cheapest cost node
        :param goal_node: Expects a way point Node object or the goal node object
        :return: h cost
        """

        return abs(neighbour_node.point[0] - goal_node.point[0]) + abs(
            neighbour_node.point[1] - goal_node.point[1])

    def set_map_to_perform_fastest_path(self, new_arena):
        self.arena = new_arena
