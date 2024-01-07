from kgp import Board, NORTH, SOUTH, connect
from dotenv import load_dotenv
from typing import Tuple, Dict
from enum import Enum
import multiprocess as mp
import random
import utils
import math
import time


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

# class CustomHash(Hash):
#     def __init__(self, pit_count):
#         # Generiere Zufallswerte für jede Kombination aus Pit und Samenanzahl
#         self.table = [random.randint(1, 2**64 - 1) for _ in range(pit_count)]

#     def hash(self, state:Board):
#         h = 0
#         for i in getAllPits(board):
#             h += i * self.table[i]
#         return h

#     def update(self, old_hash, old_board:Board, new_board:Board):
#         """
#         Aktualisiert den Hash basierend auf den Änderungen in den Pits.
#         :param old_hash: Der aktuelle Hash-Wert des Bretts.
#         :param pit_changes: Eine Liste von Tupeln, die die Änderungen in den Pits darstellen.
#                             Jedes Tupel hat das Format (pit_index, old_seeds, new_seeds).
#         :return: Der aktualisierte Hash-Wert.
#         """
#         all_pits_old = old_board.north_pits + old_board.south_pits
#         all_pits_new = new_board.north_pits + new_board.south_pits

#         for i in range(len(all_pits_new)):
#             old_hash += (all_pits_new[i] - all_pits_old[i]) * self.table[i]
        
#         return old_hash

class ZobristHashing(Hash):
    def __init__(self, size:int, max_seeds:int):
        # Initialisieren der Zobrist-Tabelle für das Brett und Spielstände
        self.zobrist_table = {
            'north_pits': [[random.randint(1, 2**64 - 1) for _ in range(size)] for _ in range(max_seeds)],
            'south_pits': [[random.randint(1, 2**64 - 1) for _ in range(size)] for _ in range(max_seeds)],
            'north_score': random.randint(1, 2**64 - 1),
            'south_score': random.randint(1, 2**64 - 1)
        }

    def hash(self, state:Board):
        # Hashen der Board-Positionen und Spielstände
        h = 0
        for i in range(state.size):
            h ^= self.zobrist_table['north_pits'][state.north_pits[i]][i]
            h ^= self.zobrist_table['south_pits'][state.south_pits[i]][i]

        # Hashen der Spielstände
        h ^= self.zobrist_table['north_score'] * state.north
        h ^= self.zobrist_table['south_score'] * state.south

        return h
    
    def update(self, old_hash: int, old_board: Board, new_board: Board) -> int:
        """
        Aktualisiert den Hash basierend auf den Änderungen in den Pits und Scores.
        :param old_hash: Der aktuelle Hash-Wert des Bretts.
        :param old_board: Das vorherige Board.
        :param new_board: Das aktualisierte Board.
        :return: Der aktualisierte Hash-Wert.
        """
        # Aktualisieren der Hashes für die Pits
        for pit_index in range(old_board.size):
            old_north_seeds, new_north_seeds = old_board.north_pits[pit_index], new_board.north_pits[pit_index]
            old_south_seeds, new_south_seeds = old_board.south_pits[pit_index], new_board.south_pits[pit_index]

            # Entferne den alten Wert für dieses Pit
            old_hash ^= self.zobrist_table['north_pits'][old_north_seeds][pit_index]
            old_hash ^= self.zobrist_table['south_pits'][old_south_seeds][pit_index]

            # Füge den neuen Wert für dieses Pit hinzu
            old_hash ^= self.zobrist_table['north_pits'][new_north_seeds][pit_index]
            old_hash ^= self.zobrist_table['south_pits'][new_south_seeds][pit_index]

        # Aktualisieren der Hashes für die Scores
        old_hash ^= self.zobrist_table['north_score'] * old_board.north
        old_hash ^= self.zobrist_table['south_score'] * old_board.south
        old_hash ^= self.zobrist_table['north_score'] * new_board.north
        old_hash ^= self.zobrist_table['south_score'] * new_board.south

        return old_hash

class SimplifiedZobristHashing(Hash):
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
    
