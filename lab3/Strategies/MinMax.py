import os
import sys 
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) 
from PlayerBaseClass import PlayerBase
from GameState.GameState import *
from copy import deepcopy
MoveResult = namedtuple("MoveResult", "row, num_objects, gain")

class MinMax(PlayerBase):
    
    def __init__(self, bound = None, bound_mode = None):
        assert (bound == None and bound_mode == None) or (bound!=None and (bound_mode == 0 or bound_mode == 1))
        self.bound = bound 
        if (bound_mode==0):
            #horizon
            self.current_value = lambda game: 0.5 
        else:
            #xor sum
            self.current_value = MinMax.xor_sum
    
    #Real constructors to use
    def get_minmax_unbounded():
        return MinMax()
    def get_minmax_bounded_horizon(bound):
        return MinMax(bound, 0)
    def get_minmax_bounded_xor(bound):
        return MinMax(bound, 1)

    def xor_sum(game:Nim):
        tuples = None
        if (game.k is not None):
            tuples = [x%(game.k+1) for x in game.rows]
        else:
            tuples = list(game.rows)
        #Computes nimSum
        nim_sum = 0
        for tuple in tuples: nim_sum = nim_sum ^ tuple
        if nim_sum == 0:
            return 0
        else:
            return 1

    def get_possible_moves(game:Nim) -> list[Nimply]:
        k = game.k
        if (k == None): k = 9999999
        return [
            [
                (row_index, move) for move in reversed(range(1, min(k, row)+1))
            ] for row_index, row in enumerate(game.rows) if row > 0
        ]

    def min(self, game:Nim, depth = 0) -> MoveResult:
        if (self.bound != None and depth >= self.bound):
            return (-1, -1, 1-self.current_value(game))
        possible_moves = MinMax.get_possible_moves(game)
        if (len(possible_moves)==0):
            return (-1,-1, 1) #If min has no moves left, max won
        current_fav = None
        for row in possible_moves:
            for move in row:
                g = deepcopy(game)
                g.nimming(move)
                result = self.max(g, depth+1)
                if (current_fav==None or result[2] > current_fav[2]):
                    current_fav = (move[0], move[1], result[2])
                if (result[2]==0):
                    #If he find a winning move, no need to keep exploring
                    return (move[0], move[1], 0)
        #If no winning move found, doesn't matter what choice max makes, he'll lose. It can return any move he wants
        return current_fav
        
    def max(self, game:Nim, depth = 0) -> MoveResult:
        if (self.bound != None and depth >= self.bound):
            return (-1, -1, self.current_value(game))
        possible_moves = MinMax.get_possible_moves(game)
        if (len(possible_moves)==0):
            return (-1,-1, 0) #If max has no moves left, he lost
        current_fav = None
        for row in possible_moves:
            for move in row:
                g = deepcopy(game)
                g.nimming(move)
                result = self.min(g, depth+1)
                if (current_fav==None or result[2] > current_fav[2]):
                    current_fav = (move[0], move[1], result[2])
                if (result[2]==1):
                    #If he find a winning move, no need to keep exploring
                    return (move[0], move[1], 1)
        #If no winning move found, doesn't matter what choice max makes, he'll lose. It can return any move he wants
        return current_fav


    def play(self,game:Nim) -> MoveResult:
        move = self.max(game)
        return game.nimming((move[0], move[1]))