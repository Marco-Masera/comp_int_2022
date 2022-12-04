import os
import sys 
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))))
import numpy as np
import random
from PlayerBaseClass import PlayerBase
from GameState.GameState import *
from Strategies.NimSum import NimSum
if __name__=='main':
    from Instructors import  GenerousNimSum
    from learned_rules import learned_strategy
else:
    from Strategies.EvolvingRules.Instructors import GenerousNimSum
    from Strategies.EvolvingRules.learned_rules import learned_strategy



#These classes contains the default rules that agents can use
#for each class the get_strings() method returns the strings corresponding to the different rules,
# and get_function() returns the correct function given a string
class TransformationRules:
    def id(game:Nim) -> list:
        return list(game.rows)
    def modK(game:Nim) -> list:
        if (game.k == None):
            return game.rows 
        return [x%(game.k) for x in game.rows]
    def modK_plus1(game:Nim) -> list:
        if (game.k == None):
            return game.rows 
        return [x%(game.k+1) for x in game.rows]
    def power_2(game:Nim) -> list:
        return [x*x for x in game.rows]
    
    def get_function(name):
        return getattr(TransformationRules, name)
    def get_strings():
        return ["id", "modK", "modK_plus1", "power_2"]

class CumulativeValueRules:
    def xor_(transformed_list, k) -> int:
        v = 0
        for tuple in transformed_list: v = v ^ tuple
        return v
    def sum_(transformed_list, k) -> int:
        v = 0
        for tuple in transformed_list: v = v + tuple
        return v
    def avg_(transformed_list, k) -> int:
        v = 0
        for tuple in transformed_list: v = v + tuple
        return int(v/len(transformed_list))
    def min(transformed_list, k) -> int:
        return min(transformed_list)
    def max(transformed_list, k) -> int:
        return max(transformed_list)

    def get_function(name):
        return getattr(CumulativeValueRules, name)
    def get_strings():
        return ['xor_', 'sum_', 'avg_', 'min', 'max']


class SortingRules:
    def add_indexes_to_list(list) -> list:
        return [(item, index) for index, item in enumerate(list)]


    def min(transformed_list, k, accumulated) -> list:
        list = SortingRules.add_indexes_to_list(transformed_list)
        return sorted(list)
    def max(transformed_list, k, accumulated) -> list:
        list = SortingRules.add_indexes_to_list(transformed_list)
        return sorted(list, reverse=True)
    def xor_accumulated(transformed_list, k, accumulated) -> list:
        list = SortingRules.add_indexes_to_list(transformed_list)
        return sorted(list, reverse=True, key = lambda x: x[0] ^ accumulated)
    def mod_accumulated(transformed_list, k, accumulated) -> list:
        list = SortingRules.add_indexes_to_list(transformed_list)
        if (accumulated == 0): accumulated=1
        return sorted(list, reverse=True, key = lambda x: x[0] % accumulated)
    def mod_accumulated_plus1(transformed_list, k, accumulated) -> list:
        list = SortingRules.add_indexes_to_list(transformed_list)
        if (accumulated == -1): accumulated=0
        return sorted(list, reverse=True, key = lambda x: x[0] % (accumulated + 1))

    def get_function(name):
        return getattr(SortingRules, name)
    def get_strings():
        return ['min', 'max', 'xor_accumulated','mod_accumulated','mod_accumulated_plus1']


class SplitRules:
    def never_split(value, k, accumulated) -> bool:
        return True 
    def if_even(value, k, accumulated) -> bool:
        return (value%2) == 0 
    def if_acc_even(value, k, accumulated) -> bool:
        return (accumulated%2) == 0 
    def if_bigger_than_k(value, k, accumulated) -> bool:
        return (value > k)

    def get_function(name):
        return getattr(SplitRules, name)
    def get_strings():
        return ['never_split', 'if_even', 'if_acc_even', 'if_bigger_than_k']


class AmountRules:
    def always_one(value, k, accumulated) -> int:
        return 1
    def always_two(value, k, accumulated) -> int:
        if (value >= 2):
            return 2 
        return 1 #Yeah i know...
    def value_xor_acc(value, k, accumulated) -> int:
        return value ^ accumulated 
    def value_mod_acc(value, k, accumulated) -> int:
        if (accumulated==0):
            accumulated=1
        return value % accumulated 
    def value_mod_acc_plusone(value, k, accumulated) -> int:
        if (accumulated==0):
            accumulated = 1
        return value % accumulated + 1

    def target_xor_acc(value, k, accumulated) -> int:
        return value - (value ^ accumulated )
    def target_mod_acc(value, k, accumulated) -> int:
        if (accumulated==0):
            accumulated=1
        return value - (value % accumulated )
    def get_function(name):
        return getattr(AmountRules, name)
    def get_strings():
        return ['always_one', 'always_two', 'value_xor_acc', 'value_mod_acc', 'value_mod_acc_plusone', 'target_xor_acc','target_mod_acc']


