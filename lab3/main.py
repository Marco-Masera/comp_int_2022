from GameState.GameState import *
from PlayerBaseClass import *
from Strategies.NimSum import NimSum
#Params
NUM_ROWS = 5
K = None 
PRINT_EACH_MOVE = True 
#Players
PLAYER_1 = NimSum()
PLAYER_2 = NimSum()


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
        turn += 1; turn %= 2
        

    print(f"Game ended. Player #{turn+1} is the winner!")


def main():
    nim = Nim(NUM_ROWS, K)
    game(nim, PLAYER_1, PLAYER_2, PRINT_EACH_MOVE)


if (__name__ == '__main__'):
    main()