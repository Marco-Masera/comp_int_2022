import os
import sys 
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))))
from copy import deepcopy
import random
from PlayerBaseClass import PlayerBase
from GameState.GameState import *
from Strategies.NimSum import NimSum
"""if __name__=='main':
    from Instructors import  GenerousNimSum
    from learned_rules import learned_strategy
else:
    from Strategies.EvolvingRules.Instructors import GenerousNimSum
    from Strategies.EvolvingRules.learned_rules import learned_strategy
"""

class ReinforcementLearningAgent(PlayerBase):
    def __init__(self, exploration = 20, alpha = 0.4, discount_effect_factor = 0.1):
        self.exploration = exploration
        self.states_reward = dict()
        self.alpha = alpha
        self.discount_effect_factor = discount_effect_factor
    
    #To be called before each game
    def initialize(self, game:Nim) -> None:
        self.states = []

    #To be called during or after a game to reward/punish the state the agent is in
    def give_reward(self, reward):
        alpha = self.alpha 
        discount_factor = 1 - self.discount_effect_factor
        for state in reversed(self.states):
            hashable = str(state)
            if (hashable in self.states_reward):
                self.states_reward[hashable] = (self.states_reward[hashable] * (1-alpha)) + (reward * alpha)
            else:
                self.states_reward[hashable] = (0.5 * (1-alpha)) + (reward * alpha)
            alpha *= discount_factor

    #Take action calls game.nimming to make the move, but it also memorize informations for the purpose of learning
    def take_action(self, game, action):
        result = game.nimming(action) 
        self.states.append(self.reduce_state(game))
        return result
    

    def reduce_state(self,game:Nim, keep_index=False):
        reduced = None
        if (not keep_index):
            reduced = [row for row in game.rows if row > 0] # Remove zeros
        else:
            reduced = [(row, index) for index, row in enumerate(game.rows) if row > 0]
        reduced.sort() # Sort, so we avoid permutations
        return reduced

    def get_reward_from_state(self, game:Nim, action):
        g = deepcopy(game)
        g.nimming(action)
        reduced = self.reduce_state(g) 
        if (str(reduced) in self.states_reward):
            return self.states_reward[str(reduced)]
        else:
            return 0.5

    #Given the current state and a set of actions, it choosen the one considered best
    def policy(self, game:Nim, actions):
        move_rewards = [ (self.get_reward_from_state(game,action), action) for action in actions ]
        move_rewards.sort(reverse=True)
        return move_rewards[0][1]

    #Returns possible actions given a state
    def get_actions(self, game:Nim):
        actions = []
        last = -1
        k = 99999
        if (game.k != None):
            k = game.k
        for row, index in self.reduce_state(game, keep_index=True):
            if (row==last):
                continue 
            last = row 
            for i in range(1, min(row, k)+1):
                actions.append( (index, i) )
        return actions 
        
    def play(self,game:Nim) -> MoveResult:
        actions = self.get_actions(game)
        if (len(actions)==0):
            raise Exception("Illegal game state")

        random_choice = random.randint(0,100)
        if (random_choice < self.exploration):
            #It's exploration time baby
            return self.take_action(game, random.choice(actions))
        else:
            best_action = self.policy(game, actions)
            return self.take_action(game, best_action)


#Tries to make the agent learn for a given rows, k. Returns the
#number of games won
def learn(player, rows, k, max_rounds = 1000, alpha = 0.4, discount_factor = 0.1, exploration_factor = 20):
    players = (player, NimSum()); 
    wins = 0
    wins_in_a_row = 0
    player.alpha = alpha 
    player.discount_effect_factor = discount_factor
    for i in range(0,max_rounds):
        turn = 0 
        game = Nim(rows, k)
        if (wins_in_a_row < 3):
            players[0].exploration = int( exploration_factor * (max_rounds-i) / max_rounds )
        else:
            players[0].exploration = 0 #If it's winning, let's focus on exploiting instead of exploring
        players[0].initialize(game); players[1].initialize(game)
        while(True):
            move_result = players[turn].your_turn(game)
            if move_result == MoveResult.Game_Over:
                #print(f"Game #{i}, player {turn} won")
                if (turn==0):
                    wins+=1
                    wins_in_a_row+=1
                else:
                    wins_in_a_row = 0
                players[0].give_reward((1-turn)*2 - 1) #1 se ha vinto lui se no -1
                break
            turn  = 1 - turn
        
    return wins

#Fast learn use the Xor sum to give a reward for each move of the agent, instead of waiting for it to finish the game.
def fast_learn(player, rows, k, exploraton=35, max_rounds = 1000, alpha = 0.4):
    players = (player, NimSum())
    player.alpha = alpha
    for i in range(0,max_rounds):
        turn = 0 
        game = Nim(rows, k)
        players[0].exploration = exploraton
        players[1].initialize(game)
        while(True):
            #Initialize is now called at each move, so the reward given will affect only the last choice
            players[0].initialize(game); 
            move_result = players[turn].your_turn(game)
            if move_result == MoveResult.Game_Over:
                players[0].give_reward((1-turn)*2 - 1) #1 se ha vinto lui se no -1
                break
            #if it's player 0 turn, let's compute the nimsum and reward the agent
            if (player==0):
                tuples = None
                if (game.k is not None):
                    tuples = [x%(game.k+1) for x in game.rows]
                else:
                    tuples = list(game.rows)
                nim_sum = 0
                for tuple in tuples: nim_sum = nim_sum ^ tuple
                if (nim_sum == 0):
                    players[0].give_reward(1)
                else:
                    players[0].give_reward(-0.6)
                    break
            turn  = 1 - turn

def run():

    rounds = [
        #{'rows': 4, 'k': 2},
        #{'rows': 5, 'k': 4},
        #{'rows': 6, 'k':4},
        {'rows': 6, 'k':4, 'n_matches': 3000},
        {'rows': 8, 'k':5, 'n_matches': 60000}
    ]
    print("\n")
    for round in rounds:
        n_matches = 500
        if ('n_matches' in round):
            n_matches = round['n_matches']
        print(f"Playing round with Rows = {round['rows']} and K = {round['k']}")
        agent = ReinforcementLearningAgent()
        wins = learn(agent, round['rows'], round['k'], max_rounds = n_matches, alpha = 0.4, discount_factor = 0.1, exploration_factor = 20)
        print(f"{wins} victories over {n_matches} games")
        print("Let's try with fast learn before and lower exploration after:")
        agent = ReinforcementLearningAgent()
        fast_learn(agent, round['rows'], round['k'], exploraton=40, max_rounds = n_matches*2, alpha = 0.9)
        wins = learn(agent, round['rows'], round['k'], max_rounds = n_matches, alpha = 0.4, discount_factor = 0.1, exploration_factor = 5)
        print(f"Now it's {wins} victories over {n_matches} games")
        print("\n")


if (__name__ == '__main__'):
    run()