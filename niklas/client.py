import kgp
import math
from dotenv import load_dotenv
import time
import hashlib

CLIENT_SIDE = kgp.SOUTH
DEPTH = 5

def evaluate(state : kgp.Board, side) -> int:
    # return sum(state.south_pits) - sum(state.north_pits) + 2 * (state.south - state.north)
    return state[side] - state[not side]

def search(state : kgp.Board, depth : int, side : bool, alpha = -math.inf, beta = math.inf) -> (int, int):
    """
    Searches the best move to a given board state\n
    Returns a move and its evaluation
    """
    maxScore = -1 * math.inf
    bestMove = -1
    for move in state.legal_moves(side):
        if depth <= 0:
            if (score := evaluate(state, side)) > maxScore:
                maxScore, bestMove = score, move
            continue

        new_board, repeat_move = state.sow(side, move)
        if new_board.is_final():
            if (score := evaluate(new_board, side)) > maxScore:
                maxScore, bestMove = score, move
            continue
        
        result = 0
        if repeat_move:
            result = -search(
                state = new_board,
                depth = depth - 1,
                side  = side,
                alpha = alpha,
                beta  = beta
            )[0]
        else:
            result = -search(
                state = new_board,
                depth = depth - 1,
                side  = not side,
                alpha = -beta,
                beta  = -alpha
            )[0]
        if result > maxScore:
                maxScore, bestMove = result, move

        if result > beta: break
        alpha = max(alpha, result)

    return maxScore, bestMove
    
    
    
def agent(state : kgp.Board):
    start = time.time()
    result = search(
        state,
        DEPTH,
        CLIENT_SIDE
    )
    end = time.time()
    print(result," ",end-start)
    yield result[1]


if __name__ == "__main__":
    import os
    load_dotenv()
    kgp.connect(
        agent,
        host="localhost",
        debug=True,
        token=os.getenv("TOKEN"),
        name="ABP",
        authors=["Niklas Haas"]
    )