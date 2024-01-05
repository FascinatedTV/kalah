#!/usr/bin/env python3

# To write a Python client, we first need to import kgp.  In case
# "kgp.py" is not in the current working directory, adjust your
# PYTHONPATH.

import kgp
import time
from functools import lru_cache

# We will be using a simple evaluation strategy: Compare the
# difference of stones in my (north) store vs. the opponents store
# (south).  kgp.py always assumes the agent is on the south side of
# the board, to avoid confusion.

def evaluate(state):
    return state[kgp.SOUTH]-state[kgp.NORTH]

def evaluate_sort_max(state,side,move):
    next_state, again = state.sow(side,move)
    return next_state[side] + int(again)

#%% MinMax alpha beta
"""
def alpha_beta_search(state, depth, side, alpha=float('-inf'), beta=float('inf')):
    def child(move):
        if depth <= 0:
            return evaluate(state), move
        new_state, again = state.sow(side, move)
        if new_state.is_final():
            return evaluate(new_state), move
        if again:
            child_value, _ = alpha_beta_search(new_state, depth, side, alpha, beta)
            return child_value, move
        else:
            child_value, _ = alpha_beta_search(new_state, depth-1, not side, alpha, beta)
            return child_value, move
    

    legal_moves = state.legal_moves(side)

    if depth == 0 or state.is_final():
        return evaluate(state), None  # Return evaluated value and no specific move/state

    if side == kgp.SOUTH: # Max-Player
        legal_moves_sort = sorted(legal_moves,reverse = True, key=lambda move: evaluate_sort_max(state,side,move)) #sorting to maximize
        best_move = None
        value = float('-inf')
        for move in legal_moves_sort:
            child_value, _ = child(move)
            if child_value > value:
                value = child_value
                best_move = move
            alpha = max(alpha, value)
            if value >= beta:
                break  # Beta-Cutoff
        return value, best_move  # Return evaluated value and best move

    else:  # Min-Player
        legal_moves_sort = sorted(legal_moves,reverse = True, key=lambda move: evaluate_sort_max(state,side,move)) #sorting to minimize nodes
        best_move = None
        value = float('inf')
        for move in legal_moves_sort:
            child_value, _ = child(move)
            if child_value < value:
                value = child_value
                best_move = move
            beta = min(beta, value)
            if value <= alpha:
                break
        return value, best_move  # Return evaluated value and best move
"""

