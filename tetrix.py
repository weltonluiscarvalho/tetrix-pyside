from enum import IntEnum
import sys
import random
from PySide6.QtCore import QBasicTimer, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QLCDNumber, QLabel, QPushButton

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

        next_piece_label = QLabel()
        next_piece_label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        next_piece_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.board.set_next_piece_label(next_piece_label)

        score_lcd = QLCDNumber(5)
        score_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        level_lcd = QLCDNumber(2)
        level_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        lines_lcd = QLCDNumber(5)
        lines_lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        start_button = QPushButton("&Start")
        start_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        quit_button = QPushButton("&Quit")
        quit_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        pause_button = QPushButton("&Pause")
        pause_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        start_button.clicked.connect(self.board.start)
        pause_button.clicked.connect(self.board.pause)
        quit_button.clicked.connect(qApp.quit)
        self.board.score_changed.connect(score_lcd.display)
        self.board.level_changed.connect(level_lcd.display)
        self.board.lines_removed_changed.connect(lines_lcd.display)

        layout = QGridLayout(self)
        layout.addWidget(self.create_label("NEXT"), 0, 0)
        layout.addWidget(next_piece_label, 1, 0)
        layout.addWidget(self.create_label("LEVEL"), 2, 0)
        layout.addWidget(level_lcd, 3, 0)
        layout.addWidget(start_button, 4, 0)
        layout.addWidget(self.board, 0, 1, 6, 1)
        layout.addWidget(self.create_label("SCORE"), 0, 2)
        layout.addWidget(score_lcd, 1, 2)
        layout.addWidget(self.create_label("LINES REMOVED"), 2, 2)
        layout.addWidget(lines_lcd, 3, 2)
        layout.addWidget(quit_button, 4, 2)
        layout.addWidget(pause_button, 5, 2)

        self.setWindowTitle("Tetrix")
        self.resize(550, 370)

    def create_label(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        return lbl


class TetrixBoard(QFrame):
    board_width = 10
    board_height = 22

    score_changed = Signal(int)
    level_changed = Signal(int)
    lines_removed_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QBasicTimer()
        self.nextPieceLabel = None
        self._is_waiting_after_line = False
        self._cur_piece = TetrixPiece()
        self._next_piece = TetrixPiece()
        self._cur_x = 0 
        self._cur_y = 0
        self._num_lines_removed = 0
        self._num_pieces_dropped = 0
        self.score = 0
        self.level = 0
        self.board = None 

        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._is_started = False
        self._is_paused = False
        self.clear_board()

        self._next_piece.set_random_shape()

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

    def set_next_piece_label(self, label):
        self.nextPieceLabel = label

    def sizeHint(self):
        return QSize(TetrixBoard.board_width * 15 + self.frameWidth() * 2, TetrixBoard.board_height * 15 + self.frameWidth() * 2)

    def minimum_size_hint(self):
        return QSize(TetrixBoard.board_width * 5 + self.frameWidth() * 2, TetrixBoard.board_height * 5 + self.frameWidth() * 2)

    def clear_board(self):
        self.board = [Piece.NoShape for _ in range(TetrixBoard.board_height * TetrixBoard.board_width)]

    @Slot()
    def start(self):
        if self._is_paused:
            return

        self._is_started = True
        self._is_waiting_after_line = False
        self._num_lines_removed = 0 
        self._num_pieces_dropped = 0 
        self.score = 0 
        self.level = 1 
        self.clear_board()

        self.lines_removed_changed.emit(self._num_lines_removed)
        self.score_changed.emit(self.score)
        self.level_changed.emit(self.level)

        self.new_piece()
        self.timer.start(self.timeout_time(), self)
    
    @Slot()
    def pause(self):
        if not self._is_started:
            return

        self._is_paused = not self._is_paused
        if self._is_paused:
            self.timer.stop()
        else:
            self.timer.start(self.timeout_time(), self)

        self.update()

    def keyPressEvent(self, event):
        if not self._is_started or self._is_paused or self._cur_piece.shape() == Piece.NoShape:
            super(TetrixBoard, self).keyPressEvent(event)
            return

        key = event.key()
        if key == Qt.Key.Key_Left:
            self.try_move(self._cur_piece, self._cur_x - 1, self._cur_y)
        elif key == Qt.Key.Key_Right:
            self.try_move(self._cur_piece, self._cur_x + 1, self._cur_y)
        elif key == Qt.Key.Key_Down:
            self.try_move(self._cur_piece.rotated_right(), self._cur_x, self._cur_y)
        elif key == Qt.Key.Key_Up:
            self.try_move(self._cur_piece.rotated_left(), self._cur_x, self._cur_y)
        elif key == Qt.Key.Key_Space:
            self.drop_down()
        elif key == Qt.Key.Key_D:
            self.one_line_down()
        else:
            super(TetrixBoard, self).keyPressEvent(event)

    def paintEvent(self, event):
        super(TetrixBoard, self).paintEvent(event)

        with QPainter(self) as painter:
            rect = self.contentsRect()

            if self._is_paused:
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Pause")
                return

            board_top = rect.bottom() - TetrixBoard.board_height * self.square_height()

            for i in range(TetrixBoard.board_height):
                for j in range(TetrixBoard.board_width):
                    shape = self.shape_at(j, TetrixBoard.board_height - i - 1)
                    if shape != Piece.NoShape:
                        self.draw_square(painter,
                                         rect.left() + j * self.square_width(),
                                         board_top + i * self.square_height(), shape)

            if self._cur_piece.shape() != Piece.NoShape:
                for i in range(4):
                    x = self._cur_x + self._cur_piece.x(i)
                    y = self._cur_y - self._cur_piece.y(i)
                    self.draw_square(painter, rect.left() + x * self.square_width(),
                                     board_top
                                     + (TetrixBoard.board_height - y - 1) * self.square_height(),
                                     self._cur_piece.shape())

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self._is_waiting_after_line:
                self._is_waiting_after_line = False
                self.new_piece()
                self.timer.start(self.timeout_time(), self)
            else:
                self.one_line_down()
        else:
            super(TetrixBoard, self).timerEvent(event)

    def drop_down(self):
        drop_height = 0
        new_y = self._cur_y
        while new_y > 0:
            if not self.try_move(self._cur_piece, self._cur_x, new_y - 1):
                break
            new_y -= 1 
            drop_height += 1 

        self.piece_dropped(drop_height)

    def one_line_down(self):
        if not self.try_move(self._cur_piece, self._cur_x, self._cur_y - 1):
            self.piece_dropped(0)

    def piece_dropped(self, drop_height):
        for i in range(4):
            x = self._cur_x + self._cur_piece.x(i)
            y = self._cur_y - self._cur_piece.y(i)
            self.set_shape_at(x, y, self._cur_piece.shape())

        self._num_pieces_dropped += 1 
        if self._num_pieces_dropped % 25 == 0:
            self.level += 1 
            self.timer.start(self.timeout_time(), self)
            self.level_changed.emit(self.level)

        self.score += drop_height + 7
        self.score_changed.emit(self.score)
        self.remove_full_lines()

        if not self._is_waiting_after_line:
            self.new_piece()
            
    def remove_full_lines(self):
        num_full_lines = 0 

        for i in range(TetrixBoard.board_height - 1, -1, -1):
            line_is_full = True

            for j in range(TetrixBoard.board_width):
                if self.shape_at(j, i) == Piece.NoShape:
                    line_is_full = False
                    break

            if line_is_full:
                num_full_lines += 1 
                for k in range(i, TetrixBoard.board_height - 1):
                    for j in range(TetrixBoard.board_width):
                        self.set_shape_at(j, k, self.shape_at(j, k + 1))

                for j in range(TetrixBoard.board_width):
                    self.set_shape_at(j, TetrixBoard.board_height - 1, Piece.NoShape)

        if num_full_lines > 0:
            self._num_lines_removed += num_full_lines
            self.score += 10 * num_full_lines
            self.lines_removed_changed.emit(self._num_lines_removed)
            self.score_changed.emit(self.score)

            self.timer.start(500, self)
            self._is_waiting_after_line = True
            self._cur_piece.set_shape(Piece.NoShape)
            self.update()

    def new_piece(self):
        self._cur_piece = self._next_piece
        self._next_piece.set_random_shape()
        self.show_next_piece()
        self._cur_x = TetrixBoard.board_width // 2 + 1 
        self._cur_y = TetrixBoard.board_height - 1 + self._cur_piece.min_y()

        if not self.try_move(self._cur_piece, self._cur_x, self._cur_y):
            self._cur_piece.set_shape(Piece.NoShape)
            self.timer.stop()
            self._is_started = False

    def show_next_piece(self):
        if self.nextPieceLabel is not None:
            return

        dx = self._next_piece.max_x() - self._next_piece.min_x() + 1
        dy = self._next_piece.max_y() - self._next_piece.min_y() + 1

        pixmap = QPixmap(dx * self.square_width(), dy * self.square_height())
        with QPainter(pixmap) as painter:
            painter.fillRect(pixmap.rect(), self.nextPieceLabel.palette().background())

        for i in range(4):
            x = self._next_piece.x(i) - self._next_piece.min_x()
            y = self._next_piece.y(i) - self._next_piece.min_y()
            self.draw_square(painter, x * self.square_width(), y * self.square_height(), self._next_piece.shape())

        self.nextPieceLabel.setPixmap(pixmap)

    def try_move(self, new_piece, new_x, new_y):
        for i in range(4):
            x = new_x + new_piece.x(i)
            y = new_y + new_piece.y(i)
            if x < 0 or x >= TetrixBoard.board_width or y < 0 or y >= TetrixBoard.board_height:
                return False
            if self.shape_at(x, y) != Piece.NoShape:
                return False

        self._cur_piece = new_piece
        self._cur_x = new_x
        self._cur_y = new_y
        self.update()
        return True

    def draw_square(self, painter, x, y, shape):
        color_table = [0x000000, 0xcc6666, 0x66cc66, 0x6666cc, 0xcccc66, 0xcc66cc, 0x66cccc, 0xdaaa00]

        color = QColor(color_table[shape])
        painter.fillRect(x + 1, y + 1, self.square_width() - 2, self.square_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height() - 1, x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1, y + self.square_height() - 1, x + self.square_width() - 1, y + 1)

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

        self.set_shape(Piece.NoShape)
    
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
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m

    def max_y(self):
        m = self.coords[0][1]
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
    random.seed(None)
    sys.exit(app.exec())
