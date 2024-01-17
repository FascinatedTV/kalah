from kgp import Board, NORTH, SOUTH, connect
from dotenv import load_dotenv
from typing import Tuple
from JenkisHash import hashlittle
import utils
import math
import time
import os

# Example board representation
# <8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>
# <size, north, south, *north_pits, *south_pits>

EXACT = 1
UPPERBOUND = 2
CLIENT_SIDE = SOUTH
DEPTH = 6

def getAllPits(board:Board):
    return board.north_pits + board.south_pits

class TranspositionTable:
    def __init__(self) -> None:
        self.table = dict()
        self.hits = 0
        self.entries = 0

    def lookUp(self, hash) -> Tuple[int, int, int]:
        if hash in self.table.keys(): self.hits += 1
        return self.table.get(hash, (0, -1, 0, -1))
    
    def save(self, hash, score: int, depth: int, flag: int, move:int = -1) -> bool:
        if hash not in self.table.keys(): self.entries += 1
        self.table[hash] = (score, depth, flag, move)
        return True

    def persist(self):
        pass

def evaluate(state : Board, side:bool) -> int:
    # return sum(state.south_pits) - sum(state.north_pits) + 2 * (state.south - state.north)
    return state[side] - state[not side]

def eval_approach(state: Board, side:bool, move:int) -> int:
    next_state, again = state.sow(side,move)
    return evaluate(next_state, side) + int(again) * 3


class Agent:
    def __init__(self):
        self.t_table = TranspositionTable()
        self.stopFlag = False
        self.halfPoints = 0

    def agent(self, state : Board):
        self.stopFlag = False
        # if self.halfPoints == 0:
        #     self.halfPoints = (sum(state.north_pits + state.south_pits) + state.north + state.south) // 2
        start = time.time()
        for i in range(1,16):
            self.t_table.hits = 0
            if self.stopFlag: break
            result = self.search(
                state,
                i,
                CLIENT_SIDE
            )
            # print("Yield: ", self.stopFlag)
            if not self.stopFlag:
                yield result[1]
            end = time.time()
            print(utils.colors.fg.lightgreen if (end-start) <= 5.0 else utils.colors.fg.lightred, end="")
            print(f"[{i}] {result} - {end - start}", end="")
            print(utils.colors.reset, end=" | ")
            print(f"Cache Hits: {self.t_table.hits} - Cache entries {self.t_table.entries}")
            # start = end

    def search(self, state: Board, depth: int, side: bool, alpha=-math.inf, beta=math.inf) -> (int, int):
        """
        Searches the best move for a given board state
        Returns a move and its evaluation
        """
        if agent.stopFlag or depth <= 0 or state.is_final():
            return evaluate(state, side), -3
        

        h = hashlittle(str(state))
        tt_entry = agent.t_table.lookUp(h)
        if tt_entry is not None and tt_entry[1] >= depth:
            if tt_entry[2] == EXACT:
                return tt_entry[0], tt_entry[3]
            elif tt_entry[2] == UPPERBOUND:
                beta = min(beta, tt_entry[0])

            if alpha >= beta:
                return tt_entry[0], tt_entry[3]


        allMoves = sorted(state.legal_moves(side), key=lambda x: -eval_approach(state, side, x))
        bestMove = -1

        for move in allMoves:
            new_board, repeat_move = state.sow(side, move)
            sign = 1 if repeat_move else -1
            n_side = side if repeat_move else not side

            if move == allMoves[0]:
                n_alpha, n_beta = (alpha, beta) if repeat_move else (-beta, -alpha)
            else:
                n_alpha, n_beta = (alpha, -alpha - 1) if repeat_move else (-alpha - 1, -alpha)

            result = sign * self.search(state=new_board, depth=depth - 1, side=n_side, alpha=n_alpha, beta=n_beta)[0]

            if move != allMoves[0] and alpha < result < beta:
                n_alpha, n_beta = (alpha, beta) if repeat_move else (-beta, -alpha)
                result = sign * self.search(state=new_board, depth=depth - 1, side=n_side, alpha=n_alpha, beta=n_beta)[0]

            if result > alpha:
                alpha, bestMove = result, move

            if alpha >= beta:
                break

        if agent.stopFlag:
            return 0, -4

        flag = EXACT if alpha > beta else UPPERBOUND
        agent.t_table.save(h, alpha, depth, flag, bestMove)

        return alpha, bestMove

if __name__ == '__main__':
    agent = Agent()

    import os
    load_dotenv()
    connect(
        # getNegamaxAgent(),
        agent,
        host="localhost",
        debug=True,
        token=os.getenv("TOKEN"),
        name=os.getenv("NAME"),
        authors=[os.getenv("AUTHOR")]
    )