class EvolvingAgent(PlayerBase):
    def __init__(self, genome):
        self.genome = genome

    def get_from_learned_strategy():
        return EvolvingAgent(learned_strategy)
    
    #Takes an object whose values are numbers. It returns it such as the sum of these numbers equals 1000
    def normalize_probabilities(object) -> object:
        categories = object.items()
        for category in categories:
            items = object[category[0]].items()
            sum = 0
            for it in items: sum += it[1]
            moltiplicator = 1000/sum 
            for it in items:
                object[category[0]][it[0]] = int(it[1] * moltiplicator)
        return object 
    #Creates a random genome
    def get_random_genome():
        def get_random_probability(vector) -> dict:
            ret = dict()
            for element in vector:
                ret[element] = random.randint(0, 1000)
            return ret

        genome = dict()
        genome['transformation'] = get_random_probability(TransformationRules.get_strings())
        genome['cumulative_value'] = get_random_probability(CumulativeValueRules.get_strings())
        genome['sorting'] = get_random_probability(SortingRules.get_strings())
        genome['split'] = get_random_probability(SplitRules.get_strings())
        genome['amount'] = get_random_probability(AmountRules.get_strings())
        genome['amount_alternative'] = get_random_probability(AmountRules.get_strings())
        genome = EvolvingAgent.normalize_probabilities(genome)
        return genome
    
    def get_choice(dict):
        r = random.randint(0, 1000)
        items = dict.items()
        for index, item in enumerate(items):
            r -= item[1]
            if (r <= 0 or index == len(items)-1):
                return item[0]
        items = list(items)
        print(items)
        return items[len(items)-1][0]

    def mix_genomes(genome_1, genome_2):
        new_gen = dict()
        for category in genome_1.items():
            if not category[0] in new_gen: new_gen[category[0]] = dict()
            for item in genome_1[category[0]].items():
                new_gen[category[0]][item[0]] = item[1]
        for category in genome_2.items():
            if not category[0] in new_gen: new_gen[category[0]] = dict()
            for item in genome_1[category[0]].items():
                new_gen[category[0]][item[0]] += item[1]
        EvolvingAgent.normalize_probabilities(new_gen)
        return new_gen
    def random_mutation(genome, num_mutations, mutation_size):
        mutation_size = mutation_size*10
        categories = list(genome.items())
        for i in range(num_mutations):
            category = categories[random.randint(0, len(categories)-1)][0]
            rules = list(genome[category].items())
            rule = rules[random.randint(0, len(rules)-1)][0]
            change = random.randint(-mutation_size, mutation_size)
            genome[category][rule] += change
            if (genome[category][rule] < 0):
                genome[category][rule] = 0
        genome = EvolvingAgent.normalize_probabilities(genome)
        return genome
        

    def play(self,game:Nim) -> MoveResult:
        game_k = game.k
        if (game_k == None):
            game_k = 90000
        #Find the rules to use
        transformation_func = EvolvingAgent.get_choice(self.genome['transformation'])
        cumulative_value_func = EvolvingAgent.get_choice(self.genome['cumulative_value'])
        sorting_function = EvolvingAgent.get_choice(self.genome['sorting'])
        split_function = EvolvingAgent.get_choice(self.genome['split'])
        amount_function = EvolvingAgent.get_choice(self.genome['amount'])
        amount_function_alt = EvolvingAgent.get_choice(self.genome['amount_alternative'])
        #Use the rules in order to execute an action
        transformed_list = TransformationRules.get_function(transformation_func)(game)
        cumulative_value = CumulativeValueRules.get_function(cumulative_value_func)(transformed_list, game_k)
        sorted_list = SortingRules.get_function(sorting_function)(transformed_list, game_k, cumulative_value)
        split_value = SplitRules.get_function(split_function)(sorted_list[0][0], game_k, cumulative_value)
        amount = -1
        if (split_value):
            amount = AmountRules.get_function(amount_function)(sorted_list[0][0], game_k, cumulative_value)
        else:
            amount = AmountRules.get_function(amount_function_alt)(sorted_list[0][0], game_k, cumulative_value)
        amount = min(game_k, amount)
        #Check if the decision is ok (should be most of times) - if it's not it uses a default decision
        if (game.rows[sorted_list[0][1]] >= amount and amount > 0):
            #Ok
            return game.nimming((sorted_list[0][1], amount))
        else:
            #Not ok - default move
            for index, row in enumerate(game.rows):
                if row >= 1:
                    return game.nimming((index, 1))



