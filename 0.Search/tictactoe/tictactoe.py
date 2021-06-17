"""
Tic Tac Toe Player
"""

import math, copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY,EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    countX = 0
    countO = 0
    # count_EMPTY = 0

    for row in board:
        countX += row.count(X)
        countO += row.count(O)
    if (terminal(board)):
        return "Game Finished"
    elif (countX > countO):
        return O
    else:
        return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.add((i,j))
    return moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if terminal(board):
        return "Game Finished"
    
    curr_player = player(board)
    allowed_moves = actions(board)

    if action in allowed_moves:
        result_board = copy.deepcopy(board)
        # (i,j) = (action[0],action[1])
        result_board[action[0]][action[1]] = curr_player
        return result_board
    else:
        raise ValueError('Not a valid action')


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    is_winner = False

    # Check winner by row/col
    for i in range(3):
        if (board[i][0] == board[i][1] == board[i][2]):
            ttt_winner = board[i][0]
            if (ttt_winner != None):
                is_winner = True
        elif (board[0][i] == board[1][i] == board[2][i]):
            ttt_winner = board[0][i]
            if (winner != None):
                is_winner = True
    # Check winner on diagonals    
    if (board[0][0] == board[1][1] == board[2][2]):
        ttt_winner = board[0][0]
        if (ttt_winner != None):
            is_winner = True
    elif (board[0][2] == board[1][1] == board[2][0]):
        ttt_winner = board[0][2]
        if (ttt_winner != None):
            is_winner = True
     
    if (is_winner == True):
        return ttt_winner 
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if (winner(board) != None):
        return True

    for row in board:
        for cell in row:
            if cell is EMPTY:
                return False
    
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    ttt_winner = winner(board)
    if (ttt_winner == X):
        return 1
    elif (ttt_winner == O):
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
        
    # Check current player
    curr_player = player(board)
    opt_move = None

    # If X, maximise minimax return using max_value fxn
    if (curr_player == X):
        v_max = -math.inf 
        for action in actions(board):
            v = min_value(result(board, action))
            if v > v_max:
                v_max = v
                opt_move = action
 
    # If O, minimise minimax return using min_value fxn
    elif (curr_player == O):
        v_min = math.inf
        for action in actions(board):
            v = max_value(result(board, action))
            if v < v_min:
                v_min = v
                opt_move = action
    return opt_move

def max_value(board):
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v
    
def min_value(board):
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v