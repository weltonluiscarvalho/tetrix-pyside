from enum import IntEnum
import sys
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
        self._piece = TetrixPiece()
        self._piece.set_x(3, 45)
        self._piece.set_y(3, 46)
        print(f" as posicoes do bloco 3 da peca são {self._piece.x(3)}, e {self._piece.y(3)}")

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
        print(f"This is a TetrixPiece class!, the shape of this piece is {self.shape()}") 
    
    def shape(self):
        return self._piece_shape


    def set_shape(self, shape):
        table = TetrixPiece.coords_table[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self._piece_shape = shape

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TetrixWindow()
    window.show()
    sys.exit(app.exec())
