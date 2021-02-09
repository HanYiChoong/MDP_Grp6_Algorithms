from algorithms.fastest_path_solver import AStarAlgorithm
from map import Map

map_object = Map()

solver = AStarAlgorithm(map_object.fastest_path_map_with_virtual_wall)

start_point = [18, 1]  # bottom left
way_point = [5, 5]
end_point = [1, 13]  # top right
direction = 0  # north

path = solver.run_algorithm(start_point, way_point, end_point, direction, False)
if path:
    for node in path:
        x, y = node.point
        map_object.fastest_path_map_with_virtual_wall[x][y] = 5

    for row in map_object.fastest_path_map_with_virtual_wall:
        print(row)

else:
    print("Nothing boii!!! Fix your stuff :' ^    )")
