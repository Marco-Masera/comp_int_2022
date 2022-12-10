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

    #Take action calls game.nimming to make the move, but it can memorize informations for the purpose of learning
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


def run():
    players = (ReinforcementLearningAgent(), NimSum()); 
    for i in range(0,1000):
        turn = 0 
        game = Nim(3, 2)
        players[0].exploration = int( 20 * (1000-i) / 1000 )
        players[0].initialize(game); players[1].initialize(game)
        while(True):
            move_result = players[turn].your_turn(game)
            if move_result == MoveResult.Game_Over:
                print(f"Game #{i}, player {turn} won")
                players[0].give_reward((1-turn)*2 - 1) #1 se ha vinto lui se no -1
                break
            turn  = 1 - turn

    for i in range(0,300):
        turn = 0 
        game = Nim(5, 3)
        #players[0].exploration = int( 20 * (1000-i) / 1000 )
        players[0].initialize(game); players[1].initialize(game)
        while(True):
            move_result = players[turn].your_turn(game)
            if move_result == MoveResult.Game_Over:
                print(f"Game #{i}, player {turn} won")
                players[0].give_reward((1-turn)*2 - 1) #1 se ha vinto lui se no -1
                break
            turn  = 1 - turn
        


if (__name__ == '__main__'):
    run()