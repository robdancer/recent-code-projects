from tkinter import *
import math
import numpy
import copy
from collections import Counter

# Change SolveHelper level (0-8, 0 is off)
solveHelper = 0

'''
class GridSquare():
    def __init__(self, fixed=False, possibilities=[1, 2, 3, 4, 5, 6, 7, 8, 9]):
        self.fixed = fixed
        self.possibilities = possibilities

    def thin(self, others):
        if not fixed:
            conflictFix = [square.fixed for square in others if square.fixed]
            self.possibilities = [possibility for possibility in self.possibilities if possibility not in conflictFix]
            if len(self.possibilities) == 1:
                self.fixed = self.possibilities[0]
            elif len(self.possibilities) == 0:
                return False
'''

# Old method
#thin = lambda group : [square if len(square) == 1 else [possibility for possibility in square if possibility not in [other[0] for other in group if len(other) == 1]] for square in group]

'''
def printDemo(grid):
    for row in grid:
        for square in row:
            if len(square) == 1:
                print(square, end="")
            else:
                print(" ", end="")
        print()
    print()
'''

# New method
def thin(group):
    fixed = [square[0] for square in group if len(square) == 1]
    countList = []
    for fix in fixed:
        if fix in countList:
            # Multiple of the same number!
            return False
        else:
            countList.append(fix)
    newGroup = [square if len(square) == 1 else [possibility for possibility in square if possibility not in fixed] for square in group]
    if [] in newGroup:
        return False
    counts = Counter([i for j in newGroup for i in j])
    for squareNum in range(9):
        for possibility in newGroup[squareNum]:
            if counts[possibility] == 1:
                newGroup[squareNum] = [possibility]
    # Return False if there is a square with no possibilities
    return False if [] in newGroup else newGroup

def solveGrid(oldGrid):
    #printDemo(oldGrid)
    newGrid = copy.deepcopy(oldGrid)

    # Rows
    for i in range(9):
        newGroup = thin(newGrid[i])
        if newGroup:
            newGrid[i] = newGroup
        else:
            return False

    # Column
    for i in range(9):
        newGroup = thin([row[i] for row in newGrid])
        if newGroup:
            for row in range(9):
                newGrid[row][i] = newGroup[row]
        else:
            return False

    #'''
    # 3x3 Segments
    for row in (0, 3, 6):
        for column in (0, 3, 6):
            newGroup = thin(newGrid[row][column:column+3]+newGrid[row+1][column:column+3]+newGrid[row+2][column:column+3])
            if newGroup:
                newGrid[row][column:column+3] = newGroup[0:3]
                newGrid[row+1][column:column+3] = newGroup[3:6]
                newGrid[row+2][column:column+3] = newGroup[6:9]
            else:
                return False
    #'''

    if newGrid == oldGrid:
        # Stagnated
        # Check if solved
        for row in newGrid:
            for square in row:
                if len(square) > 1:
                    # Not finished - uh oh - time for 'alternative tactics'
                    # Comment next line to enable brute force
                    #return False
                    for i in range(2, 3):
                        for row in range(9):
                            for column in range(9):
                                if len(newGrid[row][column]) == i:
                                    prevSave = newGrid[row][column]
                                    for j in range(i):
                                        newGrid[row][column] = [prevSave[j]]
                                        result = solveGrid(newGrid)
                                        if result:
                                            return result
                                    newGrid[row][column] = prevSave
                    return False

        # Sudoku finished - exit

        return newGrid
    else:
        # Changes have occured - keep on going with current grid
        return solveGrid(newGrid)

def solveSudoku(gui):
    grid = [[[int(x)] if x else [1, 2, 3, 4, 5, 6, 7, 8, 9] for x in y] for y in gui.valueGrid]
    result = solveGrid(grid)
    if result:
        # Solution found
        gui.importGrid(result)
    else:
        # No solution found - invalid sudoku
        gui.showError("Invalid Sudoku - No Possible Solutions")

class GUIManager():

    def __init__(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=550, height=650)
        for i in range(1, 11):
            self.canvas.create_line(i*50, 50, i*50, 500)  
        for i in range(1, 11):
            self.canvas.create_line(50, i*50, 500, i*50)
        for i in range(4):
            self.canvas.create_line(i*150+50, 50, i*150+50, 500, width=3)
        for i in range(4):
            self.canvas.create_line(50, i*150+50, 500, i*150+50, width=3)
        self.canvas.create_rectangle(225, 550, 325, 600, fill='aqua')
        self.canvas.create_text(275, 575, text="Solve")
        self.root.bind("<Key>", self.key)
        self.root.bind("<Button-1>", self.click)
        self.canvas.pack(fill=BOTH, expand=1)
        self.selectRect = False
        self.valueGrid = numpy.zeros((9, 9), dtype=str)
        self.idGrid = numpy.zeros((9, 9), dtype=int)
        for y in range(9):
            for x in range(9):
                self.idGrid[y][x] = self.canvas.create_text(x*50+75, y*50+75, fill="black", text="")
        self.selectSquare(0, 0)
        self.root.mainloop()

    def nextSelect(self):
        if self.selectX < 8:
            self.selectSquare(self.selectX+1, self.selectY)
        elif self.selectY < 8:
            self.selectSquare(0, self.selectY+1)

    def changeGrid(self, x, y, value):
        self.valueGrid[y][x] = value
        self.canvas.itemconfig(self.idGrid[y][x], text=value)

    def importGrid(self, grid):
        for yNum, y in enumerate(grid):
            for xNum, x in enumerate(y):
                if len(x) == 1:
                    self.changeGrid(xNum, yNum, x[0])
                else:
                    self.changeGrid(xNum, yNum, '')
                    #self.changeGrid(xNum, yNum, x[0])

    def showError(self, errorMessage):
        # Display error on screen
        print(errorMessage)

    def click(self, event):
        if event.x >= 50 and event.x < 500 and event.y >= 50 and event.y < 500:
            self.selectSquare(math.floor((event.x-50)/50), math.floor((event.y-50)/50))
        elif event.x >= 225 and event.x < 325 and event.y >= 550 and event.y < 600:
            solveSudoku(self)

    def key(self, event):
        if event.char.isnumeric() and event.char != "0":
            self.changeGrid(self.selectX, self.selectY, event.char)
            self.nextSelect()
        elif event.char == "\t":
            self.nextSelect()
        elif event.char == " ":
            self.changeGrid(self.selectX, self.selectY, '')
            self.nextSelect()
        elif event.char == "w" and self.selectY > 0:
            self.selectSquare(self.selectX, self.selectY-1)
        elif event.char == "s" and self.selectY < 8:
            self.selectSquare(self.selectX, self.selectY+1)
        elif event.char == "a" and self.selectX > 0:
            self.selectSquare(self.selectX-1, self.selectY)
        elif event.char == "d" and self.selectX < 8:
            self.selectSquare(self.selectX+1, self.selectY)
        elif event.char == "m":
            print("".join(map(lambda x : x if x else '0', numpy.ravel(self.valueGrid))))
        elif event.char == "l":
            get = input()
            for y in range(9):
                for x in range(9):
                    if get[y*9+x] == '0':
                        self.changeGrid(x, y, '')
                    else:
                        self.changeGrid(x, y, get[y*9+x])

    def selectSquare(self, x, y):
        self.selectX = x
        self.selectY = y
        if self.selectRect:
            self.canvas.delete(self.selectRect)
        self.selectRect = self.canvas.create_rectangle(x*50+50, y*50+50, x*50+100, y*50+100, fill='aqua')

def main():

    GUIManager()

if __name__ == '__main__':
    main() 