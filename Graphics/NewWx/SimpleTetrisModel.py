import numpy as np

class Piece(object):
    pass

class GameModel(object):

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        # create empty game board
        self.board = np.zeros(num_rows * num_cols).reshape((num_rows, num_cols))

    def get_size(self):
        return self.num_rows, self.num_cols
