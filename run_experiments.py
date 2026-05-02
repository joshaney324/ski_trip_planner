from generate_dataset import create_dataset
from pctsp_cplex import *
from pctsp_genetic_algorithm import *
import pickle

dataset_sizes = [5, 10, 20, 50, 100, 200, 500, 1000, 5000]

# experiments

cplex_outputs = []
ga_no_repair_outputs = []
ga_repair_outputs = []

for dataset_size in dataset_sizes:
    create_dataset(dataset_size)

    # load data
    dataset_root = Path("gigantic_dataset")
    resorts_dict, resort_names, snow_7d, snow_24h, distances_dict = get_meta_data(dataset_root)


    # solve cplex
    depot_name = random.choice(resort_names)
    output = solve_pctsp_cplex(resorts_dict, snow_24h, snow_7d, distances_dict, depot_name, 3000)
    cplex_outputs.append(output)

    # upper bound to compare GA
    upper_bound = output["upper_bound"]

    # solve ga (Valid init, no repair)
    ga_no_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, 3000, 100, 30, 0.2, 20,
                                            depot_name, 0.3, 1000000, 10, upper_bound, valid_init=True, repair_all=False, verbose=False)

    print("ga best fitness no repair:")
    print(ga_no_repair_output["best_fitnesses"][-1])

    ga_no_repair_outputs.append(ga_no_repair_output)

    # solve ga (Valid init, repair)
    ga_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, 3000, 100, 30, 0.2, 20,
                                         depot_name, 0.3, 1000000, 10, upper_bound, valid_init=True, repair_all=True, verbose=False)

    print("ga best fitness no repair:")
    print(ga_repair_output["best_fitnesses"][-1])

    ga_repair_outputs.append(ga_repair_output)

with open("results.pkl", "wb") as f:
    pickle.dump({
        "cplex": cplex_outputs,
        "ga_no_repair": ga_no_repair_outputs,
        "ga_repair": ga_repair_outputs,
    }, f)

# load later:
with open("results.pkl", "rb") as f:
    results = pickle.load(f)

