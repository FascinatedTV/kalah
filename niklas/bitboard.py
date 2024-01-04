from bitarray import bitarray

# South | Right | North | Left
# [1,0,0,0,0,0,0,0]
# [1,0,0,0,0,0,0,0]
# [1,0,0,0,0,0,0,0]
# [0,1,0,0,0,0,0,0]
# [0,1,0,0,0,0,0,0]
# [0,1,0,0,0,0,0,0]
# [0,0,1,0,0,0,0,0]
# [0,0,1,0,0,0,0,0]
# [0,0,1,0,0,0,0,0]
# [0,0,0,0,1,0,0,0]
# [0,0,0,0,1,0,0,0]
# [0,0,0,0,1,0,0,0]
# [0,0,0,0,0,1,0,0]
# [0,0,0,0,0,1,0,0]
# [0,0,0,0,0,1,0,0]
# [0,0,0,0,0,0,1,0]
# [0,0,0,0,0,0,1,0]
# [0,0,0,0,0,0,1,0]

class BitBoard:
    def __init__(self, size:int, stones:int) -> None:
        self.turn = True
        self.size = size
        self.stones = stones
        self.pits = size * 2
        self.row = self.pits + 2
        self.board = bitarray(
            stones * self.row * self.pits * [0]
        )

        for i in range(size):
            for j in range(stones):
                self.board[i * stones * self.row + j * self.row + i] = 1
                self.board[(self.pits + stones) * self.row + i * stones * self.row + j * self.row + size + 1 + i] = 1

        self.finalFilter = bitarray(
            size * [0] + [1] + size * [0] + [1]
        )

    def __str__(self) -> str:
        return f"{self.board.tolist()} {int(self.turn)}"
    
    def isFinal(self):
        pass

    def allLegalMoves(self, side: bool) -> [int]:
        pass
    

if __name__ == "__main__":
    board = BitBoard(3,3)
    print(board)
    print(len(board.board))