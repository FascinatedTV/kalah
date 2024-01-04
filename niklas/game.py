from typing import List

class Board:
    def __init__(self, size : int, stoneCount : int = 3) -> None:
        self.turn = False
        self.size = size
        self.stoneCount = stoneCount
        self.allStones = 2 * size * stoneCount
        self.board = [0] + 2 * size * [stoneCount] + [0]
        # self.board = [0] + 2 * list(range(1,size+1)) + [0]
        # self.board = [10] + size * [1] + size * [1] + [12]

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Board): return False
        return self.board == __value.board
    
    def __str__(self) -> str:
        return f"{self.board} {int(self.turn)}"

    def isFinal(self) -> bool:
        return sum(self.board[1:self.size+1]) == 0 or sum(self.board[self.size+1:-1]) == 0
    
    def getSide(self, side : bool) -> List[int]:
        return self.board[int(side) * (self.size + 1) : (int(side) + 1) * (self.size + 1)]
    
    def getLegalMoves(self):
        pass

if __name__ == "__main__":
    board = Board(5)
    print(board)
    print(board.isFinal())
    print(board.getSide(False))
    print(board.getSide(True))