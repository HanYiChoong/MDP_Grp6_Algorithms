import map
from algorithms.fastest_path_solver import AStarAlgorithm

sample_arena = map.load_map_from_disk()
map.set_virtual_walls(sample_arena)

solver = AStarAlgorithm(sample_arena)

start_point = [18, 1]  # bottom left
way_point = [5, 5]
end_point = [1, 13]  # top right
direction = 0  # north

path = solver.run_algorithm(start_point, way_point, end_point, direction, False)
if path:
    for node in path:
        x, y = node.point
        sample_arena[x][y] = 5

    for row in sample_arena:
        print(row)

else:
    print("Nothing boii!!! Fix your stuff :' ^    )")
