from collections import namedtuple
import random
from typing import Callable
from copy import deepcopy
from itertools import accumulate
from enum import Enum
Nimply = namedtuple("Nimply", "row, num_objects")


# Enum to be returned after a move, containing the result
class MoveResult(Enum):
    Game_Continues = 1,
    Game_Over = 2

#
#   Class representing the game state. Has methods to make moves, print the game state, check if player N wins
#

class Nim:
    def __init__(self, num_rows: int, k: int = None) -> None:
        self._rows = [i * 2 + 1 for i in range(num_rows)]
        self._k = k

    def __bool__(self):
        return sum(self._rows) > 0

    def __str__(self):
        return "<" + " ".join(str(_) for _ in self._rows) + ">"

    @property 
    def is_empty(self) -> bool:
        return len(list(filter(lambda c: c != 0, self._rows)))==0

    @property
    def rows(self) -> tuple:
        return tuple(self._rows)

    @property
    def k(self) -> int:
        return self._k

    def nimming(self, ply: Nimply) -> None:
        row, num_objects = ply
        print(f"Move row: {row}, num: {num_objects}")
        assert self._rows[row] >= num_objects
        assert self._k is None or num_objects <= self._k
        assert num_objects > 0
        self._rows[row] -= num_objects
        if self.is_empty:
            return MoveResult.Game_Over 
        else:
            return MoveResult.Game_Continues
    

