import json
from docplex.mp.model import Model
import cplex
import csv
import numpy as np
import folium


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
max_distance = int(input('Please input the max distance round trip you are willing to travel: '))

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

# max path length before completing tour
n = len(resorts)
u_vars = {}
for resort_name in resort_vars:
    u_vars[resort_name] = mdl.integer_var(0, n - 1, f"u_{resort_name}")

# choose first resort
found = False
depot_name = ''

while not found:
    depot_name = input('Please enter a starting resort:')
    if depot_name in all_resort_names:
        found = True
    else:
        print('Invalid name')
        print('Here are the available resorts:')
        for resort in all_resort_names:
            print(resort)


mdl.add_constraint(resort_vars[depot_name] == 1)
mdl.add_constraint(u_vars[depot_name] == 0)

M = n
for edge_name, edge_var in edge_vars.items():
    start, end = edge_name.split("->")
    if end != depot_name:

        # M * 1 - edge_var = if edge is not used it will be 0, 0 + len(resorts)

        # making sure the end of the edge comes before the start of the edge

        # M is just used to handle when edge is not used

        mdl.add_constraint(u_vars[end] - u_vars[start] + M * (1 - edge_var) >= 1)


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

resorts_by_name = {resort["name"]: resort for resort in resorts}

m = folium.Map(location=[resorts_by_name[depot_name]["lat"], resorts_by_name[depot_name]["lon"]], zoom_start=6) # center on starting location

# dark visited resorts
for resort in resorts:
  name = resort["name"]
  if solution[resort_vars[name]] == 1:
      folium.Marker(
          location=[resort["lat"], resort["lon"]],
          popup=name,
          icon=folium.Icon(color="green")
      ).add_to(m)

# draw tour edges
for edge_name, edge_var in edge_vars.items():
  if solution[edge_var] == 1:
      start, end = edge_name.split("->")
      start_resort = next(r for r in resorts if r["name"] == start)
      end_resort = next(r for r in resorts if r["name"] == end)
      folium.PolyLine(
          [[start_resort["lat"], start_resort["lon"]],
           [end_resort["lat"], end_resort["lon"]]],
          color="blue", weight=2
      ).add_to(m)

m.save("optimal_trip.html")



