import numpy as np
import json
import random
import copy
from quarto_utils import checkState, bits_in_common_multiple
"""
    Features hanno valore binario, 1 se attive 0 se disattive
    Feature: array di 16 elementi, 1 per cella attiva, 0 per disattiva
    Tipi features:
        >Tipo A: attiva se piena con pedine che hanno un attributo comune
        >Tipo B: attiva se piena con pedine che non hanno attributi in comune
        >TIpo C: attiva se vuota
    Integrazione:
        >NxN
        >Attiva se entrambe attive
        >Peso
        >Per features di tipo A: attiva se entrambe condividono attributi comuni
        >Per features di tipo AxC e AxCb: attiva solo se A contiene una feature in comune con la pedina
                                                    e nel caso b se ho una pedina con una feature in comune
    Genome: [ [Features] [Weight Matrix] ]
"""
N_FEATURES_A = 20
N_FEATURES_B = 10
N_FEATURES_C = 16
N_FEATURES = N_FEATURES_A+N_FEATURES_B+N_FEATURES_C
class StateReward:
    #Process state is used to convert the raw state from the agent to the format used to compute the function
    def process_state(state):
        return [state[0], state[1], list(set([x for x in range(16)]) - set(state[0]))]

    def get_random_genome(self):
        #Features [ [feat. 1], [feat. 2] ... ]
        features = []
        weights = np.zeros((N_FEATURES, N_FEATURES + (N_FEATURES_C)), dtype=float) #Genome: N Features x N Features + C
        for i in range(N_FEATURES):
            features.append([np.array([ random.choice([True, False]) for _ in range(16)]), 0, None])
            for j in range(i, N_FEATURES + N_FEATURES_C): 
                weights[i][j] = random.uniform(-0.1, 0.1)
        return (np.array(features, dtype=object), weights)
    
    #State needs to be processed via process_state before this function is called
    def get_reward(self, state): #State = ([chessboard], assigned_pawn, set[remaining])
        full, winning = checkState(state[0])
        if (winning):
            return 1000
        if (full):
            return 0
        reward = 0
        #Check features of type A
        for i in range(0, N_FEATURES_A):
            feature = self.genome[0][i]
            #Activated = feature[1], feature[0] è chessboard
            feature[1] = 1
            last = None; acc=15
            for i in range(16):
                if (feature[0][i]==True):
                    if (state[0][i]==-1 ):
                        feature[1] = 0
                        break
                    if (last != None):
                        acc = acc & (~(last ^ state[0][1]))
                    last = state[0][1]
            feature[2] = (last, acc)
            if (acc==0):
                feature[1] = 0
        #Check features of type B
        for i in range(N_FEATURES_A, N_FEATURES_A+N_FEATURES_B):
            feature = self.genome[0][i]
            feature[1] = 1
            for i in range(16):
                if (feature[0][i]==True and state[0][i]!=-1):
                    feature[1] = 0
                    break
        #Features of type C
        for i in range(N_FEATURES_A+N_FEATURES_B, N_FEATURES):
            feature = self.genome[0][i]
            feature[1] = 1
            for i in range(16):
                if (feature[0][i]==True and state[0][i]!=-1):
                    feature[1] = 0
                    break
        #COmputes the reward
        for i in range(N_FEATURES):
            for j in range(i, N_FEATURES+N_FEATURES_C):
                #C x Cb viene balzata
                if (i>=N_FEATURES-N_FEATURES_C and j >= N_FEATURES):
                    continue 
                if (j >= N_FEATURES): 
                    j2 = j - N_FEATURES_C 
                else: j2 = j
                if (self.genome[0][i][1]*self.genome[0][j2][1]==0):
                    continue
                weight = self.genome[1][i][j]
                #Per features di tipo A: attiva se entrambe condividono attributi comuni
                if (i<N_FEATURES_A and j < N_FEATURES_A): #(last, acc)
                    first = self.genome[0][i][2]; second = self.genome[0][j][2]
                    if (( (~(first[0] ^ second[0])) & first[1] & second[1]) ==0):
                        continue
                #>Per features di tipo AxCn: attiva solo se A contiene la feature n e 1 attiva se
                if (i<N_FEATURES_A and j>=N_FEATURES-N_FEATURES_C):
                    if (bits_in_common_multiple([state[1]], acc=self.genome[0][i][2][1], last=self.genome[0][i][2][0])==0):
                        continue
                if (i<N_FEATURES_A and j>=N_FEATURES):
                    if (bits_in_common_multiple(state[2], acc=self.genome[0][i][2][1], last=self.genome[0][i][2][0])==0):
                        continue
                reward += weight
        return reward

    def __init__(self, genome = None):
        if (genome==None):
            self.genome = self.get_random_genome()
        else:
            self.genome = genome
        pass 


    def random_mutations(self, n_mutation):
        for _ in range(n_mutation):
            if (random.randint(0,1)==0):
                feature = random.randint(0, N_FEATURES-1)
                cell = random.randint(0,15)
                self.genome[0][feature][0][cell] = not self.genome[0][feature][0][cell]
            else:
                feature = random.randint(0, N_FEATURES-1)
                feature_2 = random.randint(feature, N_FEATURES + N_FEATURES_C - 1)
                self.genome[1][feature][feature_2] += random.uniform(-0.02, 0.02)
    
    def crossover(ind1, ind2):
        genome = copy.deepcopy(ind1.genome)
        if (random.randint(0,2)==0):
            #mutate some feature
            i = random.randint(0,N_FEATURES-1)
            j = random.randint(i, min(N_FEATURES, i+10))
            for k in range(i, j):
                genome[0][k] = copy.deepcopy(ind2.genome[0][k])
                for z in range(k, N_FEATURES+N_FEATURES_C):
                    genome[1][k][z] = copy.deepcopy(ind2.genome[1][k][z])
        for i in range(random.randint(3,15)):
            #Mutate the matrix
            i = random.randint(0,N_FEATURES-1)
            for k in range(0, N_FEATURES+N_FEATURES_C):
                genome[1][i][k] = copy.deepcopy(ind2.genome[1][i][k])
                
        return StateReward(genome)

    def __lt__(self, other):
        return False



