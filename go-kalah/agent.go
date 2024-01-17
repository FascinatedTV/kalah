package main

import (
	"bufio"
	"fmt"
	. "game"
	"os"
	"sort"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	text, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("stop")
		return
	}
	board, err := Parse(text)

	//board, err := Parse("<8,0,2,9,9,9,9,8,8,8,8,0,9,9,0,10,10,10,10>")

	if err != nil {
		fmt.Println(err)
		return
	}

	_, move := Search(board, South, 10, -1000, 1000)
	fmt.Print(move)
}

func Evaluate(state *Board, side Side) int {
	return int(state.Store(side) - state.Store(!side))
}

func Sum(numbers []uint) (sum uint) {
	for _, number := range numbers {
		sum += number
	}
	return
}

type Order struct {
	move  uint
	score int
}

func EvaluateForOrdering(state *Board, side Side, move uint) int {
	newState := state.Copy()
	isRepeat := newState.Sow(side, move)

	switch {
	case isRepeat:
		return 1
	case newState.Store(side)-state.Store(side) > 1:
		return 0
	case Sum(newState.Pits(side))-Sum(state.Pits(side)) == 0:
		return 2
	case Sum(newState.Pits(!side))-Sum(state.Pits(side)) > 0:
		return 3
	}
	return 4
}

func Search(state *Board, side Side, depth, alpha, beta int) (int, uint) {
	if state.Over() || depth <= 0 {
		return Evaluate(state, side), 0
	}

	//var move, bestMove uint
	//for ; move < state.Size; move++ {
	//	if state.Legal(South, move) {
	//		break
	//	}
	//}

	//if move == state.Size {
	//	return color * Evaluate(state), 0
	//}

	//newState := state.Copy()
	//isRepeat := newState.Sow(South, move)
	//var score float64
	//
	//// First Move
	//if isRepeat {
	//	score, _ = Search(newState, depth-1, alpha, beta)
	//} else {
	//	score, _ = Search(newState.Mirror(), depth-1, -beta, -alpha)
	//	score = -score
	//}
	//
	//if score > alpha {
	//	alpha, bestMove = score, move
	//}
	//if alpha >= beta {
	//	return alpha, bestMove
	//}

	var newState *Board
	var score, bestScore = 0, -1000
	var move, bestMove uint
	var isRepeat bool

	// Tree ordering
	orderedMoves := make([]Order, 0, state.Size)
	for ; move < state.Size; move++ {
		if !state.Legal(side, move) {
			continue
		}
		orderedMoves = append(orderedMoves, Order{move, EvaluateForOrdering(state, side, move)})
	}
	sort.Slice(orderedMoves, func(i, j int) bool {
		return orderedMoves[i].score < orderedMoves[j].score
	})

	// For each move
	for _, m := range orderedMoves {
		move = m.move
		if !state.Legal(side, move) {
			continue
		}

		newState = state.Copy()
		isRepeat = newState.Sow(side, move)

		if isRepeat {
			score, _ = Search(newState, side, depth-1, alpha, beta)
		} else {
			score, _ = Search(newState, !side, depth-1, -beta, -alpha)
			score = -score
		}

		//if score > alpha && score < beta {
		//	if isRepeat {
		//		score, _ = Search(newState, depth-1, alpha, beta)
		//	} else {
		//		score, _ = Search(newState.Mirror(), depth-1, -beta, -alpha)
		//		score = -score
		//	}
		//}

		if score > bestScore {
			bestScore = score
			bestMove = move
		}
		alpha = max(alpha, bestScore)
		if alpha >= beta {
			break
		}

	}

	//fmt.Println(depth, bestMove)
	return bestScore, bestMove
}
