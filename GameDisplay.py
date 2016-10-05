__author__ = 'jmsbo'
from math import floor

import tkinter as tk

WIDTH = 1080
HEIGHT = 720
GAMEITERS = 500

class GameDisplay(tk.Frame):
    """
    The object which displays the game and takes user input. This displays the
    board state using colored cells, allows users to draw cells on the initial
    grid, lets the user start the game, and diplays how many living cells there
    are for each iteration.
    """
    def __init__(self, game, master=None):
        """
        Initializes the display and generates the blank grid
        :param master:
        :return:
        """
        super(GameDisplay, self).__init__(master)
        self.game = game
        self.bind("<Configure>", self.__on_resize)
        self.grid(sticky=tk.N+tk.E+tk.S+tk.W)
        self.liveCellCount = tk.StringVar()
        self.iterNumVar = tk.StringVar()
        self.__create_widgets()
        self.__paint_grid()
        self._root().mainloop()

    def __create_widgets(self):
        """
        This creates and binds the actual widgets for the GUI. This should
        only be called at the initialization of the window..
        :return: None
        """
        # Make stuff expandable
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Create the canvas widget and draw a blank grid on it
        self.gridCanvas = tk.Canvas(self, bg="#d7941d", closeenough=0.0)
        self.gridCanvas.grid(row=0, column=0, columnspan=5, sticky=tk.N+tk.E+tk.S+tk.W)
        self.gridCanvas.bind("<ButtonRelease-1>", self.__handle_click)
        self.__create_canvas_grid()

        # Create the new game button widget and tie to new game command
        self.newGameButton = tk.Button(self, text="New Game", command=self.new_game)
        self.newGameButton.grid(row=1, column=0, sticky=tk.N+tk.E+tk.S+tk.W)

        # Create the start button widget and tie it to the start command
        self.startButton = tk.Button(self, text="Start Game", command=self.start_game)
        self.startButton.grid(row=1, column=1, sticky=tk.N+tk.E+tk.S+tk.W)

        # Create the step button widget and tie it to the step game command
        self.stepButton = tk.Button(self, text="Step Game", command=self.step_game)
        self.stepButton.grid(row=1, column=2, sticky=tk.N+tk.E+tk.S+tk.W)

        # Create the label widget which will indicate how many live cells there are
        self.liveCellCountLabel = tk.Label(self, textvariable=self.liveCellCount)
        self.liveCellCountLabel.grid(row=1, column=3, sticky=tk.N+tk.E+tk.S+tk.W)

        # Create the label widget which indicates the iteration number
        self.iterNumVar.set("Iteration #: {iNum}".format(iNum=self.game.get_iter_num()))
        self.iterNumLabel = tk.Label(self, textvariable=self.iterNumVar)
        self.iterNumLabel.grid(row=1, column=4, sticky=tk.N+tk.E+tk.S+tk.W)

    def __create_canvas_grid(self):
        """
        Create an initial grid of rectangles to display the board state.
        This is called every time the window is resized, and generates a
        new list of rectangles. The reason I use this is because it is faster
        to swap rectangle colors and redraw than it is to redraw all the
        rectangles in new colors.
        :return: None
        """
        self._root().update()
        windowHgt, windowWdt = (self.gridCanvas.winfo_height(), self.gridCanvas.winfo_width())
        rectHgt = self.winfo_height() / self.game.get_size()
        rectWdt = self.winfo_width() / self.game.get_size()
        self.canvasGrid=[]
        for y in range(self.game.get_size()):
            gridRow = []
            for x in range(self.game.get_size()):
                x0, y0 = (x * rectWdt, y * rectHgt)
                x1, y1 = ((x+1) * rectWdt - 1, (y+1) * rectHgt - 1)
                rectTag = "({x},{y})".format(x=x, y=y)
                gridRow.append(self.gridCanvas.create_rectangle(x0, y0,
                                                                x1, y1,
                                                                width=0,
                                                                tags=rectTag))
            self.canvasGrid.append(gridRow)
        self.gridCanvas.update_idletasks()

    def __on_resize(self, event):
        """
        This makes sure that the canvas and grid scale with the window
        as the user resizes them.

        :param event: The resizing event, not used here.
        :return: None, but changes canvas
        """
        try:
            self.gridCanvas.delete("all")
            self.__create_canvas_grid()
            self.__paint_grid()
        except AttributeError as e:
            pass

    def __paint_grid(self, reset=False):
        """
        Paints the grid by checking which cells changed and painting them the
        appropriate color. This is significantly faster that reading through
        the whole grid on large grids. This method also updates the labels.
        :return: None, but changes the canvas
        """
        if reset:
            for row in self.canvasGrid:
                for rect in row:
                    self.gridCanvas.itemconfigure(rect,
                                                  fill="#d7941d")
        for cell in self.game.get_changed_cells():
            x, y = cell
            if self.game.get_board()[y, x] == 1:
                self.gridCanvas.itemconfigure(self.canvasGrid[y][x],
                                              fill="#822433")
            elif self.game.get_board()[y, x] == 0:
                self.gridCanvas.itemconfigure(self.canvasGrid[y][x],
                                              fill="#d7941d")
        self.gridCanvas.update_idletasks()
        self.__update_labels()

    def __update_labels(self):
        """
        Updates the two labels (cell count and iteration number).

        :return: None, but changes the labels
        """
        self.liveCellCount.set("Live Cells: {cells}".format(cells=self.game.get_live_count()))
        self.liveCellCountLabel.update_idletasks()
        self.iterNumVar.set("Iteration #: {iNum}".format(iNum=self.game.get_iter_num()))
        self.iterNumLabel.update_idletasks()


    def __handle_click(self, event):
        """
        Handles the user's click on the canvas. Basically, if the game hasn't
        started yet (self.game.get_iter_num() == 0), let the user paint and
        erase cells. Once the game starts, make sre the user can't change
        anything.

        :param event: Mouse button 1 released, used for coordinates.
        :return: None, but changes canvas and game state
        """
        if self.game.get_iter_num() > 0:
            return
        clickX, clickY = (event.x, event.y)
        cellID = self.gridCanvas.find_closest(clickX, clickY, halo=0)[0]
        cellTag = self.gridCanvas.gettags(cellID)[0]
        cell = [int(pos) for pos in cellTag.strip('()').split(',')]
        x, y = cell
        print(x, y, clickX, clickY)
        self.game.flip_cell_at(x, y)
        self.__paint_grid()


    def step_game(self):
        """
        Perform one iteration of the game, including painting the grid
        again.

        :return: None, but changes canvas and game state
        """
        self.game.iterate_game()
        self.__paint_grid()

    def start_game(self):
        """
        Start a loop which iterates the game as many times as GAMEITERS
        specifies, or until there are no changing cells.

        :return: None, but changes canvas and game state
        """
        for i in range(GAMEITERS):
            if self.game.get_changed_cells() == []:
                break
            self.game.iterate_game()
            self.__paint_grid()

    def new_game(self):
        """
        Reset the board so that the game can be played again.

        :return: None, but changes canvas and game state
        """
        self.game.new_game()
        self.__paint_grid(reset=True)




if __name__ == '__main__':
    import AutomataGame as AG
    tBoard = AG.Game(25, test=False)
    root = tk.Tk()
    gameDisplay = GameDisplay(game=tBoard, master=root)