#Functions to evolve the agents
class AgentsGim:
    POPULATION_SIZE = 270
    SURVIVING_SIZE = 30
    OFFSPRING_SIZE = int(POPULATION_SIZE/SURVIVING_SIZE)
    NUM_MUTATION = 10
    MUTATION_SIZE = 13
    MAX_EPOCH_ONE_NOIMPROVEMENTS = 30
    MAX_EPOCH_ONE_GEN = 400

    MAX_EPOCH_TWO_GEN = 350
    
    K = 5
    NROWS = 7
    NIMSUM = NimSum()
    INSTRUCTORS = [GenerousNimSum(7), GenerousNimSum(9), GenerousNimSum(10), NIMSUM ]

    def match(individual_1, individual_2, nrows, k):
        players = (individual_1, individual_2); turn = 0 
        game = Nim(nrows, k)
        players[0].initialize(game); players[1].initialize(game)
        while(True):
            move_result = players[turn].your_turn(game)
            if move_result == MoveResult.Game_Over:
                break
            turn  = 1 - turn
        return 1 - turn #1 if player 0 wins, else 0

    def fight(individual: EvolvingAgent) -> int:
        victories = 0
        for instructor in AgentsGim.INSTRUCTORS:
            victories += AgentsGim.match(individual, instructor, AgentsGim.NROWS, AgentsGim.K)
            victories += AgentsGim.match(individual, instructor, AgentsGim.NROWS*2, AgentsGim.K*2)
        return victories

    def fight_epoch_2(individual: EvolvingAgent, others) -> int:
        victories = 0
        if (AgentsGim.match(individual, AgentsGim.NIMSUM, AgentsGim.NROWS, AgentsGim.K)==1):
            victories += 100 #if he beats NimSum he deserves high fitness

        for i in range(7):
            victories += AgentsGim.match(individual, others[random.randint(0, len(others)-1)][1], AgentsGim.NROWS, AgentsGim.K)
        return victories

    def evolve_individuals():
        #Create individuals
        population = [[0, EvolvingAgent(EvolvingAgent.get_random_genome())] for i in range(AgentsGim.POPULATION_SIZE) ]
        gen = 0
        last_best = -1; no_improve = 0
        #First epoch of evolution
        while(gen < AgentsGim.MAX_EPOCH_ONE_GEN):
            gen += 1
            #assign fitness values
            for p in population: p[0] = AgentsGim.fight(p[1]) 
            population.sort(reverse = True, key = lambda x: x[0])
            #If no improvements for too many generations, skip to phase 2:
            if (population[0][0] != last_best):
                last_best = population[0][0]
                no_improve = 0
            else:
                no_improve+=1
            if (no_improve > AgentsGim.MAX_EPOCH_ONE_NOIMPROVEMENTS):
                break # time for epoch 2
            print(f"Gen {gen}, best fitness: {population[0][0]}")

            population = np.array(population[0:AgentsGim.SURVIVING_SIZE])
            new_p = []
            for p in population:
                for j in range(AgentsGim.OFFSPRING_SIZE):
                    new_individual =EvolvingAgent.mix_genomes(p[1].genome, population[random.randint(0, len(population)-1)][1].genome)
                    EvolvingAgent.random_mutation(new_individual, random.randint(0, AgentsGim.NUM_MUTATION), AgentsGim.MUTATION_SIZE)
                    new_p.append([0, EvolvingAgent(new_individual)])
                    #new_p.append(p)
            population = new_p

        print("End of epoch 1")

        #Second epoch of evolution
        gen = 0
        while(gen < AgentsGim.MAX_EPOCH_TWO_GEN):
            gen += 1
            #assign fitness values
            for p in population: p[0] = AgentsGim.fight_epoch_2(p[1], population) 
            population.sort(reverse = True, key = lambda x: x[0])
            #Check if at least 6 individuals have beaten all the instructors:
            if (population[8][0] >= 100):
                print("End of epoch 2: 9 agents beated the NimSum agent")
                break
            population = np.array(population[0:AgentsGim.SURVIVING_SIZE])
            print(f"Gen {gen}, best fitness: {population[0][0]}")
            new_p = []
            for p in population:
                for j in range(AgentsGim.OFFSPRING_SIZE):
                    new_individual =EvolvingAgent.mix_genomes(p[1].genome, population[random.randint(0, len(population)-1)][1].genome)
                    EvolvingAgent.random_mutation(new_individual, random.randint(0, AgentsGim.NUM_MUTATION), AgentsGim.MUTATION_SIZE)
                    new_p.append([0, EvolvingAgent(new_individual)])
                    #new_p.append(p)
            population = new_p


        print("End of process. Best 3 individuals:")
        for p in population: p[0] = AgentsGim.fight_epoch_2(p[1], population) 
        population.sort(reverse = True, key = lambda x: x[0])
        for p in population[:3]:
            print(p[1].genome)
            print("\n")



if (__name__ == '__main__'):
    AgentsGim.evolve_individuals()

