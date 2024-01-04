import kgp
import math
from dotenv import load_dotenv
import time
import hashlib

CLIENT_SIDE = kgp.SOUTH
DEPTH = 5

def evaluate(state : kgp.Board) -> int:
    # return sum(state.south_pits) - sum(state.north_pits) + 2 * (state.south - state.north)
    return state[kgp.SOUTH] - state[kgp.NORTH]

def search(state : kgp.Board, depth : int, side : bool, alpha = -math.inf, beta = math.inf) -> (int, int):
    """
    Searches the best move to a given board state\n
    Returns a move and its evaluation
    """
    returns = []
    for move in state.legal_moves(side):
        if depth <= 0:
            returns.append((evaluate(state), move))
            continue

        new_board, repeat_move = state.sow(side, move)
        if new_board.is_final():
            returns.append((evaluate(new_board), move))
            continue

        # Depth search
        result = search(
            state = new_board,
            depth = depth - 1,
            side  = repeat_move == side, # XNOR
            alpha = alpha,
            beta  = beta
        )
        returns.append((result[0], move))

        if side: # Min Player
            if result[0] < alpha: break
            beta = min(beta, result[0])
        else: # Max Player
            if result[0] > beta: break
            alpha = max(alpha, result[0])
        
    if side:
        return min(returns, key=lambda x: x[0])
    return max(returns, key=lambda x: x[0])
    
    
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