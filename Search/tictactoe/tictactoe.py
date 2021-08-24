"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    turnNumber = 9
    for i in board:
        for j in i:
            if j==EMPTY:
                turnNumber -=1
    if turnNumber%2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actionsList = []
    for i in range(3):
        for j in range(3):
            if board[i][j]==EMPTY:
                actionsList.append((i,j))
    return actionsList


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action in actions(board):
        i=action[0]
        j=action[1]
        boardCopy = copy.deepcopy(board)
        if board[i][j] == EMPTY:
            boardCopy[i][j] = player(board)
    elif action not in actions(board):
        raise ValueError('Not a valid choice')
    return boardCopy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if all(i == board[0][0] for i in board[0]):
        return board[0][0]
    elif all(i == board[1][0] for i in board[1]):
        return board[1][0]    
    elif all(i == board[2][0] for i in board[2]):
        return board[2][0]
    elif (board[0][0] == board[1][0] == board[2][0]):
        return board[0][0]
    elif (board[0][1] == board[1][1] == board[2][1]):
        return board[0][1]
    elif (board[0][2] == board[1][2] == board[2][2]):
        return board[0][2]
    elif (board[0][0] == board[1][1] == board[2][2]):
        return board[0][0]
    elif (board[0][2] == board[1][1] == board[2][0]):
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if actions(board) == [] or winner(board) == X or winner(board) == O:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    #takes only terminal board
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def max_value(board):
    v=-42
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = max(v,min_value(result(board,action)))
    return v

def min_value(board):
    v=42
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = min(v,max_value(result(board,action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    action = actions(board)
    highestValue = -1
    smallestValue = 1
    optimalMove = None
    #For all action A player X can make we consider the highest value of min-value(result(state,A))
    if player(board) == X:
        for moveCase in action:
            if highestValue <= min_value(result(board, moveCase)):
                highestValue,optimalMove = (min_value(result(board, moveCase)),moveCase)
        return optimalMove

    #For all action A player O can make we consider the smallest value of max-value(result(state,A))
    elif player(board) == O:
        for moveCase in action:
            if smallestValue > max_value(result(board, moveCase)):
                smallestValue,optimalMove = (max_value(result(board, moveCase)),moveCase)
        return optimalMove
    
