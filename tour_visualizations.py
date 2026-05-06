import random
from pathlib import Path

import folium

from pctsp_cplex import solve_pctsp_cplex
from pctsp_genetic_algorithm import generate_edges, get_meta_data, genetic_algorithm

dataset_root = Path("dataset_mini")
max_distance = 3000

resorts, resort_names, snow_7d, snow_24h, distances_dict = get_meta_data(dataset_root)
resorts_by_name = {r["name"]: r for r in resorts}

depot_name = random.choice(resort_names)

# solve cplex
cplex_output = solve_pctsp_cplex(resorts, snow_24h, snow_7d, distances_dict, depot_name, max_distance, verbose=True)
upper_bound = cplex_output["upper_bound"]

# solve ga (Valid init, no repair)
ga_no_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, max_distance, 100, 0.2, 10,
                                        depot_name, 0.3, 500000, 10, upper_bound, max_time=120, valid_init=True, repair_all=False, verbose=True)
print(f"ga best fitness no repair: {ga_no_repair_output['population'][0][0] if ga_no_repair_output['population'] else 'n/a'}")

# solve ga (Valid init, repair)
ga_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, max_distance, 100, 0.2, 10,
                                     depot_name, 0.3, 500000, 10, upper_bound, max_time=120, valid_init=True, repair_all=True, verbose=True)
print(f"ga best fitness repair: {ga_repair_output['population'][0][0] if ga_repair_output['population'] else 'n/a'}")


def render_tour(tour_edges, visited_names, depot, output_path, line_color):
    depot_resort = resorts_by_name[depot]
    m = folium.Map(location=[depot_resort["lat"], depot_resort["lon"]], zoom_start=6)

    for name in visited_names:
        resort = resorts_by_name[name]
        marker_color = "red" if name == depot else "green"
        folium.Marker(
            location=[resort["lat"], resort["lon"]],
            popup=name,
            icon=folium.Icon(color=marker_color),
        ).add_to(m)

    for edge_name in tour_edges:
        start, end = edge_name.split("->")
        start_resort = resorts_by_name[start]
        end_resort = resorts_by_name[end]
        folium.PolyLine(
            [[start_resort["lat"], start_resort["lon"]],
             [end_resort["lat"], end_resort["lon"]]],
            color=line_color, weight=2,
        ).add_to(m)

    m.save(output_path)
    print(f"Saved {output_path}")


# CPLEX tour
if cplex_output.get("tour_edges"):
    render_tour(
        cplex_output["tour_edges"],
        cplex_output["visited_resorts"],
        depot_name,
        "example_outputs/tour_cplex.html",
        line_color="blue",
    )
else:
    print("CPLEX produced no solution; skipping map.")

# GA (no repair) tour
if ga_no_repair_output["population"]:
    best_chromosome = ga_no_repair_output["population"][0][1]
    edges = generate_edges(best_chromosome)
    visited = list(dict.fromkeys(best_chromosome))
    render_tour(edges, visited, depot_name, "example_outputs/tour_ga_no_repair.html", line_color="orange")
else:
    print("GA (no repair) produced no solution; skipping map.")

# GA (repair) tour
if ga_repair_output["population"]:
    best_chromosome = ga_repair_output["population"][0][1]
    edges = generate_edges(best_chromosome)
    visited = list(dict.fromkeys(best_chromosome))
    render_tour(edges, visited, depot_name, "example_outputs/tour_ga_repair.html", line_color="purple")
else:
    print("GA (repair) produced no solution; skipping map.")