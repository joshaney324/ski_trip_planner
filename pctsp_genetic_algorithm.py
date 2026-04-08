import csv
import json
import random
from pathlib import Path

import numpy as np


def genetic_algorithm(all_resort_names, snow_7d, snow_24h, distances_dict, max_distance, population_size,
                      scaling_factor, mutation_rate, max_num_genes, depot, chance, max_iters, tournament_size,
                      valid_init=True, repair_all=False):
    population = generate_population(population_size, all_resort_names, max_num_genes, depot, chance, distances_dict,
                                     max_distance, valid_init)
    population_fitness = get_pop_fitness(population, snow_7d, snow_24h, max_distance, scaling_factor, distances_dict)

    for i in range(max_iters):

        chromosome1, chromosome2 = tournament(population_fitness, tournament_size)
        new_chromosome = crossover(chromosome1[1], chromosome2[1])

        if random.random() < mutation_rate:
            new_chromosome = mutate(new_chromosome, all_resort_names)

        if repair_all:
            new_chromosome = repair(new_chromosome, distances_dict, snow_7d, snow_24h, max_distance)

        population.append(new_chromosome)
        population_fitness = get_pop_fitness(population, snow_7d, snow_24h, max_distance, scaling_factor,
                                             distances_dict)
        population_fitness = population_fitness[:-1]
        population = [chromosome[1] for chromosome in population_fitness]

        if i % 5000 == 0:
            idv = population_fitness[0]
            fitness = idv[0]
            edges = generate_edges(idv[1])
            print("Best Fitness at iteration " + str(i) + ": " + str(fitness))
            print("Total Distance Traveled: " + str(get_path_distance(edges, distances_dict)))

    return population


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
        next(reader)
        distance = [[float(v) for v in row[1:]] for row in reader]

    distances = np.array(distance)

    distances_dict = {}

    for i, row in enumerate(distances):
        row_name = resorts[i]["name"]
        for j, col in enumerate(row):
            col_name = resorts[j]["name"]

            if row_name != col_name:
                edge_name = row_name + "->" + col_name
                distances_dict[edge_name] = distances[i][j]

    return all_resort_names, snow_7d, snow_24h, distances_dict


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
        change_range.insert(location, new_resort)
    else:
        change_range.pop(random.randrange(len(change_range)))

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


def generate_population(population_size, all_resort_names, max_num_genes, depot, chance, distances_dict, max_distance, valid_init):
    population = []

    while len(population) < population_size:
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

    return population


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
    max_distance = 2000

    population = genetic_algorithm(all_resort_names, snow_7d, snow_24h, distances_dict, max_distance, 100, 30, 0.05,
                                   20,
                                   depot, 0.5, 50000, 10, repair_all=True)

    best_individual = population[0]
    edges = generate_edges(best_individual)
    total_distance = get_path_distance(edges, distances_dict)

    best_fitness = fitness_function(edges, snow_7d, snow_24h, total_distance, max_distance, 0.5)
    print("Best fitness:", best_fitness)
    print("Total distance:", total_distance)
    print(edges)


if __name__ == "__main__":
    main()
