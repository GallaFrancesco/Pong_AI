from __future__ import print_function
import pong
import os
from time import time, sleep
from neat import nn, population, statistics, parallel


def eval_fitness(genomes):
    flag = False
    ch = input("Would you like to play? [y/n]\n")
    if ch == 'y':
        flag = True
    for g in genomes:
        start = time()
        net = nn.create_feed_forward_phenotype(g)
        score = pong.main(net, flag)
        g.fitness = (time() - start)*(score + 1)


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'neat_config')
pop = population.Population(config_path)
# pe = parallel.ParallelEvaluator(8, eval_fitness)
pop.run(eval_fitness, 300)

# Log statistics.
statistics.save_stats(pop.statistics)
statistics.save_species_count(pop.statistics)
statistics.save_species_fitness(pop.statistics)

print('Number of evaluations: {0}'.format(pop.total_evaluations))

# Show output of the most fit genome against training data.
winner = pop.statistics.best_genome()
print('\nBest genome:\n{!s}'.format(winner))
print('\nOutput:')
winner_net = nn.create_feed_forward_phenotype(winner)
