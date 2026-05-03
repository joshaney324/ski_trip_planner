from generate_dataset import create_dataset
from pctsp_cplex import *
from pctsp_genetic_algorithm import *
import pickle

dataset_sizes = [20, 50, 100, 200, 300, 400, 500, 1000, 5000]

# experiments

cplex_outputs = []
ga_no_repair_outputs = []
ga_repair_outputs = []

def cplex_picklable(d):
    return {k: v for k, v in d.items() if k != "solution"}

def save_results():
    with open("results/results.pkl", "wb") as f:
        pickle.dump({
            "cplex": [cplex_picklable(d) for d in cplex_outputs],
            "ga_no_repair": ga_no_repair_outputs,
            "ga_repair": ga_repair_outputs,
        }, f)

for dataset_size in dataset_sizes:
    try:
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
        ga_no_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, 3000, 100, 0.2, 20,
                                                depot_name, 0.3, 1000000, 10, upper_bound, valid_init=True, repair_all=False, verbose=False)

        pop = ga_no_repair_output["population"]
        print(f"ga best fitness no repair: {pop[0][0] if pop else 'n/a'}")

        ga_no_repair_outputs.append(ga_no_repair_output)

        # solve ga (Valid init, repair)
        ga_repair_output = genetic_algorithm(resort_names, snow_7d, snow_24h, distances_dict, 3000, 100, 0.2, 20,
                                             depot_name, 0.3, 1000000, 10, upper_bound, valid_init=True, repair_all=True, verbose=False)

        pop = ga_repair_output["population"]
        print(f"ga best fitness repair: {pop[0][0] if pop else 'n/a'}")

        ga_repair_outputs.append(ga_repair_output)

    except Exception as e:
        print(f"dataset_size={dataset_size} failed: {type(e).__name__}: {e}")

    # checkpoint after each size so a later crash doesn't wipe earlier results
    save_results()

