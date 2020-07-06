# Link Cuatro
# Connect n
# By Robert Dancer
# robertdancer@ymail.com

from tkinter import *
import random
from PIL import Image, ImageTk, ImageOps, ImageColor

custom_board = True
custom_players = True

class GUIManager():

    def __init__(self, params):
        self.params = params
        self.root = Tk()
        self.canvas = Canvas(self.root, width=params["width"]*50+100, height=params["height"]*50+150)
        self.setupBindings()
        self.setupGUI()
        self.setupArrows()
        self.canvas.pack(fill=BOTH, expand=1)        
        self.setupGame()
        self.root.mainloop()

    def setupArrows(self):
        downArrow = Image.open("down_arrow_v2.png").convert("L")
        self.finishedArrows = []
        for player in self.params["players"]:
            colour = ImageColor.getrgb(self.params["colours"][player])
            colouredArrow = ImageOps.colorize(downArrow, colour, (0, 0, 0))
            self.finishedArrows.append(ImageTk.PhotoImage(colouredArrow))

    def setupBindings(self):
        self.root.bind("<Left>", self.arrowLeft)
        self.root.bind("<Right>", self.arrowRight)
        self.root.bind("<Key>", self.keyPress)

    def setupGUI(self):
        grid = []
        for i in range(1, self.params["width"]+1):
            grid.append(self.canvas.create_line(i*50, 100, i*50, self.params["height"]*50+100))
        for i in range(2, self.params["height"]+2):
            grid.append(self.canvas.create_line(50, i*50, self.params["width"]*50+50, i*50))
        grid.append(self.canvas.create_line(50, 100, 50, self.params["height"]*50+100, width=3))
        grid.append(self.canvas.create_line(50, 100, self.params["width"]*50+50, 100, width=3))
        grid.append(self.canvas.create_line(self.params["width"]*50+50, 100, self.params["width"]*50+50, self.params["height"]*50+100, width=3))
        grid.append(self.canvas.create_line(50, self.params["height"]*50+100, self.params["width"]*50+50, self.params["height"]*50+100, width=3))
        self.grid = grid

        self.drawnObjects = []

        self.gameOverText = self.canvas.create_text(self.params["width"]*25+50,10,fill="red",font="Times 20 bold",text="", anchor=N, state="hidden")

    def setupGame(self):
        self.currentPlayer = 0
        self.placeLoc = 0
        self.tokenGrid = []
        for i in range(self.params["width"]):
            self.tokenGrid.append([])
        self.gameActive = True
        self.enableArrow(self.currentPlayer)

    def getToken(self, x, y):
        if self.tokenGrid[x]:
            if len(self.tokenGrid[x]) >= y + 1:
                return self.tokenGrid[x][y]
            else:
                return -1
        else:
            return -1

    def checkToken(self, x, y):
        currentToken = self.getToken(x, y)
        # directions needed:
        # left
        # left-up
        # right-up
        # up

        # left
        if x + 1 >= self.params["target"]:
            # just left
            fail = False
            for i in range(x+1-self.params["target"], x):
                if self.getToken(i, y) != currentToken:
                    fail = True
                    break
            if not fail:
                return True, currentToken, x, y, x+1-self.params["target"], y

            # left-up
            fail = False
            for i in range(1, self.params["target"]):
                if self.getToken(x-i, y+i) != currentToken:
                    fail = True
                    break
            if not fail:
                return True, currentToken, x, y, x+1-self.params["target"], y+self.params["target"]-1

        # right-up
        if x + self.params["target"] <= self.params["width"]:
            fail = False
            for i in range(1, self.params["target"]):
                if self.getToken(x+i, y+i) != currentToken:
                    fail = True
                    break
            if not fail:
                return True, currentToken, x, y, x+self.params["target"]-1, y+self.params["target"]-1

        # up
        if len(self.tokenGrid[x]) >= y + self.params["target"]:
            fail = False
            for i in self.tokenGrid[x][y:y+self.params["target"]]:
                if i != currentToken:
                    fail = True
                    break
            if not fail:
                return True, currentToken, x, y, x, y+self.params["target"]-1

        return False, -1, 0, 0, 0, 0

    def checkBoard(self):
        success = False
        for columnNo in range(self.params["width"]):
            if self.tokenGrid[columnNo]:
                for rowNo in range(len(self.tokenGrid[columnNo])):
                    success, winner, x1, y1, x2, y2 = self.checkToken(columnNo, rowNo)
                    if success:
                        break
            if success:
                break
        if success:
            self.gameWon(winner, x1, y1, x2, y2)

        fail = False
        for i in range(self.params["width"]):
            if len(self.tokenGrid[i]) < self.params["height"]:
                fail = True
                break
        if not fail:
            self.gameDraw()

    def gameWon(self, player, x1, y1, x2, y2):
        y1 = self.params["height"]-y1
        y2 = self.params["height"]-y2
        self.gameActive = False
        self.canvas.itemconfigure(self.gameOverText, text=f"{self.params['playerNames'][player]} wins! 'r' to restart, 'q' to quit.", state="normal")
        self.drawnObjects.append(self.canvas.create_line(x1*50+75, y1*50+75, x2*50+75, y2*50+75, width=10))

    def gameDraw(self):
        self.gameActive = False
        self.canvas.itemconfigure(self.gameOverText, text="Draw! 'r' to restart, 'q' to quit.", state="normal")

    def goNextPlayer(self):
        self.disableArrow()
        if self.currentPlayer + 1 >= len(self.params["players"]):
            self.currentPlayer = 0
        else:
            self.currentPlayer += 1
        self.enableArrow(self.currentPlayer)

    def playerPlace(self):
        if len(self.tokenGrid[self.placeLoc]) >= self.params["height"]:
            return
        else:
            squaresDown = self.params["height"]-len(self.tokenGrid[self.placeLoc])
            self.placeToken(self.currentPlayer, self.placeLoc*50+50, squaresDown*50+50)
            self.tokenGrid[self.placeLoc].append(self.currentPlayer)
            self.checkBoard()
            if self.gameActive:
                self.goNextPlayer()

    def placeToken(self, player, x, y):
        fillColour = self.params["colours"][player]
        self.drawnObjects.append(self.canvas.create_rectangle(x, y, x+50, y+50, fill=fillColour))

    def disableArrow(self):
        self.canvas.delete(self.arrow)

    def enableArrow(self, player):
        self.placeLoc = 0
        self.arrow = self.canvas.create_image(50, 50, image=self.finishedArrows[player], anchor=NW, state="normal")

    def updateArrow(self):
        self.canvas.coords(self.arrow, self.placeLoc*50+50, 50)

    def resetGame(self):
        self.canvas.delete(*self.drawnObjects)
        self.canvas.itemconfigure(self.gameOverText, state="hidden")
        self.disableArrow()
        self.setupGame() 

    def keyPress(self, event):
        if event.char == " " and self.gameActive:
            self.playerPlace()
        elif event.char == "r":
            self.resetGame()
        elif event.char == "q":
            self.root.destroy()  

    def arrowLeft(self, event):
        if self.placeLoc > 0 and self.gameActive:
            self.placeLoc -= 1
            self.updateArrow()

    def arrowRight(self, event):
        if self.placeLoc + 1 < self.params["width"] and self.gameActive:
            self.placeLoc += 1
            self.updateArrow()

def getParams():
    params = {}
    if custom_board:
        params["width"] = int(input("Width: "))
        params["height"] = int(input("Height: "))
        params["target"] = int(input("Target to win: "))
    else:
        params["width"] = 7
        params["height"] = 6
        params["target"] = 4
    if custom_players:
        playerCount = int(input("Players: "))
        params["players"] = list(range(playerCount))
        params["playerNames"] = []
        for i in params["players"]:
            params["playerNames"].append(input("Player " + str(i+1) + ": "))
        params["colours"] = {}
        for playerNo in params["players"]:
            params["colours"][playerNo] = input(params["playerNames"][playerNo]+"'s colour: ")
    else:
        params["players"] = [0, 1]
        params["playerNames"] = ["Player 1", "Player 2"]
        params["colours"] = {0: "blue", 1: "red"}
    return params
        
def main():

    params = getParams()

    GUIManager(params)

if __name__ == '__main__':
    main()