#The following code handles the learning part
STATES = {} # [ [chessboard], pawn, [remaining], real_reward ]
SAMPLE_TARGET = 3

class Island:
    def __init__(self, population_size, offspring_size, mutations):
        self.population_size = population_size
        self.offspring_size = offspring_size
        self.mutations = mutations
        self.population = [StateReward() for _ in range(population_size)]
        self.best_error = -100000
        

    def get_state_sample(self):
        sample = []
        for i in range(9,16):
            for k in STATES[str(i)].keys():
                set_ = STATES[str(i)][k]
                if (len(set_)>SAMPLE_TARGET):
                    sample.extend(random.sample(set_, SAMPLE_TARGET))
                else:
                    sample.extend(set_)
        self.sample = sample

    def value_individual(self,individual):
        error = 0
        for state in self.sample:
            reward = individual.get_reward(state)
            error += (reward - state[3])**2
        return error

    def new_gen(self):
        self.get_state_sample()
        #Mutate and crossover to get offspring_size individuals!
        new_p = []
        for _ in range(self.offspring_size):
            p = StateReward.crossover(random.choice(self.population), random.choice(self.population))
            p.random_mutations(random.randint(1,self.mutations))
            new_p.append((self.value_individual(p), p))
        new_p.sort()
        self.population = [x[1] for x in new_p[:self.population_size]]

    def tsunami(self, survivors):
        self.population =self.population[:survivors] + [StateReward() for _ in range(self.population_size-survivors)]

    def get_best_performer_error(self):
        return self.value_individual(self.population[0])


def evolve():
    global STATES 
    with open("dataset/pre_processed/output.json", 'r') as source:
        STATES = json.load(source)

    island_1 = Island(120,220, 3)
    island_2 = Island(100,200, 6)
    #island_3 = Island(100,200, 4)
    #continent = Island(600,1200, 2)
    gen = 0
    print("Start")
    while(True):
        island_1.new_gen()
        island_2.new_gen()
        gen += 1
        best_1 = island_1.get_best_performer_error()
        best_2 = island_2.get_best_performer_error()
        if (gen%100==0):
            island_1.tsunami(40)
            island_2.tsunami(40)
            with open("res.txt",'w') as output:
                output.write(str(min(best_1, best_2)))
        if (gen%10==0):
            print(f"Gen {gen}: {best_1} {best_2}")


if __name__== '__main__':
    evolve()