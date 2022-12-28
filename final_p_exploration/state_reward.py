import numpy as np
import json
import random
import copy
from quarto_utils import checkState, bits_in_common_multiple

#Init some static stuff to calculate the feature faster during runtime
LINES = [
    # ( (caselle),[(quale_riga_tocca, casella )])
    ((0, 1, 3, 6), [] ),   #0
    ((2, 4, 7, 10), []),      #1
    ((5,8, 11, 13), []),      #2
    ((9, 12, 14, 15), []),    #3
    ((6, 10, 13, 15), []),    #4
    ((3, 7, 11, 14), []),     #5
    ((1, 4, 8, 12), []),     #6
    ((0, 2, 5, 9), []),       #7
    ((6, 7, 8, 9), []),       #8
    ((0, 4, 11, 15), [])]     #9
LINES_PRECEDING = np.array([0 for _ in range(16)])
count_ = 0
for index,line in enumerate(LINES):
    LINES_PRECEDING[index] = count_
    for index2 in range(index+1, len(LINES)):
        line2 = LINES[index2]
        check = -1
        for c in line2[0]:
            if (c in line[0]):
                check = c
                line[1].append([index2, c])
                count_  = count_ + 1
                break
LINES_PRECEDING[len(LINES_PRECEDING)-1] = count_
MULTILINE_BLOCK = ((LINES_PRECEDING[len(LINES_PRECEDING)-1] * 6) + 80)


class StateReward:
    state_length = (MULTILINE_BLOCK)*2
    #Process state is used to convert the raw state from the agent to the format used to compute the function
    def process_state(state):
        return [np.array(state[0]), state[1], list(set([x for x in range(16)]) - set(state[0]))]

    def get_random_genome(self):
        return np.array([random.uniform(-1,1) for _ in range(StateReward.state_length)])
    
    #State needs to be processed via process_state before this function is called
    def get_reward(self, state): #State = ([chessboard], assigned_pawn, set[remaining])
        global LINES; global LINES_PRECEDING; global MULTILINE_BLOCK;
        full, winning = checkState(state[0])
        if (winning):
            return 120
        if (full):
            return 0
        chessboard = state[0]
        mylines = np.array([(False, 0,0) for _ in range(16)])
        self.truth_value = np.array([0 for _ in range(StateReward.state_length)])
        #mylines = [] -> (Active, acc)
        for index,line in enumerate(LINES):
            count = 0; acc = 15; last = None
            for box in line[0]:
                if (chessboard[box]!=-1):
                    count += 1
                    if (last != None):
                        acc = acc & (~(chessboard[box] ^ last))
                    last = chessboard[box]
            
            if (acc == 0):
                mylines[index] = (False, acc, 0)
                continue 
            #can extend, can block -> calcolati da pawn
            if (count != 0 and acc & (~(state[1] ^ last))):#(can_extend):
                self.truth_value[(index*8) + count] = 1
            else: # (can_block):
                self.truth_value[(index*8) + count + 4] = 1

            #posso bloccare avversario -> calcolato
            one_extending = False; one_blocking = False
            for pawn in state[2]:
                if (count!=0 and acc & (~(pawn ^ last))):
                    one_extending = True 
                else:
                    one_blocking = True 
                if (one_blocking and one_extending): break

            if (one_extending):
                self.truth_value[MULTILINE_BLOCK + (index*8) + count] = 1
            elif (one_blocking):
                self.truth_value[MULTILINE_BLOCK + (index*8) + count + 4] = 1
            #aggiorna linea singola -> index
            if (last==None):
                last = -1
            mylines[index] = (True, acc, last)
        #Secondo giro
        for index,line in enumerate(LINES):
            if (mylines[index][0] == False): continue
            for common in line[1]:
                if (mylines[common[0]][0] == False): continue
                if (chessboard[common[1]] != -1): continue 

                #Verifica se posso bloccare entrambe, aumentarle entrambe o una e una
                acc = mylines[index][1]; acc2 = mylines[common[0]][1]
                can_extend_one = (acc & (~(state[1] ^ mylines[index][2])))!=0
                can_extend_two = (acc2 & (~(state[1] ^ mylines[common[0]][2])))!=0
                if (can_extend_one and can_extend_two):
                    self.truth_value[80 + (LINES_PRECEDING[index] * 6)] = 1
                elif (can_extend_one != can_extend_two):
                    self.truth_value[80 + (LINES_PRECEDING[index] * 6) + 1] = 2
                else:
                    self.truth_value[80 + (LINES_PRECEDING[index] * 6) + 2] = 3
                #verifica se posso bloccare avversario, verifica se può bloccare me
                canEO = 0; canBO = 0; canM = 0
                for pawn in state[2]:
                    can_extend_one = (acc & (~(pawn ^ mylines[index][2])))!=0
                    can_extend_two = (acc2 & (~(pawn ^ mylines[common[0]][2])))!=0
                    if (can_extend_one and can_extend_two):
                        canEO += 1
                        if (canEO==1):
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6)] = 1
                        else:
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6) + 3] = 1
                    elif (can_extend_one != can_extend_two):
                        canBO += 1
                        if (canBO==1):
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6) + 1] = 1
                        else:
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6) + 4] = 1
                    else:
                        canM += 1
                        if (canM==1):
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6) + 2] = 1
                        else:
                            self.truth_value[80 + MULTILINE_BLOCK + (LINES_PRECEDING[index] * 6) + 5] = 1
                    if (canEO >= 2 and canBO >= 2 and canM >= 2): break
        
        
        reward = np.matmul(self.genome,self.truth_value)
        if (reward > 0):
            return min(reward,140)
        else:
            return max(-140, reward)

    def __init__(self, genome = None):
        if (genome==None):
            self.genome = self.get_random_genome()
        else:
            self.genome = genome
        pass 


    def random_mutations(self, n_mutation):
        pass
    
    def crossover(ind1, ind2):
        return StateReward()

    def __lt__(self, other):
        return False



