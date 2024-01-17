// Kalah Board Implementation Tests
//
// Copyright (c) 2021, 2022  Philip Kaludercic
//
// This file is part of go-kgp.
//
// go-kgp is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License,
// version 3, as published by the Free Software Foundation.
//
// go-kgp is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public
// License, version 3, along with go-kgp. If not, see
// <http://www.gnu.org/licenses/>

package game

import (
	"reflect"
	"testing"
)

func TestLegal(t *testing.T) {
	for i, test := range []struct {
		start *Board
		move  uint
		side  Side
		legal bool
	}{
		{
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  0,
			side:  North,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{5, 5, 5, 5},
				South:     0,
				SouthPits: []uint{5, 5, 5, 5},
			},
			move:  2,
			side:  North,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  2,
			side:  North,
			legal: true,
		}, {
			start: &Board{
				North:     1,
				NorthPits: []uint{3, 3, 3},
				South:     1,
				SouthPits: []uint{3, 3, 3},
			},
			move:  1,
			side:  South,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{9, 9, 9},
				South:     0,
				SouthPits: []uint{9, 9, 9},
			},
			move:  0,
			side:  North,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{1, 0, 3},
			},
			move:  0,
			side:  South,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 0, 0},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  0,
			side:  North,
			legal: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{0, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  0,
			side:  North,
			legal: false,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{0, 0, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  0,
			side:  North,
			legal: false,
		},
	} {
		legal := test.start.Legal(test.side, test.move)
		if test.legal != legal {
			t.Errorf("(%d) Didn't recognize illegla move", i)
		}
	}
}

func TestSow(t *testing.T) {
	// FIXME: adapt test cases

	for i, test := range []struct {
		start, end *Board
		move       uint
		side       Side
		again      bool
	}{
		{
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			end: &Board{
				North:     1,
				NorthPits: []uint{0, 4, 4},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			move:  0,
			side:  North,
			again: true,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{5, 5, 5, 5},
				South:     0,
				SouthPits: []uint{5, 5, 5, 5},
			},
			end: &Board{
				North:     1,
				NorthPits: []uint{5, 5, 0, 6},
				South:     0,
				SouthPits: []uint{6, 6, 6, 5},
			},
			move: 2,
			side: North,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			end: &Board{
				North:     1,
				NorthPits: []uint{3, 3, 0},
				South:     0,
				SouthPits: []uint{4, 4, 3},
			},
			move: 2,
			side: North,
		}, {
			start: &Board{
				North:     1,
				NorthPits: []uint{3, 3, 3},
				South:     1,
				SouthPits: []uint{3, 3, 3},
			},
			end: &Board{
				North:     1,
				NorthPits: []uint{4, 3, 3},
				South:     2,
				SouthPits: []uint{3, 0, 4},
			},
			move: 1,
			side: South,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{9, 9, 9},
				South:     0,
				SouthPits: []uint{9, 9, 9},
			},
			end: &Board{
				North:     1,
				NorthPits: []uint{1, 11, 11},
				South:     0,
				SouthPits: []uint{10, 10, 10},
			},
			move: 0,
			side: North,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{1, 0, 3},
			},
			end: &Board{
				North:     0,
				NorthPits: []uint{3, 0, 3},
				South:     4,
				SouthPits: []uint{0, 0, 3},
			},
			move: 0,
			side: South,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{7, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			end: &Board{
				North:     6,
				NorthPits: []uint{0, 4, 4},
				South:     0,
				SouthPits: []uint{4, 4, 0},
			},
			move: 0,
			side: North,
		}, {
			start: &Board{
				North:     0,
				NorthPits: []uint{1, 0, 1},
				South:     0,
				SouthPits: []uint{0, 0, 1},
			},
			end: &Board{
				North:     0,
				NorthPits: []uint{0, 1, 1},
				South:     0,
				SouthPits: []uint{0, 0, 1},
			},
			move: 0,
			side: North,
		},
	} {
		again := test.start.Sow(test.side, test.move)
		if test.again != again {
			t.Errorf("(%d) Didn't recognize repeat move", i)
		} else if !reflect.DeepEqual(test.start, test.end) {
			t.Errorf("(%d) Expected %s, got %s", i, test.end, test.start)
		}
	}
}

