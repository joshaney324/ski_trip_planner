import math
import time
from docplex.mp.model import Model


def solve_pctsp_cplex(resorts, snow_24h, snow_7d, distances_dict, depot_name, max_distance, max_time=600, verbose=False):
    start = time.time()

    def remaining():
        return max_time - (time.time() - start)

    def check_budget(stage):
        if remaining() <= 0:
            raise TimeoutError(f"Budget exceeded during {stage}")

    try:
        mdl = Model(name="pctsp")
        if verbose:
            print("Adding resort vars")

        resort_vars = {}
        for i, resort in enumerate(resorts):
            resort_vars[resort["name"]] = mdl.integer_var(0, 1, resort["name"])

            if i % 1000 == 0:
                check_budget("adding resort variables")

        if verbose:
            print("Adding edge vars")

        edge_vars = {}
        for i, edge_name in enumerate(distances_dict):

            edge_vars[edge_name] = mdl.integer_var(0, 1, edge_name)

            if i % 1000000 == 0:
                if verbose:
                    print("Added " + str(i) + " edge variables")

                check_budget("adding edge variables")

        if verbose:
            print("adding distance constraint")

        distance_sum = mdl.sum(distances_dict[e] * edge_vars[e] for e in edge_vars)
        mdl.add_constraint(distance_sum <= max_distance)
        check_budget("adding distance constraint")

        if verbose:
            print("adding incoming and outcoming edge constraint if visited resort")

        outgoing = {name: [] for name in resort_vars}
        incoming = {name: [] for name in resort_vars}
        for i, (edge_name, edge_var) in enumerate(edge_vars.items()):
            start_node, end_node = edge_name.split("->")
            outgoing[start_node].append(edge_var)
            incoming[end_node].append(edge_var)

            if i % 1000000 == 0:
                check_budget("bucketing incoming/outgoing edges")

        for i, (resort_name, resort_var) in enumerate(resort_vars.items()):
            mdl.add_constraint(resort_var == mdl.sum(outgoing[resort_name]))
            mdl.add_constraint(resort_var == mdl.sum(incoming[resort_name]))

            if i % 1000 == 0:
                check_budget("adding flow constraints")

        if verbose:
            print("Adding resort ordering vars")

        n = len(resorts)
        u_vars = {}
        for i, resort_name in enumerate(resort_vars):
            u_vars[resort_name] = mdl.integer_var(0, n - 1, f"u_{resort_name}")

            if i % 1000 == 0:
                check_budget("adding ordering variables")

        if verbose:
            print("Adding depot visited constraint")

        mdl.add_constraint(resort_vars[depot_name] == 1)
        mdl.add_constraint(u_vars[depot_name] == 0)

        if verbose:
            print("Added depot visited constraint")

        if verbose:
            print("Adding edge ordering constraints")

        M = n
        for i, (edge_name, edge_var) in enumerate(edge_vars.items()):
            start_node, end_node = edge_name.split("->")
            if end_node != depot_name:
                # M * 1 - edge_var = if edge is not used it will be 0, 0 + len(resorts)

                # making sure the end of the edge comes before the start of the edge

                # M is just used to handle when edge is not used

                mdl.add_constraint(u_vars[end_node] - u_vars[start_node] + M * (1 - edge_var) >= 1)

            if i % 1000000 == 0:
                check_budget("adding MTZ ordering constraints")

        if verbose:
            print("Added edge ordering constraints")

        # objective
        mdl.maximize(mdl.sum(
            (0.5 * snow_24h[resort_name] + 0.5 * snow_7d[resort_name]) * resort_var for resort_name, resort_var in
            resort_vars.items()))

        build_time = time.time() - start
        solve_budget = remaining()
        if solve_budget <= 0:
            raise TimeoutError(f"Budget exceeded before solve (build took {build_time:.1f}s)")

        mdl.parameters.timelimit.set(max(1.0, solve_budget))

        if verbose:
            print(f'Finding optimal trip... (build took {build_time:.1f}s, {solve_budget:.1f}s left for solve)')
        solution = mdl.solve(log_output=verbose)

        total_elapsed = time.time() - start

        if solution is None:
            return {
                "solution": None,
                "status": mdl.solve_details.status if mdl.solve_details else "no_solution",
                "elapsed": total_elapsed,
                "build_time": build_time,
                "solve_time": total_elapsed - build_time,
                "upper_bound": mdl.solve_details.best_bound if mdl.solve_details else math.inf,
            }

        print("Objective value:", solution.objective_value)

        total_traveled = 0
        tour_edges = []
        for edge_name, edge_var in edge_vars.items():
            if solution[edge_var] == 1:
                if verbose:
                    print(edge_name + ' distance: ' + str(distances_dict[edge_name]))
                total_traveled += distances_dict[edge_name]
                tour_edges.append(edge_name)

        visited_resorts = [name for name, var in resort_vars.items() if solution[var] == 1]

        if verbose:
            print("Total traveled distance:", total_traveled)

        return {
            "solution": solution,
            "status": mdl.solve_details.status,
            "elapsed": total_elapsed,
            "build_time": build_time,
            "solve_time": total_elapsed - build_time,
            "objective": solution.objective_value,
            "total_distance": total_traveled,
            "tour_edges": tour_edges,
            "visited_resorts": visited_resorts,
            "upper_bound": mdl.solve_details.best_bound if mdl.solve_details else math.inf,
        }

    except TimeoutError as e:
        elapsed_at_timeout = time.time() - start
        if verbose:
            print(f"CPLEX timed out: {e}")
        return {
            "solution": None,
            "status": f"timeout: {e}",
            "elapsed": elapsed_at_timeout,
            "build_time": elapsed_at_timeout,
            "solve_time": 0.0,
            "upper_bound": math.inf,
        }