class TranspositionTable:
    def __init__(self) -> None:
        self.manager = mp.Manager()
        self.table = self.manager.dict()
        self.hits = self.manager.Value("i", 0)
        self.entries = self.manager.Value("i", 0)
        self.lock = self.manager.Lock()

    def lookUp(self, hash) -> Tuple[int, int, int]:
        with self.lock:
            if hash in self.table.keys(): self.hits.set(self.hits.get() + 1)
            return self.table.get(hash, (0, -1, 0))

    def save(self, hash, score: int, depth: int, flag: int) -> bool:
        with self.lock:
            if hash not in self.table.keys(): self.entries.set(self.entries.get() + 1)
            self.table[hash] = (score, depth, flag)
        return True
    
    def persist(self):
        pass

def evaluate(state : Board) -> int:
    # return sum(state.south_pits) - sum(state.north_pits) + 2 * (state.south - state.north)
    return state[SOUTH] - state[NORTH]

def eval_approach(state: Board, side:bool, move:int) -> int:
    next_state, again = state.sow(side,move)
    return next_state[side] + int(again)

def getHashfunction(board:Board) -> TranspositionTable:
    return ZobristHashing(board.size, sum(getAllPits(board)) + board.north + board.south)

def getSearch(tt_table : TranspositionTable, hash_function:Hash):
    def search(state : Board, depth : int, side : bool, alpha = -math.inf, beta = math.inf) -> (int, int):
        """
        Searches the best move to a given board state\n
        Returns a move and its evaluation
        """
        nonlocal tt_table, hash_function
        tt_entry =  tt_table.lookUp(hash_function.hash(state))
        if tt_entry[1] >= depth:
            if tt_entry[2] == 1:
                return tt_entry[0], None
            elif tt_entry[2] == 2:
                alpha = max(alpha, tt_entry[0])
            else:
                beta = min(beta, tt_entry[0])
            
            if alpha > beta: return tt_entry[0], None
        

        if depth <= 0 or state.is_final():
            return pow(-1, int(side)) * evaluate(state), None
        
        maxScore = -math.inf
        bestMove = -1    
        for move in sorted(state.legal_moves(side), key=lambda x: -eval_approach(state, side, x)):
        # for move in state.legal_moves(side):
            new_board, repeat_move = state.sow(side, move)
            sign, n_alpha, n_beta, n_side = (1, alpha, beta, side) if repeat_move else (-1, -beta, -alpha, not side)
            result = sign * search(
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

        flag = 1
        if maxScore < alpha:
            flag = 2
        elif result > beta:
            flag = 3

        tt_table.save(hash_function.hash(state), maxScore, depth, flag)

        return maxScore, bestMove
    return search

# tt_table = None
def getAgent(tt_table:TranspositionTable):
    def agent(state : Board):
        nonlocal tt_table
        h = getHashfunction(state)
        search = getSearch(tt_table, h)
        start = time.time()
        for i in range(1,16):
            result = search(
                state,
                i,
                CLIENT_SIDE
            )
            yield result[1]
            end = time.time()
            print(utils.colors.fg.lightgreen if (end-start) <= 5.0 else utils.colors.fg.lightred, end="")
            print(f"[{i}] {result} - {end - start}", end="")
            print(utils.colors.reset, end=" | ")
            print(f"Cache Hits: {tt_table.hits.get()} - Cache entries {tt_table.entries.get()}")
            # start = end
    return agent

# def agent(state : Board):
#     nonlocal tt_table
#     if tt_table is None:
#         tt_table = getTranspositionTable(state)
#         search = getSearch(tt_table)
        
#     start = time.time()
#     result = search(
#         state,
#         DEPTH,
#         CLIENT_SIDE
#     )
#     end = time.time()
#     print(f"{result} - {end - start}")
#     yield result[1]

def handleAgent(agent, state:Board, ref:int):
    for move in agent(state):
        print(ref, " ", move)

if __name__ == '__main__':
    mp.freeze_support() # Do not touch
    tt_table = TranspositionTable()
    # b = Board.parse("<8,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8>")

    # a = getAgent(tt_table)

    # agent_1 = mp.Process(name="agent-1", args=(a, b, 1), target=handleAgent)
    # agent_1.start()
    # agent_1.join()
    # agent_1.kill()

    # new_board, _ = b.sow(False, 1)
    
    # agent_2 = mp.Process(name="agent-2", args=(a, new_board, 2), target=handleAgent)
    # agent_2.start()
    # agent_2.join()
    # agent_2.kill()


    import os
    load_dotenv()
    connect(
        # getNegamaxAgent(),
        getAgent(tt_table),
        host="localhost",
        debug=True,
        token=os.getenv("TOKEN"),
        name=os.getenv("NAME"),
        authors=[os.getenv("AUTHOR")]
    )