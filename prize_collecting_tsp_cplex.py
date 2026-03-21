import json
from docplex.mp.model import Model
import cplex
import csv
import numpy as np

print(cplex.__version__)

mdl = Model(name="pc_tsp_solver")

with open("dataset_mini/ski_resorts.json") as f:
    resorts = json.load(f)["ski_resorts"]

snow_24h = {}
for resort in resorts:
    snow_24h[resort["name"]] = resort["snowfall_24hr_in"]

snow_7d = {}
for resort in resorts:
    snow_7d[resort["name"]] = resort["snowfall_7day_in"]

all_resort_names = snow_24h.keys()

# add resort vars
resort_vars = {}
for resort in resorts:
    resort_vars[resort["name"]] = mdl.integer_var(0, 1, resort["name"])

# add edge vars
with open('dataset_mini/resort_distances.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    distance = [[float(v) for v in row[0:]] for row in reader]

distances = np.array(distance)
# print(distances.shape)

distances_dict = {}

for i, row in enumerate(distances):
    row_name = resorts[i]["name"]
    for j, col in enumerate(row):
        col_name = resorts[j]["name"]

        if row_name != col_name:
            edge_name = row_name + "->" + col_name
            distances_dict[edge_name] = distances[i][j]

edge_vars = {}
for edge_name in distances_dict:
    edge_vars[edge_name] = mdl.integer_var(0, 1, edge_name)

# constraints

# max distance constraint
max_distance = 1000

distance_sum = mdl.sum(distances_dict[e] * edge_vars[e] for e in edge_vars)

mdl.add_constraint(distance_sum <= max_distance)

# if a resort is visited edge coming in and out

for resort_name, resort_var in resort_vars.items():
    curr_var = resort_var
    curr_name = resort_var.name

    total_outgoing = 0
    total_incoming = 0

    for edge_name, edge_var in edge_vars.items():


        edge_endpoints = edge_name.split("->")
        start = edge_endpoints[0]
        end = edge_endpoints[1]

        if start == curr_name:
            total_outgoing += edge_var

        if end == curr_name:
            total_incoming += edge_var

    mdl.add_constraint(resort_var == total_outgoing)
    mdl.add_constraint(resort_var == total_incoming)
    mdl.add_constraint(total_incoming == total_outgoing)

# objective
mdl.maximize(mdl.sum((0.5 * snow_24h[resort_name] + 0.5 * snow_7d[resort_name]) * resort_var for resort_name, resort_var in resort_vars.items()))

solution = mdl.solve(log_output=False)

print("Objective value:", solution.objective_value)

# for resort_name, resort_var in resort_vars.items():
#     if solution[resort_var] == 1:
#         print(resort_name)

total_traveled = 0
for edge_name, edge_var in edge_vars.items():
    if solution[edge_var] == 1:
        print(edge_name + ' distance: ' + str(distances_dict[edge_name]))
        total_traveled += distances_dict[edge_name]

print("Total traveled distance:", total_traveled)

