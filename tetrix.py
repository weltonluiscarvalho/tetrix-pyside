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

class TetrixPiece:

    def __init__(self):
        self._piece_shape = Piece.NoShape
        print(f"This is a TetrixPiece class!, the shape of this piece is {self.shape()}") 
    
    def shape(self):
        return self._piece_shape

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TetrixWindow()
    window.show()
    sys.exit(app.exec())
