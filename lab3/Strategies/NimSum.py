import os
import sys 
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) 
from PlayerBaseClass import PlayerBase
from GameState.GameState import *

class NimSum(PlayerBase):
    def play(self,game:Nim) -> MoveResult:
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
                target = tuple ^ nim_sum
                return game.nimming((index, tuple-target))