import heapq
from typing import List, Optional

from utils import constants
from utils.enums import Cell, Direction, Movement
from utils.logger import print_general_log, print_error_log

INFINITE_COST = 999999
CoordinateList = List[int]  # x, y


class Node:
    """
    A class to keep track of the fastest path from start to end goal
    """

    def __init__(self,
                 point: CoordinateList,
                 direction_facing: Direction = None,
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
    def __init__(self, arena: List[int]) -> None:
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
        self.arena = arena
        self.facing_direction = None

    def run_algorithm(self,
                      start_point: CoordinateList,
                      way_point: CoordinateList,
                      goal_point: CoordinateList,
                      direction_facing: Direction) -> Optional[list]:
        """
        Finds the fastest path from the start point to the way point
        and from the way point to the end point.

        :param start_point: The starting point of the robot
        :param way_point: The way point provided by the Android device
        :param goal_point: The goal point
        :param direction_facing: Current facing direction of the robot
        :return: A list of nodes for the fastest path search OR None if the provided points are out of range
        """

        # TODO: Consider cases such as start point = way point or way point = end point
        if self._given_points_are_out_of_range(start_point, way_point, goal_point):
            print_error_log('Start, Way Point or Goal coordinates are out of range')
            return

        self._initialise_nodes(direction_facing, goal_point, start_point, way_point)

        heapq.heappush(self.open_list, self.start_node)

        path_found = self._find_fastest_path(goal_node=self.way_point_node)

        if not path_found:
            print_error_log(f'No fastest path found from start to waypoint.')
            return

        self.start_node = self.way_point_node
        self.open_list.clear()
        heapq.heappush(self.open_list, self.closed_list.pop())
        self.closed_list.clear()

        goal_found = self._find_fastest_path(goal_node=self.goal_node)

        if not goal_found:
            print_error_log(f'No fastest path found from waypoint to end.')
            return

        self._rebuild_fastest_path_route()

        # reset to base config and other misc
        self.open_list.clear()
        self.closed_list.clear()

        return self.path[1:]

    def _initialise_nodes(self, direction_facing, goal_point, start_point, way_point=None) -> None:
        """
        Prepares the nodes and direction required to find the fastest path to the goal

        :param direction_facing: Current facing direction of the robot
        :param goal_point: The goal point
        :param start_point: The starting point of the robot
        :param way_point: The way point provided by the Android device if it is provided. Else None
        """
        self.start_node = Node(start_point, direction_facing)
        self.way_point_node = Node(way_point) if way_point is not None else None
        self.goal_node = Node(goal_point)
        self.start_node.g = 0
        self.start_node.h = self.get_h_cost(self.start_node,
                                            self.way_point_node if way_point is not None else self.goal_node)
        self.start_node.f = self.start_node.g + self.start_node.h
        self.facing_direction = direction_facing

        if len(self.path) > 0:  # clears the previous fastest path record if the algorithm was ran previously
            self.path.clear()

    def run_algorithm_for_exploration(self, start_point, goal_point, direction_facing) -> Optional[list]:
        """
        Finds the fastest path to the destination point. The method finds the fastest path to the goal point without
        going through the way point, unlike the run_algorithm method where it requires a way point.

        :param start_point: The starting point of the robot
        :param goal_point: The goal point
        :param direction_facing: Current facing direction of the robot
        :return:
        """
        self._initialise_nodes(direction_facing, goal_point, start_point)

        heapq.heappush(self.open_list, self.start_node)

        path_found = self._find_fastest_path(goal_node=self.goal_node)

        if not path_found:
            print_error_log(f'No fastest path found from start to goal.')
            return

        self._rebuild_fastest_path_route()
        self.open_list.clear()
        self.closed_list.clear()

        # Discard the first node in the list as it is the node of the robot's position
        return self.path[1:]

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
        neighbour_node.h = self.get_h_cost(neighbour_node, goal_node)
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

        return self.arena[x][y] != Cell.FREE_AREA

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

        return constants.MOVE_COST + turn_cost + current_node.g

    def _get_neighbour_direction(self, current_node: Node, neighbour_node: Node) -> int:
        """
        Determines the direction required to reach the neighbouring node

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: The constant value of direction required to reach the neighbouring node
        """
        if neighbour_node.point[0] - current_node.point[0] > 0:
            return Direction.SOUTH

        if neighbour_node.point[1] - current_node.point[1] > 0:
            return Direction.EAST

        if neighbour_node.point[0] - current_node.point[0] < 0:
            return Direction.NORTH

        else:
            return Direction.WEST

    def _get_direction_cost_from_bearing(self, current_node: Node, neighbour_node: Node) -> int:
        """
        Determines the turn cost required to reach the neighbouring node.
        The larger the turn, the higher the cost.

        :param current_node: The cheapest cost node popped from the priority queue
        :param neighbour_node: The neighbouring node of the cheapest cost node
        :return: Turn cost to reach the neighbouring node
        """
        if current_node.direction_facing == neighbour_node.direction_facing:
            return constants.NO_TURN_COST

        turn_costs = [constants.TURN_COST_PERPENDICULAR, constants.TURN_COST_OPPOSITE_DIRECTION]

        previous_bearing = Direction.get_anti_clockwise_direction(current_node.direction_facing)
        next_bearing = Direction.get_clockwise_direction(current_node.direction_facing)

        for i in range(len(turn_costs)):
            if previous_bearing == neighbour_node.direction_facing or \
                    next_bearing == neighbour_node.direction_facing:
                return turn_costs[i]

            previous_bearing = Direction.get_anti_clockwise_direction(previous_bearing)
            next_bearing = Direction.get_clockwise_direction(next_bearing)

    @staticmethod
    def get_h_cost(neighbour_node: Node, goal_node: Node) -> int:
        """
        The distance (heuristic) cost from the neighbouring node to the goal node.

        :param neighbour_node: The neighbouring node of the cheapest cost node
        :param goal_node: Expects a way point Node object or the goal node object
        :return: h cost
        """

        return abs(neighbour_node.point[0] - goal_node.point[0]) + abs(
            neighbour_node.point[1] - goal_node.point[1])

    def set_map(self, new_arena_map):
        self.arena = new_arena_map

    def convert_fastest_path_movements_to_string(self, fastest_path_movements: List[Movement]) -> str:
        """
        Converts the list of movements to string. Used as string commands to send the fastest path movements to the RPI

        :param fastest_path_movements: The list of fastest path movements to direct the RPI
        :return: A string representation of the fastest path movements
        """

        # TODO: Discuss and set the separator for RPI
        return ','.join(map(Movement.to_string, fastest_path_movements))

    def convert_fastest_path_to_movements(self, fastest_path: List[Node], robot_direction) -> List[Movement]:
        """
        Converts the list of fastest path directions to a list of movements

        :param fastest_path: the fastest path solved from the algorithm
        :param robot_direction: The current direction of the robot
        :return: The list of movements from the fastest path
        """
        list_of_movements = []
        robot_facing_direction = robot_direction

        for node in fastest_path:
            # no_of_right_rotations = (node.direction_facing - robot_facing_direction) % 8
            no_of_right_rotations = Direction.get_no_of_right_rotations_to_destination_cell(robot_facing_direction,
                                                                                            node.direction_facing)

            if no_of_right_rotations == 2:
                list_of_movements.append(Movement.RIGHT)
            elif no_of_right_rotations == 4:
                list_of_movements.append(Movement.RIGHT)
                list_of_movements.append(Movement.RIGHT)
            elif no_of_right_rotations == 6:
                list_of_movements.append(Movement.LEFT)

            list_of_movements.append(Movement.FORWARD)
            robot_facing_direction = node.direction_facing

        return list_of_movements

    def consolidate_movements_to_string(self, fastest_path_movements: List['Movement']) -> str:
        movements = []
        consecutive_same_movements = 1

        # Arduino format for movement: Movement_|, where _ is the number of consecutive movement
        # E.g Forward x# = F3|
        movement_string = Movement.to_string(fastest_path_movements[0]) + f'{consecutive_same_movements}|'
        movements.append(movement_string)

        for i in range(1, len(fastest_path_movements)):
            if fastest_path_movements[i - 1] != fastest_path_movements[i]:
                # If the previous movement is not the same as the current movement,
                # reset the number of consecutive movements to 1 and append it to the movements list
                consecutive_same_movements = 1
                movement_string = Movement.to_string(fastest_path_movements[i]) + f'{consecutive_same_movements}|'
                movements.append(movement_string)

                continue

            consecutive_same_movements += 1
            latest_movement_string = movements[-1]
            updated_movement_string = latest_movement_string[0] + f'{consecutive_same_movements}|'
            movements[-1] = updated_movement_string

        return ''.join(movements)


if __name__ == '__main__':
    from map import Map

    map_object = Map()
    # test_map = map_object.sample_arena

    p1, p2 = map_object.load_map_from_disk('../maps/sample_arena_4.txt')
    test_map = map_object.decode_map_descriptor_for_fastest_path_task(p1, p2)

    Map.set_virtual_walls_on_map(test_map)

    solver = AStarAlgorithm(test_map)

    # way_point = [5, 5]
    way_point = [4, 3]
    direction = Direction.NORTH

    path = solver.run_algorithm(constants.ROBOT_START_POINT,
                                way_point,
                                constants.ROBOT_END_POINT,
                                direction)

    # Simulate setting a new arena map to find fastest path
    # solver.set_map(test_map)
    # path = solver.run_algorithm_for_exploration(constants.ROBOT_START_POINT,
    #                                             constants.ROBOT_END_POINT,
    #                                             direction)

    if path:
        list_of_movements = solver.convert_fastest_path_to_movements(path, direction)
        # list_of_movements = [Movement.FORWARD, Movement.FORWARD, Movement.RIGHT, Movement.RIGHT]
        test = solver.consolidate_movements_to_string(list_of_movements)
        for movement in list_of_movements:
            print(movement)
        print(test)
        # for row in path:
        #     x, y = row.point
        #     test_map[x][y] = 5
        # print(movements)
        # for row in test_map:
        #     print(row)
    else:
        print("Nothing boii!!! Fix your stuff :' ^    )")
