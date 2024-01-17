package game

import (
	"errors"
	"fmt"
	"math"
	"math/rand"
	"regexp"
	"strconv"
	"strings"
)

var repr = regexp.MustCompile(`^\s*<\s*(\d+(\s*,\s*\d+)+)\s*>\s*$`)

// Board represents a Kalah game
type Board struct {
	// The North and South store
	North, South uint
	// The northern pits (from right to left)
	NorthPits []uint
	// The southern pits (from left to right)
	SouthPits []uint
	Size      uint
	// The initial board size
	Init uint
}

func (b *Board) Type() (size, init uint) {
	return uint(len(b.NorthPits)), b.Init
}

func (b *Board) Pits(side Side) []uint {
	if side {
		return b.NorthPits
	} else {
		return b.SouthPits
	}
}

func (b *Board) Pit(side Side, pit uint) uint {
	if pit >= uint(len(b.NorthPits)) {
		panic("Illegal access")
	}

	if side {
		return b.NorthPits[pit]
	} else {
		return b.SouthPits[pit]
	}
}

func (b *Board) Store(side Side) uint {
	if side {
		return b.North
	} else {
		return b.South
	}
}

// create a new board with SIZE pits, each with INIT stones
func MakeBoard(size, init uint) *Board {
	board := Board{
		NorthPits: make([]uint, int(size)),
		SouthPits: make([]uint, int(size)),
		Size:      size,
	}

	for i := range board.NorthPits {
		board.NorthPits[i] = init
	}
	for i := range board.SouthPits {
		board.SouthPits[i] = init
	}
	board.Init = init

	return &board
}

func MakeRandomBoard() *Board {
	size := uint(6 + rand.Intn(6))
	b := MakeBoard(size, 0)

	for i := range b.NorthPits {
		b.NorthPits[i] = uint(rand.Intn(int(2 * size)))
	}
	for i := range b.SouthPits {
		b.SouthPits[i] = uint(rand.Intn(int(2 * size)))
	}
	b.South = uint(rand.Intn(int(4 * size)))
	b.North = uint(rand.Intn(int(4 * size)))

	return b
}

func Parse(spec string) (*Board, error) {
	match := repr.FindStringSubmatch(spec)
	if match == nil {
		return nil, errors.New("invalid specification")
	}

	var data []uint
	for _, part := range strings.Split(match[1], ",") {
		part = strings.TrimSpace(part)
		n, err := strconv.ParseUint(part, 10, 16)
		if err != nil {
			return nil, err
		}
		data = append(data, uint(n))
	}

	size := data[0]
	if size == 0 || uint(len(data)) != 1+2+size*2 {
		return nil, errors.New("invalid size")
	}

	b := MakeBoard(size, math.MaxUint)
	b.South = data[1]
	b.North = data[2]
	for i := uint(0); i < size; i++ {
		b.SouthPits[i] = data[3+i]
		b.NorthPits[i] = data[3+size+i]
	}
	return b, nil
}

// Mirror returns a mirrored represenation of the board
func (b *Board) Mirror() *Board {
	return &Board{
		North:     b.South,
		South:     b.North,
		NorthPits: b.SouthPits,
		SouthPits: b.NorthPits,
		Size:      b.Size,
		Init:      b.Init,
	}
}

// String converts a board into a KGP representation
func (b *Board) String() string {
	var buf strings.Builder

	fmt.Fprintf(&buf, "<%d,%d,%d", len(b.NorthPits), b.South, b.North)
	for _, pit := range b.SouthPits {
		fmt.Fprintf(&buf, ",%d", pit)
	}
	for _, pit := range b.NorthPits {
		fmt.Fprintf(&buf, ",%d", pit)
	}
	fmt.Fprint(&buf, ">")

	return buf.String()
}

// Legal returns true if SIDE may play move PIT
func (b *Board) Legal(side Side, pit uint) bool {
	if pit >= uint(len(b.NorthPits)) {
		return false
	}
	if side == North {
		return b.NorthPits[pit] > 0
	}
	return b.SouthPits[pit] > 0
}

func (b *Board) Moves(side Side) (count, last uint) {
	for i := uint(0); i < uint(len(b.NorthPits)); i++ {
		if b.Legal(side, i) {
			last = i
			count++
		}
	}

	return
}

// Random returns a random legal move for SIDE
func (b *Board) Random(side Side) (move uint) {
	legal := make([]uint, 0, len(b.NorthPits))

	for i := uint(0); i < uint(len(b.NorthPits)); i++ {
		if b.Legal(side, i) {
			legal = append(legal, i)
		}
	}

	// if len(legal) == true, rand.Intn panics.  This is ok, because
	// Random shouldn't be called when the game is already over.
	return legal[rand.Intn(len(legal))]
}

