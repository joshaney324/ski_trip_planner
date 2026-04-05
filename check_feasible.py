def check_feasible(solution, edge_vars, resort_vars, distances_dict, depot, max_distance):
    valid = True
    edges = {}
    distance_traveled = 0

    resorts_visited = set()

    for edge_name, edge_var in edge_vars.items():
        if solution[edge_var] == 1:
            start, end = edge_name.split("->")
            edges[start] = end

    last_resort = depot
    curr_resort = edges[depot]
    while curr_resort != depot:
        if curr_resort in resorts_visited:
            print('visited resort twice!')
            valid = False
            break

        resorts_visited.add(curr_resort)
        distance_traveled += distances_dict[last_resort + '->' + curr_resort]

        last_resort = curr_resort
        curr_resort = edges[last_resort]

    if distance_traveled > max_distance:
        valid = False
        print('Traveled farther than max distance!')


    return valid