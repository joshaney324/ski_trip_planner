import csv
import json
import random
import time
from pathlib import Path

import numpy as np


def genetic_algorithm(all_resort_names, snow_7d, snow_24h, distances_dict, max_distance, population_size, mutation_rate,
                      max_num_genes, depot, chance, max_iters, tournament_size, upper_bound,
                      valid_init=True, repair_all=False, max_time=600, verbose=False, ):
    start = time.time()

    def elapsed():
        return time.time() - start

    population, init_timed_out = generate_population(population_size, all_resort_names, max_num_genes, depot, chance,
                                                     distances_dict, max_distance, valid_init,
                                                     start=start, max_time=max_time)

    if init_timed_out and not population:
        return {
            "population": [],
            "best_fitnesses": [],
            "pop_fitness_avgs": [],
            "status": "timeout: population init produced no individuals",
            "elapsed": elapsed(),
            "iterations_completed": 0,
        }

    max_total_prize = sum(0.5 * snow_7d[r] + 0.5 * snow_24h[r] for r in all_resort_names)
    scaling_factor = max_total_prize

    # base_factor = max_total_prize / (max_distance * 100)

    population_fitness = get_pop_fitness(population, snow_7d, snow_24h, max_distance, scaling_factor, distances_dict)

    pop_fitness_avgs = []
    best_fitnesses = []
    status = "completed"
    iterations_completed = 0

    for i in range(max_iters):
        if elapsed() >= max_time:
            status = f"timeout: hit {max_time}s after {i} iterations"
            print(status)
            break

        chromosome1, chromosome2 = tournament(population_fitness, tournament_size)
        new_chromosome = crossover(chromosome1[1], chromosome2[1])

        if random.random() < mutation_rate:
            new_chromosome = mutate(new_chromosome, all_resort_names)

        if repair_all:
            new_chromosome = repair(new_chromosome, distances_dict, snow_7d, snow_24h, max_distance)

        population.append(new_chromosome)

        # scaling_factor = base_factor * (1 + i / 1000) ** 2

        population_fitness = get_pop_fitness(population, snow_7d, snow_24h, max_distance, scaling_factor,
                                             distances_dict)
        # random replacement
        population_fitness.pop(random.randrange(len(population_fitness)))

        if population_fitness[0][0] >= upper_bound and i > 1:
            return {
                "population": population_fitness,
                "best_fitnesses": best_fitnesses,
                "pop_fitness_avgs": pop_fitness_avgs,
                "status": status,
                "elapsed": elapsed(),
                "iterations_completed": iterations_completed,
            }

        # elite replacement
        # population_fitness = population_fitness[:-1]

        population = [chromosome[1] for chromosome in population_fitness]
        iterations_completed = i + 1

        if i % 5000 == 0:
            idv = population_fitness[0]
            fitness = idv[0]
            avg_fitness = sum(t[0] for t in population_fitness) / len(population_fitness)
            best_fitnesses.append(fitness)
            pop_fitness_avgs.append(avg_fitness)
            edges = generate_edges(idv[1])
            if verbose:
                print("Best Fitness at iteration " + str(i) + ": " + str(fitness))
                print("Average Fitness: " + str(avg_fitness))
                print("Total Distance Traveled: " + str(get_path_distance(edges, distances_dict)))

    return {
        "population": population_fitness,
        "best_fitnesses": best_fitnesses,
        "pop_fitness_avgs": pop_fitness_avgs,
        "status": status,
        "elapsed": elapsed(),
        "iterations_completed": iterations_completed,
    }