// Sow modifies the board by sowing PIT for player SELF
func (b *Board) Sow(self Side, pit uint) bool {
	if len(b.NorthPits) != len(b.SouthPits) {
		panic("Illegal board")
	}

	var (
		stones uint

		size = len(b.NorthPits)
		pos  = pit + 1
		side = self
	)

	if !b.Legal(self, pit) {
		panic(fmt.Sprintf("Illegal move %d by %s in %s",
			pit, self, b))
	}

	// pick up stones from pit
	if self == North {
		stones = b.NorthPits[pit]
		b.NorthPits[pit] = 0
	} else {
		stones = b.SouthPits[pit]
		b.SouthPits[pit] = 0
	}

	// distribute all stones
	for stones > 0 {
		if int(pos) > size {
			panic("Out of bounds")
		} else if int(pos) == size {
			if side == self {
				if self == North {
					b.North++
				} else {
					b.South++
				}
				stones--
			}

			side = !side
			pos = 0
		} else {
			if side == North {
				b.NorthPits[pos]++
			} else {
				b.SouthPits[pos]++
			}
			pos++
			stones--
		}
	}

	// check for repeat- or collect-move
	if pos == 0 && side == !self {
		if b.Over() {
			b.Collect()
		}

		return true
	} else if side == self && pos > 0 {
		last := int(pos - 1)
		if side == North && b.NorthPits[last] == 1 && b.SouthPits[size-1-last] > 0 {
			b.North += b.SouthPits[size-1-last] + 1
			b.SouthPits[size-1-last] = 0
			b.NorthPits[last] = 0
		} else if side == South && b.SouthPits[last] == 1 && b.NorthPits[size-1-last] > 0 {
			b.South += b.NorthPits[size-1-last] + 1
			b.NorthPits[size-1-last] = 0
			b.SouthPits[last] = 0
		}
	}

	if b.Over() {
		b.Collect()
	}

	return false
}

// OverFor returns true if the game has finished for a SIDE
//
// The second argument designates the right-most pit that would be a
// legal move, iff the game is not over for SIDE.
func (b *Board) OverFor(side Side) (bool, uint) {
	var pits []uint
	switch side {
	case North:
		pits = b.NorthPits
	case South:
		pits = b.SouthPits
	}

	for i := range pits {
		if pits[i] > 0 {
			return false, uint(i)
		}
	}
	return true, 0
}

// Over returns true if the game is over for either side
func (b *Board) Over() bool {
	var stones uint

	for _, pit := range b.NorthPits {
		stones += pit
	}
	for _, pit := range b.SouthPits {
		stones += pit
	}
	stones += b.North
	stones += b.South

	if b.North > stones/2 || b.South > stones/2 {
		return true
	}

	north, _ := b.OverFor(North)
	south, _ := b.OverFor(South)
	return north || south
}

// Calculate the outcome for SIDE
func (b *Board) Outcome(side Side) Outcome {
	var north, south uint

	for _, pit := range b.NorthPits {
		north += pit
	}
	for _, pit := range b.SouthPits {
		south += pit
	}

	if !b.Over() {
		panic("Cannot determine outcome of unfinished game")
	}

	north += b.North
	south += b.South

	switch {
	case north > south:
		if side == North {
			return WIN
		} else {
			return LOSS
		}
	case north < south:
		if side == North {
			return LOSS
		} else {
			return WIN
		}
	default:
		return DRAW
	}
}

// Move all stones for SIDE to the Kalah on SIDE
func (b *Board) Collect() {
	var north, south uint

	if !b.Over() {
		panic("Stones may not be collected")
	}

	for i, p := range b.NorthPits {
		north += p
		b.NorthPits[i] = 0
	}

	for i, p := range b.SouthPits {
		south += p
		b.SouthPits[i] = 0
	}

	b.North += north
	b.South += south
}

// Deep copy of the board
func (b *Board) Copy() *Board {
	north := make([]uint, len(b.SouthPits))
	south := make([]uint, len(b.NorthPits))
	if copy(north, b.NorthPits) != len(b.NorthPits) {
		panic("Illegal board state")
	}
	if copy(south, b.SouthPits) != len(b.SouthPits) {
		panic("Illegal board state")
	}
	return &Board{
		North:     b.North,
		South:     b.South,
		NorthPits: north,
		SouthPits: south,
		Size:      b.Size,
		Init:      b.Init,
	}
}

func (b *Board) Equal(d *Board) bool {
	if len(b.NorthPits) != len(d.NorthPits) {
		return false
	}
	if b.South != d.South || b.North != d.North {
		return false
	}
	for i := range b.NorthPits {
		if b.SouthPits[i] != d.SouthPits[i] {
			return false
		}
		if b.NorthPits[i] != d.NorthPits[i] {
			return false
		}

	}
	return true
}
