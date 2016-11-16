import pong
import os
from time import time, sleep
from neat import nn, population, statistics, parallel
from sys import argv

ngen = 0
keyup = 'w'
keydown = 'd'

def eval_fitness(genomes):
    global ngen
    global keyup
    global keydown
    ngen += 1
    flag = False
    if ngen > int (argv[1]):
        flag = True
    for g in genomes:
        start = time()
        net = nn.create_feed_forward_phenotype(g)
        score = pong.main(net, flag, keyup, keydown)
        g.fitness = (time() - start)*(score + 1)

def main ():
    global ngen
    global keyup
    keyup = argv[2]
    global keydown
    keydown= argv[3]
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config')
    pop = population.Population(config_path)
    # pe = parallel.ParallelEvaluator(8, eval_fitness)
    pop.run(eval_fitness, 300)

    print('Number of evaluations: {0}'.format(pop.total_evaluations))

if __name__ == '__main__':
    main ()
