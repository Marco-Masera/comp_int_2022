import os
import sys 
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))))
from PlayerBaseClass import PlayerBase
from GameState.GameState import *
import numpy as np
import random


#Instructors: agents that play nim more or less good; they serve to compute the fitness of the evolving agents
class RandomAgent(PlayerBase):
    def play(self,game:Nim) -> MoveResult:
        rows = [(value,index) for index,value in enumerate(game.rows) if value > 0]
        if random.randint(0,1) ==0:
            row = max(rows)
            return game.nimming((row[1], min( random.randint(1, row[0]), game.k )))
        else:
            row = min(rows)
            return game.nimming((row[1], min( random.randint(1, row[0]), game.k )))

#Generous NimSum gives the opponent an advantage each N moves
class GenerousNimSum(PlayerBase):
    def __init__(self, N):
        self.N = N
        self.moves = 0
    def play(self,game:Nim) -> MoveResult:
        self.moves = (self.moves+1) % self.N
        tuples = None
        if (game.k is not None):
            tuples = [x%(game.k+1) for x in game.rows]
        else:
            tuples = list(game.rows)
        #Computes nimSum
        nim_sum = 0
        for tuple in tuples: nim_sum = nim_sum ^ tuple
        if (nim_sum == 0):
            #cannot win :(
            #make a random move just to do something
            for index, tuple in enumerate(game.rows):
                if (tuple > 0):
                    return game.nimming((index, 1))
        #Otherwise find a move 
        for index, tuple in enumerate(tuples):
            target = tuple ^ nim_sum
            if (tuple >= target):
                if (self.moves == 0):
                    #gives the opponent an advantage
                    if (tuple-target > 1):
                        return game.nimming((index, tuple-target-1))
                    elif(tuple-target < game.k and target > 0):
                        return game.nimming((index, tuple-target+1))
                    else:
                        #Just a random move...
                        for index, tuple in enumerate(game.rows):
                            if (tuple > 0):
                                return game.nimming((index, 1))
                return game.nimming((index, tuple-target))
                
                