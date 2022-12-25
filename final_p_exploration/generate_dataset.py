import numpy as np
import json
import random
from collapse_state.collapse_state import collapse

export_file = "dataset/dataset_v0.json"

cache = None 
num = 0

class exported_info:
    def __init__(self, minmax_result, wins, loses, state):
        self.minmax_result = minmax_result       #MinMax result: 1 iff state leads to victory, 0 if leads to tie, -1 if leads to lose
        self.wins = wins                         #Without regards to MinMax, considers all branches sprawing from this state and counts the victories
        self.loses = loses                       #Like wins but for defeats
        #Can be computed after, but i might be useful to keep track 
        #of the ration wins/loses and the total number of leaves. High ration and low number of leaves = very good as it will be easy for the agent to find the best states
        self.state = state
    def get_value(self):
        if (self.wins + self.loses > 0):
            return (self.minmax_result*100) + ((self.wins / (self.wins + self.loses))*40)
        return (self.minmax_result*100)
    def get_tuple(self):
        return [[[int(x) for x in self.state[0]], self.state[1]], self.get_value()]

d=[(0, 1, 3, 6), (2, 4, 7, 10), (5,8, 11, 13), (9, 12, 14, 15),
        (6, 10, 13, 15), (3, 7, 11, 14), (1, 4, 8, 12), (0, 2, 5, 9),
        (6, 7, 8, 9), (0, 4, 11, 15)]
def checkState(state): # -> (isChessboardFull, isWinning)
    global d
    full = True
    for t in d:
        and_ = (~0)&15
        or_ = 0
        for c in t:
            if (state[c] != -1):
                and_ = and_ & state[c]
                or_ = or_ | state[c]
            else:
                and_ = 0
                or_ = 15
                full = False
        if (and_ != 0 or or_ != 15):
            #print(f"Winning state {str(bin(state[t[0]]))}  -  {str(bin(state[t[1]]))}  -  {str(bin(state[t[2]]))}  -  {str(bin(state[t[3]]))}")
            return (True, True)
    return (full, False)

#Stato = (stato scacchiera, pedina_assegnata)
#memorizza quanto questo stato è "buono" per il giocatore attuale che riceve la pedina
def all_s(state, depth=0, stop_flat_after=3):   #Returns 1 if it is a good state for him, else -1- 0 if stall
    global cache; global num;
    #if (depth < stop_flat_after):
    state = collapse(state[0], state[1])
    if (str(state) in cache):
        return cache[str(state)].minmax_result

    num += 1
    if (num%50000 == 0):
        print(num)

    #Verifica se c'è fila completa
    #Se lo è, giocatore precedente ha vinto e giocatore attuale ha perso
    #Se la scacchiera è piena vittoria è pareggio
    chess_full, victory = checkState(state[0])
    if (victory):
        cache[str(state)] = exported_info(-1, 0, 1, state)
        return -1 #Ha perso
    if (chess_full):
        cache[str(state)] = exported_info(0, 0, 0, state)
        return 0
    
    my_best_move = -1 
    wins = 0
    loses = 0

    allowed = set([x for x in range(0,16)]) - set(state[0])
    my_pawn = state[1]
    if (my_pawn != None and my_pawn in allowed):
        allowed.remove(my_pawn)
    if (len(allowed)==0):
        allowed = [None]
    for index in range(0, len(state[0])):
        if (state[0][index]==-1):
            if (depth==1):
                print(f"Computing {index} over {len(state[0])}")
            for i in allowed:
                new_s = (np.copy(state[0]), i)
                if (my_pawn!=None):
                    new_s[0][index] = my_pawn
                result = -(all_s(new_s, depth=depth+1, stop_flat_after=stop_flat_after))

                if (result > my_best_move):
                    my_best_move = result 
                if (result == 1):
                    wins += 1
                elif (result == -1):
                    loses += 1
            if (my_pawn == None):
                break
            
    cache[str(state)] = exported_info(my_best_move, wins, loses, state)
    return my_best_move



def generate_dataset(depth):
    global cache; global num
    random.seed()
    cache = dict()
    num = 0
    initial_state = []
    all_pawns = set([x for x in range(0,15)])

    for _ in range(16-depth):
        pawn = random.sample(all_pawns, 1)[0]
        all_pawns.remove(pawn)
        initial_state.append(pawn)
    for i in range(0, depth):
        initial_state.append(-1)

    all_s((np.array(initial_state), None))
    print(num)
    #Transform cache for export
    to_export = []
    for value in cache.values():
        tuple = value.get_tuple()
        #Discard non informative states
        if (tuple[1] == 0 and random.randint(0,100)<80):
            continue
        #print(tuple)
        to_export.append(tuple)

    with open(export_file, 'w') as dataset:
        dataset.write(json.dumps({'exp': to_export}))
    
generate_dataset(8)