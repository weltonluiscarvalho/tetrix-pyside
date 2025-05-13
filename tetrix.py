from enum import IntEnum
import sys
import random
from PySide6.QtWidgets import QApplication, QFrame

class Piece(IntEnum):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 6


class TetrixWindow(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = TetrixBoard()


class TetrixBoard(QFrame):
    board_width = 10
    board_height = 22

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cur_piece = TetrixPiece()
        self._next_piece = TetrixPiece()
        self.level = 0

    def shape_at(self, x, y):
        return self.board[(y * TetrixBoard.board_width) + x]

    def set_shape_at(self, x, y, shape):
        self.board[(y * TetrixBoard.board_width) + x] = shape

    def timeout_time(self):
        return 1000 / (1 + self.level)

    def square_width(self):
        return self.contentsRect().width() / TetrixBoard.board_width

    def square_height(self):
        return self.contentsRect().height() / TetrixBoard.board_height

    def clear_board(self):
        self.board = [Piece.NoShape for _ in range(TetrixBoard.board_height * TetrixBoard.board_width)]


class TetrixPiece:

    '''
    this coords will represent a piece in a 5x5 matrix
    example:
            __________
          2|          |
          1|     #    |
          0|     #    |
         -1|   # #    |
         -2|__________|
           -2 -1 0 1 2 
    '''
    coords_table = (
        # NoShape
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        # ZShape
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        # SShape
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        # LineShape
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        # TShape
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        # SquareShape
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        # LShape
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        # MirroredLShape
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):
        self.coords = [[0, 0] for _ in range(4)]
        self._piece_shape = Piece.NoShape
    
    def shape(self):
        return self._piece_shape


    def set_shape(self, shape):
        table = TetrixPiece.coords_table[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self._piece_shape = shape

    def set_random_shape(self):
        self.set_shape(random.randint(1, 7))

    # this method will return de x coordinate of a constitute block of the piece, the index is de constitute block position at the piece
    def x(self, index):
        return self.coords[index][0]


    # this method will return de y coordinate of a constitute block of the piece, the index is de constitute block position at the piece
    def y(self, index):
        return self.coords[index][1]


    def set_x(self, index, x):
        self.coords[index][0] = x


    def set_y(self, index, y):
        self.coords[index][1] = y


    def min_x(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m

    def max_x(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m

    def min_y(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m

    def max_y(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][1])
        return m

    def rotated_left(self):
        if self._piece_shape == Piece.SquareShape:
            return self

        result = TetrixPiece()
        result._piece_shape = self._piece_shape
        for i in range(4):
            result.set_x(i, self.y(i))
            result.set_y(i, -self.x(i))

        return result

    def rotated_right(self):
        if self._piece_shape == Piece.SquareShape:
            return self

        result = TetrixPiece()
        result._piece_shape = self._piece_shape
        for i in range(4):
            result.set_x(i, -self.y(i))
            result.set_y(i, self.x(i))

        return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TetrixWindow()
    window.show()
    sys.exit(app.exec())
