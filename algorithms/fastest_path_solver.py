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
        # TODO: include other costs like turn delay and bearing checks
        return self.f < other.f

    def __gt__(self, other) -> bool:
        # for heapq priority queue usage
        # TODO: include other costs like turn delay and bearing checks
        return self.f > other.f

    def __repr__(self) -> str:
        # For printing purposes
        return 'Node information: ' \
               f'(x, y) - ({self.point[0]}, {self.point[1]}), ' \
               f'g - {self.g}, ' \
               f'h - {self.h}, ' \
               f'f - {self.f}, ' \
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
        self.robot_movements = []
        # self.robot_initial_position = None
        # self.robot_destination_position = None
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
        end_time = None

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

            # TODO: Include direction as well
            neighbour_node = Node(neighbour_point, parent_node=visiting_node)

            # TODO: Include direction as well
            if self._is_not_a_valid_path(neighbour_node):
                continue

            # TODO: Include direction as well
            self._update_neighbour_node_costs(visiting_node, neighbour_node, goal_node)

    def _update_neighbour_node_costs(self, visiting_node: Node, neighbour_node: Node, goal_node: Node) -> None:
        """
        Updates the neighbour node's g, h and f cost and add to the priority queue.
        Replaces the node if found in the priority queue and the cost is lower

        :param visiting_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :param goal_node: Expects a way point Node object or the goal node object
        """
        # update neighbour's g, h and f
        # TODO: Include direction as well
        neighbour_node.g = self._get_g_cost(visiting_node, neighbour_node)
        neighbour_node.h = self._get_h_cost(visiting_node, goal_node)
        neighbour_node.f = neighbour_node.g + neighbour_node.h

        if neighbour_node not in self.open_list:
            # TODO: Include direction as well
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
        # TODO: Include direction as well

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

        # TODO: Include direction as well
        if neighbour_node in self.closed_list or \
                self._is_not_within_range_with_virtual_wall(neighbour_node.point) or \
                self._node_is_obstacle_or_virtual_wal(neighbour_node.point):
            return True

        return False

    def _is_not_within_range_with_virtual_wall(self, point: CoordinateList) -> bool:
        """
        Determines if the coordinate of the node is within the arena range

        :param point: The (x, y) coordinate of the current node
        :return: True if the coordinate is within the range of the arena
        """

        return not (0 < point[0] < constants.ARENA_HEIGHT - 1 and
                    0 < point[1] < constants.ARENA_WIDTH - 1) or \
               self._node_is_obstacle_or_virtual_wal(point)

    def _node_is_obstacle_or_virtual_wal(self, point: CoordinateList) -> bool:
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
            # TODO: Include direction as well

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

        return self._is_not_within_range_with_virtual_wall(start_point) or \
               self._is_not_within_range_with_virtual_wall(way_point) or \
               self._is_not_within_range_with_virtual_wall(goal_point)

    def _get_g_cost(self, current_node: Node, neighbour_node: Node) -> int:
        """
        The cost to move from the current node to the neighbouring node

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: g cost
        """
        # TODO: Consider direction cost and other misc as well
        return current_node.g + 1

    def _get_h_cost(self, current_node: Node, goal_node: Node) -> int:
        """
        The distance (heuristic) cost from the current node to the goal node.

        :param current_node: The cheapest cost node popped from the priority queue
        :param goal_node: Expects a way point Node object or the goal node object
        :return: h cost
        """
        return abs(current_node.point[0] - goal_node.point[0]) + abs(
            current_node.point[1] - goal_node.point[1])