#%% NegaMax
"""
def alpha_beta_negamax_search(state, depth, side, alpha=float('-inf'), beta=float('inf'), sign=1, eval = evaluate):
    def child(move):
        if depth <= 0:
            evaluation = eval(state)
            return sign*evaluation, move
        new_state, again = state.sow(side, move)
        if new_state.is_final():
            evaluation = eval(new_state)
            return sign*evaluation, move
        if again:
            child_value, _ = alpha_beta_negamax_search(new_state, depth, side, alpha, beta, sign, eval)
            return child_value, move
        else:
            child_value, _ = alpha_beta_negamax_search(new_state, depth-1, not side, -beta, -alpha, sign*(-1), eval)
            child_value = -child_value  #because of negamax algorithm
            return child_value, move
    
    if depth == 0 or state.is_final():
        evaluation = eval(state)
        return sign*evaluation, None  # Return evaluated value and no specific move/state
    
    legal_moves = state.legal_moves(side)
    legal_moves_sort = sorted(legal_moves,reverse = True, key=lambda move: evaluate_sort_max(state,side,move))
    best_move = None
    value = float('-inf')
    for move in legal_moves_sort:
        child_value, _ = child(move)
        if child_value > value:
            value = child_value
            best_move = move
        alpha = max(alpha, value)
        if alpha >= beta:
            break # Cut-Off
    return value, best_move  # Return evaluated value and best move
"""
#%% NegaMax with TT
def alpha_beta_negamax_searchTT(state, depth, side, alpha=float('-inf'), beta=float('inf'), sign=1, eval = evaluate, transposition_table={}, cache_info=None):
    if cache_info is None:
        cache_info = {'cache_size': 0, 'cache_hits': 0}
    
    @lru_cache(maxsize=2^20)    # TODO: Find optimal size and evaluate cachehits
    def child(move):
        if depth <= 0:
            evaluation = eval(state)
            return sign*evaluation, move
        new_state, again = state.sow(side, move)
        if new_state.is_final():
            evaluation = eval(new_state)
            return sign*evaluation, move
        if again:
            child_value, _ = alpha_beta_negamax_searchTT(new_state, depth, side, alpha, beta, sign, eval, transposition_table,cache_info)
            return child_value, move
        else:
            child_value, _ = alpha_beta_negamax_searchTT(new_state, depth-1, not side, -beta, -alpha, sign*(-1), eval, transposition_table,cache_info)
            child_value = -child_value  #because of negamax algorithm
            return child_value, move
    
    if depth == 0 or state.is_final():
        evaluation = eval(state)
        return sign*evaluation, None  # Return evaluated value and no specific move/state
    
    def generate_key(state):
        data = [state.size,
                state.south,            #hier aauch?
                state.north,            #TODO: hier ne Null rein gegen Hash collisions
                *state.south_pits,      # und hier vielleicht auch
                *state.north_pits]
        key = int(''.join(map(str,data)))
        return key
    hash_key = hash(generate_key(state))  # Compute a hash key for the current state (you may need to implement a hash function)

    # Check if the current state is in the transposition table
    if hash_key in transposition_table:
        entry = transposition_table[hash_key]
        cache_info['cache_hits'] += 1
        if entry['depth'] >= depth:
            if entry['flag'] == 'EXACT':
                return entry['score'], entry['best_move']
            elif entry['flag'] == 'LOWERBOUND':
                alpha = max(alpha, entry['score'])
            elif entry['flag'] == 'UPPERBOUND':
                beta = min(beta, entry['score'])
            if alpha >= beta:
                return entry['score'], entry['best_move']

    legal_moves = state.legal_moves(side)
    legal_moves_sort = sorted(legal_moves,reverse = True, key=lambda move: evaluate_sort_max(state,side,move))
    best_move = None
    value = float('-inf')
    for move in legal_moves_sort:
        child_value, _ = child(move)
        if child_value > value:
            value = child_value
            best_move = move
        alpha = max(alpha, value)
        if alpha >= beta:
            break # Cut-Off
    # Store the current state in the transposition table
    global cache_size
    if value <= alpha:
        cache_info['cache_size'] += 1
        transposition_table[hash_key] = {'depth': depth, 'score': value, 'flag': 'UPPERBOUND', 'best_move': best_move}
    elif value >= beta:
        cache_info['cache_size'] += 1
        transposition_table[hash_key] = {'depth': depth, 'score': value, 'flag': 'LOWERBOUND', 'best_move': best_move}
    else:
        transposition_table[hash_key] = {'depth': depth, 'score': value, 'flag': 'EXACT', 'best_move': best_move}
        cache_info['cache_size'] += 1
    return value, best_move  # Return evaluated value and best move

#%% Agent and Main
transposition_table = {}
cache_info = {'cache_size': 0, 'cache_hits': 0}
def agent(state):
    global cache_hits
    global cache_size
    for depth in range(1, 32, 2): 
        start = time.time()
        out = alpha_beta_negamax_searchTT(state, depth, kgp.SOUTH,transposition_table=transposition_table,cache_info=cache_info)[1]
        cache_size = cache_info['cache_size']
        cache_hits = cache_info['cache_hits']
        end = time.time()
        print(depth,": S ",state[kgp.SOUTH]," | ", state[kgp.NORTH]," N time: ", end-start, " Cached: ", cache_size, " Hits: ", cache_hits, " Total: ", len(transposition_table))
        yield out
    

if __name__ == "__main__":
    import os
    kgp.connect(agent, host="localhost", debug=True, token=os.getenv("TOKEN"), name="NegaMaxTT2-LRU 2^20 info")