func TestOverFor(t *testing.T) {
	for _, test := range []struct {
		board *Board
		side  Side
		over  bool
	}{
		{
			board: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			side: North,
			over: false,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			side: South,
			over: false,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{0, 0, 0},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			side: North,
			over: true,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{0, 0, 0},
				South:     0,
				SouthPits: []uint{3, 3, 3},
			},
			side: South,
			over: false,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{0, 0, 0},
			},
			side: North,
			over: false,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{0, 0, 0},
			},
			side: South,
			over: true,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{0, 0, 0},
				South:     0,
				SouthPits: []uint{0, 0, 0},
			},
			side: North,
			over: true,
		}, {
			board: &Board{
				North:     0,
				NorthPits: []uint{0, 0, 0},
				South:     0,
				SouthPits: []uint{0, 0, 0},
			},
			side: South,
			over: true,
		},
	} {
		over, _ := test.board.OverFor(test.side)
		if over != test.over {
			t.Fail()
		}
	}
}

func TestOutcome(t *testing.T) {
	for i, test := range []struct {
		board   *Board
		outcome Outcome
	}{
		{
			board: &Board{
				North: 0,
				South: 1,
			},
			outcome: WIN,
		}, {
			board: &Board{
				North: 1,
				South: 0,
			},
			outcome: LOSS,
		}, {
			board: &Board{
				North: 0,
				South: 0,
			},
			outcome: DRAW,
		}, {
			board: &Board{
				North: 1,
				South: 1,
			},
			outcome: DRAW,
		}, {
			board: &Board{
				North:     2,
				South:     1,
				SouthPits: []uint{1, 1, 1},
			},
			outcome: WIN,
		}, {
			board: &Board{
				North:     0,
				South:     2,
				NorthPits: []uint{1, 1, 1},
			},
			outcome: LOSS,
		},
	} {
		outcome := test.board.Outcome(South)
		if outcome != test.outcome {
			t.Errorf("(%d) Expected %d, got %d", i, test.outcome, outcome)
		}
	}
}

func TestCopy(t *testing.T) {
	board := MakeBoard(3, 3)
	copyBoard := board.Copy()
	// Ensure that the copy is a deep copy and not a reference
	if &board.NorthPits == &copyBoard.NorthPits || &board.SouthPits == &copyBoard.SouthPits {
		t.Errorf("Copy is not a deep copy")
	}
	// Ensure that the boards are equal
	if !board.Equal(copyBoard) {
		t.Errorf("Boards are not equal after copy")
	}
}

func TestParse(t *testing.T) {
	for i, test := range []struct {
		input  string
		output *Board
		fail   bool
	}{
		{
			input: "<3,0,0,0,0,0,3,3,3>", output: &Board{
				North:     0,
				NorthPits: []uint{3, 3, 3},
				South:     0,
				SouthPits: []uint{0, 0, 0},
			},
		},
		{
			input: "<2, 0,0, 0,1, 0,0>",
			output: &Board{
				North:     0,
				NorthPits: []uint{0, 0},
				South:     0,
				SouthPits: []uint{0, 1},
			},
		},
		{
			input: "<2,1,2,3,4,5,6>", output: &Board{
				North:     2,
				NorthPits: []uint{5, 6},
				South:     1,
				SouthPits: []uint{3, 4},
			},
		},
		{
			input: "<5,1,2,3,4,5,6,7,8,9,10,11,12>", output: &Board{
				North:     2,
				NorthPits: []uint{8, 9, 10, 11, 12},
				South:     1,
				SouthPits: []uint{3, 4, 5, 6, 7},
			},
		},
		{
			input: "<1,0,0,0,0>", output: &Board{
				North:     0,
				NorthPits: []uint{0},
				South:     0,
				SouthPits: []uint{0},
			},
		},
		{
			input: " <1	,0 , 0,0 , 	 0>  ", output: &Board{
				North:     0,
				NorthPits: []uint{0},
				South:     0,
				SouthPits: []uint{0},
			},
		},
		{
			input: " < 1 , 0 , 0 , 0 , 0 > ", output: &Board{
				North:     0,
				NorthPits: []uint{0},
				South:     0,
				SouthPits: []uint{0},
			},
		},
		{input: "<0>", fail: true},
		{input: "<0,1,1>", fail: true},
		{input: "<1,1,1,1>", fail: true},
		{input: "<1,1,1,1,1,1>", fail: true},
		{input: "1,1,1,1,1", fail: true},
		{input: "<1,1,1,1,1", fail: true},
		{input: "1,1,1,1,1>", fail: true},
		{input: "<1,1,1,1,a>", fail: true},
	} {
		parse, err := Parse(test.input)
		if test.fail {
			if err == nil {
				t.Errorf("(%d) Expected error", i)
			}
		} else {
			if err != nil {
				t.Errorf("(%d) Failed with %q", i, err)
			} else if parse.String() != test.output.String() {
				t.Errorf("(%d) Expected %s, got %s",
					i, test.output, parse)
			}
		}
	}
}