#The following code handles the learning part
STATES = {} # [ [chessboard], pawn, [remaining], real_reward ]
SAMPLE_TARGET = 8


class Climber:
    def __init__(self):
        self.individual = StateReward()  
        self.get_state_sample()

    def get_state_sample(self):
        sample = []
        for i in range(9,14):
            target = SAMPLE_TARGET
            for k in STATES[str(i)].keys():
                if (len(STATES[str(i)][k])<target):
                    target = len(STATES[str(i)][k])
            for k in STATES[str(i)].keys():
                set_ = STATES[str(i)][k]
                if (len(set_)>target):
                    sample.extend(random.sample(set_, target))
                else:
                    sample.extend(set_)
        self.sample = sample

    def random_error(self):
        error = 0
        for state in self.sample:
            reward = 0
            error += (reward - state[3])**2
        return (error / len(self.sample))


    def value_individual(self,individual):
        error = 0
        for state in self.sample:
            reward = individual.get_reward(state)
            error += (reward - state[3])**2
        return (error / len(self.sample))

    def validate(self):
        self.get_state_sample()
        print(f"Error was {self.error}. Now it's {self.value_individual(self.individual)}")

    def new_gen(self):
        self.error = self.value_individual(self.individual)
        print(f"Starting new generation - x. Best: {self.error} - random would be {self.random_error()}")
        for i in range(StateReward.state_length):
            old_v = self.individual.genome[i]
            self.individual.genome[i] = old_v + 0.07
            error = self.value_individual(self.individual)
            if (error < self.error):
                self.error = error 
                #print(f"New error {self.error} after tweaking param {i}")
                continue
            self.individual.genome[i] = old_v - 0.07
            error = self.value_individual(self.individual)
            if (error < self.error):
                self.error = error 
                #print(f"New error {self.error} after tweaking param {i}")
                continue
            self.individual.genome[i] = old_v


def load_data():
    global STATES 
    with open("dataset/pre_processed/output.json", 'r') as source:
        STATES = json.load(source)
    for i in range(9,14):
        for k in STATES[str(i)].keys():
            set_ = STATES[str(i)][k]
            for state in set_:
                state[0] = np.array(state[0])  

def climb():
    load_data()
    climber = Climber()
    for i in range(200):
        climber.new_gen()
        if (i%50==0):
            print(f"Gen {i}")
    climber.validate()

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
    for state in STATES:
        state[0] = np.array(state[0])
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
    #evolve()
    climb()