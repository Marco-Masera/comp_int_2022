import random 
import numpy as np

#NP array containing N lists. Each list in position i contains the indexes of the original lists that covers element i
#i.e. if the number 0 is in the first and the third lists, elementsCovers will be [ [0, 2], ... ]
#That is just a way to easily access the information on what lists cover a given number.
elementCovers = None 
#NP array that contains the cost (= number of elements) of each list. Again it's just a fast way to access this information.
listsCost = None 

#Global configuration
N = 50
POPULATION_SIZE = 2000
TOURNAMENT_SIZE = 500
OFFSPRINGS = 4000
GENERATIONS = 140
MUTATIONS = 2


class Individual:
    #genome: a np array of N elements. Each element i is the index of one list that covers number i
    #Of course there can and should be repetitions.
    def __init__(self, genome):
        self.genome = genome 
    
    def fitness(self):
        cost = 0
        for i in set(self.genome):
            cost += listsCost[i]
        return cost 

    #Randomly mutates his own genome
    #each mutation consists in one element of the self.genome array changed
    def mutate(self, number_of_mutations):
        for i in range(0, number_of_mutations):
            target = random.randint(0, N-1)
            #The chosen genome contains the index of one lists covering the given number. We change it to a random list
            #that does the same
            self.genome[target] = elementCovers[target][random.randint(0, len(elementCovers[target])-1)]
    
    def get_copy(self):
        return Individual(np.copy(self.genome))


#Creates a third individual with genome mixed from the two parents
def mix_genomes(parent_1, parent_2):
    new_genome = np.empty((N,),dtype=np.int64)
    for i in range(0, N):
        new_genome[i] = (parent_1.genome[i], parent_2.genome[i])[random.randint(0,1)]
    return Individual(new_genome)

#Creates a random individual
def get_random_individual():
    new_genome = np.empty((N,),dtype=np.int64)
    for target in range(0, N):
        new_genome[target] = elementCovers[target][random.randint(0, len(elementCovers[target])-1)]
    return Individual(new_genome)


def execute():
    """POPULATION_SIZE = 10
    TOURNAMENT_SIZE = 4
    OFFSPRINGS = 3
    GENERATIONS = 10
    MUTATIONS"""
    best_individual = None
    #Creates first random individuals
    population = [get_random_individual() for i in range(0, POPULATION_SIZE)] 
    for generation in range(1, GENERATIONS):
        #Select the best ones - and keep track of the best so far
        population.sort(key = lambda i: i.fitness())
        population = population[0:TOURNAMENT_SIZE]
        new_generation = []
        p = np.array(population)

        if (best_individual == None or (best_individual.fitness() > p[0].fitness())):
                print(f"Found new best individual with cost {p[0].fitness()} at generation {generation}")
                best_individual = p[0].get_copy()

        for i in range(OFFSPRINGS):
            C_1 = p[random.randint(0, len(p)-1)]
            C_2 = p[random.randint(0, len(p)-1)]
            offspring = mix_genomes(C_1, C_2)
            offspring.mutate(random.randint(0, MUTATIONS))
            new_generation.append(offspring)
        population = new_generation

    #Alternative and less effective way to create new generations:
    """for generation in range(1, GENERATIONS):
        #Select the best ones - and keep track of the best so far
        population.sort(key = lambda i: i.fitness(), reverse = True)
        new_generation = []
        for i in range(int(TOURNAMENT_SIZE/2)):
            if (len(population)<=1):
                break 
            best_c = population.pop()
            second_b = population.pop()
            if (i == 0 and (best_individual == None or (best_individual.fitness() > best_c.fitness()))):
                print(f"Found new best individual with cost {best_c.fitness()} at generation {generation}")
                best_individual = best_c.get_copy()
            #Create offsprings
            for j in range(OFFSPRINGS):
                best_c.mutate(random.randint(0, MUTATIONS))
                second_b.mutate(random.randint(0, MUTATIONS))
                new_generation.append(mix_genomes(best_c, second_b))
            #new_generation.append(best_c)
        population = new_generation"""
    print(f"Best individual found has cost {best_individual.fitness()}")

    
            
    

def problem(N_, seed=None):
    global elementCovers
    global listsCost
    global N
    N = N_
    random.seed(seed)
    generated = [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]
    #Initialize the two global variables. Then we can forget about the generated lists, we don't need them anymore.
    listsCost = np.array([ len(s) for s in generated]) #Size of each list 
    elementCovers = A=np.empty((N,),dtype=object) #Initialize elementCovers as an empty array of python objects (don't need np array for inner lists)
    for index, l in enumerate(generated): #Initialize the inner lists of elementCovers with the indexes
        for element in l:
            if (elementCovers[element] == None):
                elementCovers[element] = [index]
            else:
                elementCovers[element].append(index)

def main():
    problem(N,42)
    execute()

if (__name__ == '__main__'):
    main()