from GameState.GameState import *

class PlayerBase:
    def your_turn(self,game: Nim) -> MoveResult:
        return self.play(game) 

    #This method is to be overwritten by strategy impementation
    def play(self,game:Nim) -> MoveResult:
        pass
    #This can be initialized to store informations on game rules, if needed
    def initialize(self, game:Nim) -> None:
        pass
