from tkinter import *
import random
from PIL import Image, ImageTk

ask_for_params = True

class GUIManager():

    def __init__(self, params):
        self.params = params
        self.root = Tk()
        self.canvas = Canvas(self.root, width=params["width"]*50+100, height=params["height"]*50+100)
        self.rawAppleImg = Image.open("apple.png")
        self.appleImg = ImageTk.PhotoImage(self.rawAppleImg)
        self.root.bind("<Left>", self.arrowLeft)
        self.root.bind("<Right>", self.arrowRight)
        self.root.bind("<Up>", self.arrowUp)
        self.root.bind("<Down>", self.arrowDown)
        self.root.bind("<Key>", self.keyPress)
        self.setupGUI()
        self.canvas.pack(fill=BOTH, expand=1)        
        self.setupGame()
        self.root.after(params["speed"], self.gameLoop)        
        self.root.mainloop()

    def setupGUI(self):
        grid = []
        for i in range(1, self.params["width"]+1):
            grid.append(self.canvas.create_line(i*50, 50, i*50, self.params["height"]*50+50))
        for i in range(1, self.params["height"]+1):
            grid.append(self.canvas.create_line(50, i*50, self.params["width"]*50+50, i*50))
        grid.append(self.canvas.create_line(50, 50, 50, self.params["height"]*50+50, width=3))
        grid.append(self.canvas.create_line(50, 50, self.params["width"]*50+50, 50, width=3))
        grid.append(self.canvas.create_line(self.params["width"]*50+50, 50, self.params["width"]*50+50, self.params["height"]*50+50, width=3))
        grid.append(self.canvas.create_line(50, self.params["height"]*50+50, self.params["width"]*50+50, self.params["height"]*50+50, width=3))
        self.grid = grid
        
        snakeSquares = {}
        for x in range(self.params["width"]):
            for y in range(self.params["height"]):
                snakeSquares[(x, y)] = self.canvas.create_rectangle(x*50+50, y*50+50, x*50+100, y*50+100, fill=self.params["colour"], state="hidden")
        self.snakeSquares = snakeSquares
        self.activeSnake = []

        self.appleObj = self.canvas.create_image(0, 0, image=self.appleImg, anchor=NW)

        self.gameOverText = self.canvas.create_text(self.params["width"]*25+50,10,fill="red",font="Times 20 bold",text="", anchor=N, state="hidden")

    def setupGame(self):
        self.snakeCoords = [(self.params["width"] // 2, self.params["height"] // 2)]
        self.snakeDir = (1, 0)
        self.elongate = False
        self.gameActive = True
        self.placeApple()
        self.drawGame()

    def placeApple(self):
        possible_locations = [(w, h) for w in range(self.params["width"]) for h in range(self.params["height"])]
        possible_locations = [location for location in possible_locations if location not in self.snakeCoords]
        self.appleCoords = random.choice(possible_locations)

    def drawGame(self):
        self.canvas.coords(self.appleObj, *map(lambda coord: coord*50+50, self.appleCoords))
        activeSnakeNew = []
        for square in self.activeSnake:
            if square in self.snakeCoords:
                activeSnakeNew.append(square)
            else:
                self.canvas.itemconfigure(self.snakeSquares[square], state="hidden")
        for square in self.snakeCoords:
            if not square in activeSnakeNew:
                self.canvas.itemconfigure(self.snakeSquares[square], state="normal")
                activeSnakeNew.append(square)
        
        self.activeSnake = activeSnakeNew

        for gridObj in self.grid:
            self.canvas.tag_raise(gridObj)

    def gameLoop(self):
        self.moveSnake()
        if self.gameActive:
            self.drawGame()
            self.root.after(self.params["speed"], self.gameLoop)

    def keyPress(self, event):
        if event.char == "r" and self.gameActive == False:
            self.canvas.itemconfigure(self.gameOverText, state="hidden")
            self.snakeCoords = []
            self.drawGame()
            self.setupGame()
            self.root.after(self.params["speed"], self.gameLoop)
        elif event.char == "q":
            self.root.destroy()

    def gameOver(self):
        self.gameActive = False
        self.canvas.itemconfigure(self.gameOverText, text=f"Game over. Score: {len(self.snakeCoords)-1}. 'r' to restart, 'q' to quit.", state="normal")

    def checkCollide(self):
        if self.snakeCoords[-1] in self.activeSnake[0:-1]:
            return False
        elif self.snakeCoords[-1] == self.appleCoords:
            self.elongate = True
            self.placeApple()
            return True
        else:
            x, y = self.snakeCoords[-1]
            if x < 0 or x >= self.params["width"] or y < 0 or y >= self.params["height"]:
                return False
        return True

    def moveSnake(self):
        '''
        self.snakeDir
            == (0, -1) -> up
            == (1, 0) -> right
            == (0, 1) -> down
            == (-1, 0) -> left
        '''
        head_pos = self.snakeCoords[-1]
        new_pos = (head_pos[0]+self.snakeDir[0], head_pos[1]+self.snakeDir[1])
        self.snakeCoords.append(new_pos)
        if self.elongate:
            self.elongate = False
        else:
            self.snakeCoords.pop(0)
        if not self.checkCollide():
            self.gameOver()

    def arrowLeft(self, event):
        self.snakeDir = (-1, 0)

    def arrowRight(self, event):
        self.snakeDir = (1, 0)

    def arrowUp(self, event):
        self.snakeDir = (0, -1)

    def arrowDown(self, event):
        self.snakeDir = (0, 1)

def getParams():
    if ask_for_params:
        params = {}
        params["width"] = int(input("Width: "))
        params["height"] = int(input("Height: "))
        params["speed"] = int(input("Speed: "))
        params["colour"] = input("Colour: ")
    else:
        params = {
            "width": 10,
            "height": 10,
            "speed": 250,
            "colour": "red",
        }
    return params
        
def main():

    params = getParams()

    GUIManager(params)

if __name__ == '__main__':
    main()