from kgp import Board, NORTH, SOUTH, connect
import math
from dotenv import load_dotenv
import time
import random
from typing import Tuple, Dict
from enum import Enum
import numpy as np

CLIENT_SIDE = SOUTH
DEPTH = 6

def getAllPits(board:Board):
    return board.north_pits + board.south_pits

class Flag(Enum):
        EXACT = 1
        LOWERBOUND = 2
        UPPERBOUND = 3

class Hash:
    def hash(self, state:Board):
        raise NotImplementedError()
    
    def update(self, old_hash:int, old_board:Board, new_board:Board):
        raise NotImplementedError()

class CustomHash(Hash):
    def __init__(self, pit_count):
        # Generiere Zufallswerte für jede Kombination aus Pit und Samenanzahl
        self.table = [random.randint(1, 2**64 - 1) for _ in range(pit_count)]

    def hash(self, state:Board):
        h = 0
        for i in getAllPits(board):
            h += i * self.table[i]
        return h

    def update(self, old_hash, old_board:Board, new_board:Board):
        """
        Aktualisiert den Hash basierend auf den Änderungen in den Pits.
        :param old_hash: Der aktuelle Hash-Wert des Bretts.
        :param pit_changes: Eine Liste von Tupeln, die die Änderungen in den Pits darstellen.
                            Jedes Tupel hat das Format (pit_index, old_seeds, new_seeds).
        :return: Der aktualisierte Hash-Wert.
        """
        all_pits_old = old_board.north_pits + old_board.south_pits
        all_pits_new = new_board.north_pits + new_board.south_pits

        for i in range(len(all_pits_new)):
            old_hash += (all_pits_new[i] - all_pits_old[i]) * self.table[i]
        
        return old_hash

class SimplifiedZobristHashing:
    def __init__(self, pit_count, max_seeds) -> None:
        # Generiere Zufallswerte für jede Kombination aus Pit und Samenanzahl
        self.table = [[random.randint(1, 2**64 - 1) for _ in range(max_seeds + 1)] for _ in range(pit_count)]

    def hash(self, board:Board) -> int:
        h = 0
        for i, seeds in enumerate(getAllPits(board)):
            h ^= self.table[i][seeds]
        return h

    def update(self, old_hash:int, old_board:Board, new_board:Board) -> int:
        """
        Aktualisiert den Hash basierend auf den Änderungen in den Pits.
        :param old_hash: Der aktuelle Hash-Wert des Bretts.
        :param pit_changes: Eine Liste von Tupeln, die die Änderungen in den Pits darstellen.
                            Jedes Tupel hat das Format (pit_index, old_seeds, new_seeds).
        :return: Der aktualisierte Hash-Wert.
        """
        for pit_index, seeds in enumerate(zip(getAllPits(old_board), getAllPits(new_board))):
            old_seeds, new_seeds = seeds
            # Entferne den alten Wert für dieses Pit
            old_hash ^= self.table[pit_index][old_seeds]

            # Füge den neuen Wert für dieses Pit hinzu
            old_hash ^= self.table[pit_index][new_seeds]

        return old_hash

class LookUpTable:
    def __init__(self, hashing:Hash) -> None:
        self.table = {}
        self.hashing = hashing
        # Key = State - Hash
        # Val = (Val, Depth, Flag, Valid)

    def getKey(self, state:Board) -> str:
        return self.hashing.hash(state)

    def lookUp(self, state:Board) -> Tuple[int,int,int]:
        """
        returns (Value, Depth, Flag)
        """
        return self.table.get(self.getKey(state), (0,-1,0))
    
    def save(self, state:Board, score:int, depth:int, flag:Flag) -> None:
        key = self.getKey(state)
        if key in self.table.keys() and depth > self.table[key][1]:
            self.table[key] = (score, depth, flag)




def evaluate(state : Board) -> int:
    # return sum(state.south_pits) - sum(state.north_pits) + 2 * (state.south - state.north)
    return state[SOUTH] - state[NORTH]

def eval_approach(state: Board, side:bool, move:int) -> int:
    next_state, again = state.sow(side,move)
    return next_state[side] + int(again)

def search(tt_table: LookUpTable, state : Board, depth : int, side : bool, alpha = -math.inf, beta = math.inf) -> (int, int):
    """
    Searches the best move to a given board state\n
    Returns a move and its evaluation
    """
    tt_entry =  tt_table.lookUp(state)
    if tt_entry[1] >= depth:
        if tt_entry[2] == Flag.EXACT:
            return tt_entry[0], None
        if tt_entry[2] == Flag.LOWERBOUND:
            alpha = max(alpha, tt_entry[0])
        else:
            beta = min(beta, tt_entry[0])
        
        if alpha > beta: return tt_entry[0]
    

    if depth <= 0 or state.is_final():
        return pow(-1, int(side)) * evaluate(state), None
    
    maxScore = -math.inf
    bestMove = -1    
    for move in sorted(state.legal_moves(side), key=lambda x: -eval_approach(state, side, x)):
    # for move in state.legal_moves(side):
        new_board, repeat_move = state.sow(side, move)
        sign, n_alpha, n_beta, n_side = (1, alpha, beta, side) if repeat_move else (-1, -beta, -alpha, not side)
        result = sign * search(
            tt_table = tt_table,
            state = new_board,
            depth = depth - 1,
            side  = n_side,
            alpha = n_alpha,
            beta  = n_beta
        )[0]

        if result > maxScore:
            maxScore, bestMove = result, move

        alpha = max(alpha, result)
        if alpha >= beta: break

    flag = Flag.EXACT
    if maxScore < alpha:
        flag = Flag.UPPERBOUND
    elif result > beta:
        flag = Flag.LOWERBOUND

    tt_table.save(state, maxScore, depth, flag)

    return maxScore, bestMove
    
    
    
def agent_id(state : Board):
    for i in range(1,16):
        start = time.time()
        result = search(
            state,
            i,
            CLIENT_SIDE
        )
        end = time.time()
        print(f"[{i}] {result} - {end - start}")
        yield result[1]

def getAgent():
    tt_table = None
    def agent(state : Board):
        nonlocal tt_table
        if tt_table is None:
            tt_table = LookUpTable(
                ZobristHashing(state.size * 2, sum(state.north_pits) + sum(state.south_pits)).hash_board
            )
        start = time.time()
        result = search(
            tt_table,
            state,
            DEPTH,
            CLIENT_SIDE
        )
        end = time.time()
        print(f"{result} - {end - start}")
        yield result[1]
    return agent


if __name__ == "__main__":

    import os
    load_dotenv()
    connect(
        getAgent(),
        host="localhost",
        debug=True,
        token=os.getenv("TOKEN"),
        name="ABP",
        authors=["Niklas Haas"]
    )