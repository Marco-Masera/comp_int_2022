from GameState.GameState import *
from PlayerBaseClass import *
from Strategies.NimSum import NimSum
from Strategies.MinMax import MinMax
from Strategies.EvolvingRules.EvolvingAgent import EvolvingAgent
 
#Constructors to get Players instances:
#NimSum perfect agent (3.1)
def get_nimsum_agent():
    return NimSum()
#Evolving rules agent with pre-learned rules
def evolving_rules_agent():
    return EvolvingAgent.get_from_learned_strategy();
#MinMax unbonded, bounded with horizon effect, bounded with xor sum as gain function
def get_minmax_unbounded():
    return MinMax.get_minmax_unbounded()
def get_minmax_bounded_horizon(bound):
    return MinMax.get_minmax_bounded_horizon(bound)
def get_minmax_bounded_xor(bound):
    return MinMax.get_minmax_bounded_xor(bound)

#Players 
PLAYER_1 = get_minmax_bounded_xor(1)
PLAYER_2 = get_nimsum_agent()
#Params
NUM_ROWS = 4
K = 2
PRINT_EACH_MOVE = True



#   This methods takes one Nib game and Two player implementing the PlayerBase interface, and allow them to play until the game ends.
def game(game: Nim, player_1, player_2, print_each_move = False):
    players = (player_1, player_2); turn = 0 
    players[0].initialize(game); players[1].initialize(game)

    while(True):
        #Player makes his move
        move_result = players[turn].your_turn(game)
        #Print result if required
        if (print_each_move):
            print(f"Player #{turn+1} made a move. State: {game}")
        #Exit loop if game over
        if move_result == MoveResult.Game_Over:
            break
        #Swap players
        turn  = 1 - turn
        

    print(f"Game ended. Player #{turn+1} is the winner!")


def main():
    nim = Nim(NUM_ROWS, K)
    game(nim, PLAYER_1, PLAYER_2, PRINT_EACH_MOVE)


if (__name__ == '__main__'):
    main()