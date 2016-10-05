__author__ = 'jmsbo'
import numpy as np

from random import randint

# Read up on Conway' Game of Life at
#   https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
# Basic rules:
#   1) A cell is spawned if it was dead but has 3 live neighbors
#   2) A live cell dies if it has fewer than two live neighbors
#   3) A live cell lives to the next generation if it has two or
#       three live neighbors
#   4) A live cell dies if it has more than three live neighbors


class Game(object):
    """
    An object which holds the game state and has some methods for manipulating
    it. This includes keeping track of live cells on the board, spawning new
    cells, kill dead cells, and iterating the game.
    """
    def __init__(self, size, test=False):
        """
        Initialize the game by creating a blank board with no live cells.
        :param size: The size of the board, which is a square
        :return: None
        """
        self.size = size
        self.board = np.zeros((size, size), dtype=np.int)
        self.liveCount = 0
        self.changedCells = []
        self.iterNum = 0
        if test:
            for x in range(size):
                for y in range(size):
                    cellVal = randint(0,1)
                    self.board[y, x] = cellVal
                    self.liveCount += cellVal
                    if cellVal == 1: self.changedCells.append((x, y))

    def new_game(self):
        """
        Reset the game by zeroing out the board and live cell counter.
        :return: None
        """
        self.board = np.zeros((self.size, self.size))
        self.liveCount = 0
        self.iterNum = 0

    def _check_for_life(self, posX, posY):
        """
        Sum the neighboring cells to get a count of how many live neighbors
        the target cell has. then apply the rules of the game, returning a one
        if the cell should be alive and a zero if not. It also returns a boolean
        indicating whether there was a change or not
        :param posX: Row of the target cell
        :param posY: Column of the target cell
        :return: int 1 or 0 and a bool
        """
        leftBound = ((posX - 1) + self.size) % self.size
        rightBound = (posX + 1) % self.size
        topBound = ((posY - 1) + self.size) % self.size
        botBound = (posY + 1) % self.size
        nborSum = self.board[topBound, leftBound] +\
                  self.board[topBound, posX] +\
                  self.board[topBound, rightBound] +\
                  self.board[posY, leftBound] +\
                  self.board[posY, rightBound] +\
                  self.board[botBound, leftBound] +\
                  self.board[botBound, posX] +\
                  self.board[botBound, rightBound]
        if self.board[posY, posX] == 0:
            if nborSum == 3: return 1, True
            else: return 0, False
        if self.board[posY, posX] == 1:
            if 1 < nborSum < 4: return 1, False
            else: return 0, True

    def iterate_game(self):
        """
        Runs a single iteration of the game by creating a new board, checking
        each cell in the old board for life, and the changing the appropriate
        cell on the new board. It also updates the live cell counter.
        :return: None, but changes self.board
        """
        nextBoardState = np.array(self.board)
        nextChangedCells = []
        # Now we loop over all the cells that changed state, and check them
        # and the cells directly adjacent to them to see what changes, if any
        # result from the previous change. This is just an attempt at optimizing
        # the code.
        for cell in self.changedCells:
            x, y = cell
            if (x, y) in nextChangedCells:
                continue
            leftBound = ((x - 1) + self.size) % self.size
            rightBound = (x + 1) % self.size
            topBound = ((y - 1) + self.size) % self.size
            botBound = (y + 1) % self.size
            # We need to use a custom list because range can't handle the
            # situation in which the bounds wrap around the grid. E.g.
            # leftBound = 3, x = 4, and rightBound = 0
            for i in [leftBound, x, rightBound]:
                for j in [topBound, y, botBound]:
                    if (i, j) in nextChangedCells:
                        continue
                    newState, change = self._check_for_life(i, j)
                    if change:
                        nextBoardState[j, i] = newState
                        nextChangedCells.append((i, j))
                        if newState == 0:
                            self.liveCount -= 1
                        elif newState == 1:
                            self.liveCount += 1
        self.board = nextBoardState
        self.changedCells = nextChangedCells
        self.iterNum += 1

    def flip_cell_at(self, posX, posY):
        """
        Flip the state of the cell at the target and updates the live cell count
        :param posX: Row of the target cell
        :param posY: Column of the target cell
        :return: None, but changes self.board
        """
        if self.board[posY, posX] == 1:
            self.board[posY, posX] = 0
            self.liveCount -= 1
        elif self.board[posY, posX] == 0:
            self.board[posY, posX] = 1
            self.liveCount += 1
        self.changedCells.append((posX, posY))

    def get_board(self):
        return self.board

    def get_live_count(self):
        return self.liveCount

    def get_size(self):
        return self.size

    def get_changed_cells(self):
        return self.changedCells

    def get_iter_num(self):
        return self.iterNum

    def __repr__(self):
        retStr = "Cells: {cells} \n {board}".format(cells=self.liveCount,
                                                    board=str(self.board)
                                                    )
        return retStr

if __name__ == '__main__':
    testBoard = Game(10, test=True)
    print(testBoard)
    testBoard.iterate_game()
    print(testBoard)