def get_meta_data(dataset_root):
    with open(dataset_root / "ski_resorts.json") as f:
        resorts = json.load(f)["ski_resorts"]

    snow_24h = {}
    for resort in resorts:
        snow_24h[resort["name"]] = resort["snowfall_24hr_in"]

    snow_7d = {}
    for resort in resorts:
        snow_7d[resort["name"]] = resort["snowfall_7day_in"]

    all_resort_names = snow_24h.keys()

    # add edge vars
    with open(dataset_root / "resort_distances.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        distance = []
        for row in reader:
            # Some CSV variants prefix each row with a label; others don't.
            values = row[1:] if len(row) == len(header) else row
            distance.append([float(v) for v in values])

    distances = np.array(distance)

    distances_dict = {}

    for i, row in enumerate(distances):
        row_name = resorts[i]["name"]
        for j, col in enumerate(row):
            col_name = resorts[j]["name"]

            if row_name != col_name:
                edge_name = row_name + "->" + col_name
                distances_dict[edge_name] = distances[i][j]

    return resorts, list(all_resort_names), snow_7d, snow_24h, distances_dict


# fitness = sum_over_visited_resorts((.5 * 7d_snowfall) + (.5 * 24hr_snowfall))
def fitness_function(edges, snow_7d, snow_24h, total_distance, max_distance, scaling_factor):
    fitness = 0
    for edge in edges:
        start, end = edge.split("->")
        fitness += 0.5 * snow_7d[start] + 0.5 * snow_24h[start]

    return fitness - scaling_factor * max(0, total_distance - max_distance)


def mutate(chromosome, all_resort_names):
    change_range = chromosome[1:-1]
    depot = chromosome[0]

    if not change_range:
        return chromosome

    visited = set(change_range)
    nonvisited = list(set(all_resort_names) - visited - {depot})

    if not nonvisited:
        return chromosome

    location = random.randint(0, len(visited) - 1)
    new_resort = random.choice(nonvisited)

    if random.random() < 0.5:
        if random.random() < 0.5:
            change_range.insert(location, new_resort)
        else:
            change_range.pop(random.randrange(len(change_range)))
    else:
        if len(change_range) < 2:
            change_range.insert(location, new_resort)
        else:
            first_swap = random.randrange(0, len(change_range))
            second_swap = random.choice([i for i in range(len(change_range)) if i != first_swap])
            change_range[second_swap], change_range[first_swap] = change_range[first_swap], change_range[second_swap]

    change_range.insert(0, depot)
    change_range.append(depot)
    return change_range


def crossover(chromosome1, chromosome2):
    depot = chromosome1[0]

    chromosome1 = chromosome1[1:-1]
    chromosome2 = chromosome2[1:-1]

    max_length = max(len(chromosome1), len(chromosome2))
    chromosome1 += [None] * (max_length - len(chromosome1))
    chromosome2 += [None] * (max_length - len(chromosome2))

    new_chromosome = []

    for gene1, gene2 in zip(chromosome1, chromosome2):
        if random.random() < 0.5:
            new_chromosome.append(gene1)
        else:
            new_chromosome.append(gene2)

    seen = set()
    new_chromosome = [g for g in new_chromosome if g is not None and not (g in seen or seen.add(g))]

    new_chromosome.insert(0, depot)
    new_chromosome.append(depot)
    return new_chromosome


def generate_edges(chromosome):
    edges = []
    last_resort = chromosome[0]
    for i in range(len(chromosome[1:])):
        curr_resort = chromosome[i + 1]
        if last_resort != curr_resort:
            edges.append(last_resort + "->" + curr_resort)
        last_resort = curr_resort

    return edges


def generate_population(population_size, all_resort_names, max_num_genes, depot, chance, distances_dict, max_distance,
                        valid_init, start=None, max_time=None):
    population = []
    timed_out = False

    while len(population) < population_size:
        if start is not None and max_time is not None and (time.time() - start) >= max_time:
            timed_out = True
            print(f"Population init timed out after generating {len(population)}/{population_size} individuals")
            break

        remaining_resorts = set(all_resort_names)
        remaining_resorts.remove(depot)

        chromosome = []
        for j in range(max_num_genes - 2):
            if random.random() < chance:
                gene = random.choice(list(remaining_resorts))
                chromosome.append(gene)
                remaining_resorts.remove(gene)

        chromosome.insert(0, depot)
        chromosome.append(depot)
        if valid_init:
            if check_valid(chromosome, distances_dict, max_distance):
                population.append(chromosome)
        else:
            population.append(chromosome)

    return population, timed_out


def get_pop_fitness(population, snow_7d, snow_24h, max_distance, scaling_factor, distances_dict):
    pop_fitness = []
    for chromosome in population:
        edges = generate_edges(chromosome)
        total_distance = get_path_distance(edges, distances_dict)
        fitness = fitness_function(edges, snow_7d, snow_24h, total_distance, max_distance, scaling_factor)
        pop_fitness.append((fitness, chromosome))
    pop_fitness.sort(key=lambda x: x[0], reverse=True)
    return pop_fitness


def get_path_distance(edges, distances_dict):
    total_distance = 0
    for edge in edges:
        total_distance += distances_dict[edge]
    return total_distance


def tournament(pop_fitness, tournament_size):
    tournament_group = []

    for i in range(tournament_size):
        tournament_group.append(random.choice(pop_fitness))

    tournament_group.sort(key=lambda x: x[0], reverse=True)
    return tournament_group[0], tournament_group[1]


def check_valid(chromosome, distances_dict, max_distance):
    edges = generate_edges(chromosome)
    total_distance = get_path_distance(edges, distances_dict)
    if total_distance > max_distance:
        return False
    return True


def calc_detour(chromosome, distances_dict, snow_7d, snow_24h):
    detour = {}
    for i, stop in enumerate(chromosome[1:-1]):
        idx = i + 1
        prev = chromosome[idx - 1]
        next_ = chromosome[idx + 1]
        detour_cost = distances_dict[prev + '->' + stop] + distances_dict[stop + '->' + next_] - distances_dict.get(
            prev + '->' + next_, 0)
        prize = 0.5 * snow_7d[stop] + 0.5 * snow_24h[stop]
        detour[stop] = detour_cost / (prize + 0.00000001)
    return detour


def repair(chromosome, distances_dict, snow_7d, snow_24h, max_distance):
    while get_path_distance(generate_edges(chromosome), distances_dict) > max_distance:
        detour = calc_detour(chromosome, distances_dict, snow_7d, snow_24h)
        worst_stop = max(detour, key=detour.get)
        chromosome.remove(worst_stop)

    return chromosome


def main():
    dataset_root = Path("gigantic_dataset")
    all_resort_names, snow_7d, snow_24h, distances_dict = get_meta_data(dataset_root)

    # depot = input("Enter depot name: ")
    # max_distance = input("input max distance: ")

    depot = "Hoth Extreme Winter Sports Complex"
    max_distance = 3000

    result = genetic_algorithm(all_resort_names, snow_7d, snow_24h, distances_dict, max_distance, 100, 30, 0.2,
                               20, depot, 0.3, 100000, 10, valid_init=True, repair_all=True, max_time=600)

    print(f"Status: {result['status']}")
    print(f"Elapsed: {result['elapsed']:.1f}s, iterations: {result['iterations_completed']}")

    if not result["population"]:
        print("No individuals produced.")
        return

    best_individual = result["population"][0]
    edges = generate_edges(best_individual)
    total_distance = get_path_distance(edges, distances_dict)

    best_fitness = fitness_function(edges, snow_7d, snow_24h, total_distance, max_distance, 0.5)
    print("Best fitness:", best_fitness)
    print("Total distance:", total_distance)
    # print(edges)


if __name__ == "__main__":
    main()
