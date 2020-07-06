#Version number:
vName = "v1.1.1"

'''
Key:
P = Pawn
B = Bishop
N = Knight
R = Rook
Q = Queen
K = King

Capital = white
Lowercase = black

Notable features for inclusion:
-Castling
-En passant capture
-Checkmate detection

Notes:
-RunFunc was included so that pawns could ask the user how to upgrade, but only on actual moves, not a mate detection. The mate detection will not run the included runFunc, while with the advValidation, if it is ok, then run the function. Basically, only run runFunc when you're happy that it will become the actual board.
'''

# imports
import re
import copy

# canPass is used for info about the piece moving, for pawns that is if it is their first move (for en passant capture), and for kings and rooks that is for if they have moved (for castling)
# update: kings and rooks have their own variables now, canPass is just for pawn

def hasStuff(checkList):
    for i in checkList:
        if i:
            # Found something
            return True
    return False

def pawnUpgrade(board, x, y):
    newBoard = copy.deepcopy(board)
    up = input("Would you like to promote your pawn to a knight, bishop, rook, or queen? ").lower()
    while up != "knight" and up != "bishop" and up != "rook" and up != "queen":
        print("Invalid choice. Please enter 'knight', 'bishop', 'rook' or 'queen'.")
        up = input("Would you like to promote your pawn to a knight, bishop, rook, or queen? ").lower()
    if up == "knight":
        newBoard[x][y] = knight(board[x][y].letter.islower())
        return newBoard
    if up == "bishop":
        newBoard[x][y] = bishop(board[x][y].letter.islower())
        return newBoard
    if up == "rook":
        newBoard[x][y] = rook(board[x][y].letter.islower(), False)
        return newBoard
    if up == "queen":
        newBoard[x][y] = queen(board[x][y].letter.islower())
        return newBoard

class piece():
    def __init__(self, letter, name, isBlack):
        if isBlack:
            self.letter = letter.lower()
        else:
            self.letter = letter
        self.name = name
    
    def pieceCalled(self, board, spotx, spoty, x, y):
        # this method is called when the user wishes to use this piece to move or take
        # possible return values:
        # False: generic error
        # String: specific error, string is error message
        # 2d List: board with updated positions
        raise NotImplementedError

    def doesCheck(self, board, spotx, spoty, x, y):
        # is this piece putting the other team's king in check?
        raise NotImplementedError

    def restore(self):
        # it is now this piece's team's turn - this function is here for en passant captures, so that the ability to en passant capture stops if it is not utilised immediately
        # this function always returns nothing
        return


class pawn(piece):
    def __init__(self, isBlack, canPass):
        super().__init__("P", "Pawn", isBlack)
        self. canPass = canPass

    def pieceCalled(self, board, spotx, spoty, x, y):
        newBoard = copy.deepcopy(board)
        # With the pawn, a lot of things depend on what side the pawn is on
        if(self.letter.isupper()):
            # the pawn is white
            if(spoty == y + 1 and spotx == x):
                # attempting to move one space forwards
                if(board[x][spoty]):
                    # there is a piece there - can't move there!
                    return False, "There is a piece obstructing the pawn from moving there.", None
                else:
                    # no piece there - pawn moving forwards
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(False, False)
                    if(spoty == 7):
                        # promotion time!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        return True, newBoard, None
            elif(spoty == y + 2 and spotx == x and y == 1):
                # attempting to move two spaces forwards
                # could do a check for an empty space in the middle square + target square at the same time, but to get different error messages I'm not going to
                if(board[x][y+1]):
                    # a piece is in the way
                    return False, "There is a piece obstructing the pawn from moving there.", None
                elif(board[x][spoty]):
                    # there is a piece where the pawn is trying to move to
                    return False, "There is a piece obstructing the pawn from moving there.", None
                else:
                    # all good
                    newBoard[x][y] = None
                    # one of the only times we set the pawn's canPass to True
                    newBoard[spotx][spoty] = pawn(False, True)
                    return True, newBoard, None
            elif(spoty == y + 1 and spotx == x + 1):
                # moving diagonal one space to the right
                if(board[spotx][spoty]):
                    # there is a piece where the pawn is trying to take
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(False, False)
                    # check for promotion
                    if(spoty == 7):
                        # top row - promotion!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        # no promotion
                        return True, newBoard, None
                elif(y == 4 and board[spotx][y]):
                    # en passant capture to the right
                    if(board[spotx][y].letter == "p"):
                        if(board[spotx][y].canPass):
                            newBoard[x][y] = None
                            newBoard[spotx][spoty] = pawn(False, False)
                            # also removing pawn that was en passant captured
                            newBoard[spotx][y] = None
                            return True, newBoard, None
                        else:
                            return False, "You cannot en passant capture that pawn.", None
                    else:
                        return False, "The pawn cannot move like that.", None
                else:
                    return False, "The pawn cannot move like that.", None
            elif(spoty == y + 1 and spotx == x - 1):
                # moving diagonal one space to the left
                if(board[spotx][spoty]):
                    # there is a piece where the pawn is trying to move
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(False, False)
                    if(spoty == 7):
                        # pawn can be promoted!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        return True, newBoard, None
                elif(y == 4 and board[spotx][y]):
                    if(board[spotx][y].letter == "p"):
                        if(board[spotx][y].canPass):
                            # en passant capture confirmed!
                            newBoard[x][y] = None
                            newBoard[spotx][spoty] = pawn(False, False)
                            newBoard[spotx][y] = None
                            return True, newBoard, None
                        else:
                            return False, "You cannot en passant capture that pawn.", None
                    else:
                        return False, "The pawn cannot move like that.", None
                else:
                    return False, "The pawn cannot move like that.", None
            else:
                return False, "The pawn cannot move like that.", None
        else:
            # pawn is black
            if(spoty == y - 1 and spotx == x):
                # attempting to move one space forwards
                if(board[x][spoty]):
                    # there is a piece there - can't move there!
                    return False, "There is a piece obstructing the pawn from moving there.", None
                else:
                    # no piece there - pawn moving forwards
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(True, False)
                    if(spoty == 0):
                        # promotion time!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        return True, newBoard, None
            elif(spoty == y - 2 and spotx == x and y == 6):
                # attempting to move two spaces forwards
                # could do a check for an empty space in the middle square + target square at the same time, but to get different error messages I'm not going to
                if(board[x][y-1]):
                    # a piece is in the way
                    return False, "There is a piece obstructing the pawn from moving there.", None
                elif(board[x][spoty]):
                    # there is a piece where the pawn is trying to move to
                    return False, "There is a piece obstructing the pawn from moving there.", None
                else:
                    # all good
                    newBoard[x][y] = None
                    # one of the only times we set the pawn's canPass to True
                    newBoard[spotx][spoty] = pawn(True, True)
                    return True, newBoard, None
            elif(spoty == y - 1 and spotx == x + 1):
                # moving diagonal one space to the right
                if(board[spotx][spoty]):
                    # there is a piece where the pawn is trying to take
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(True, False)
                    # check for promotion
                    if(spoty == 0):
                        # bottom row - promotion!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        # no promotion
                        return True, newBoard, None
                elif(y == 3 and board[spotx][y]):
                    # en passant capture to the right
                    if(board[spotx][y].letter == "P"):
                        if(board[spotx][y].canPass):
                            newBoard[x][y] = None
                            newBoard[spotx][spoty] = pawn(True, False)
                            # also removing pawn that was en passant captured
                            newBoard[spotx][y] = None
                            return True, newBoard, None
                        else:
                            return False, "You cannot en passant capture that pawn.", None
                    else:
                        return False, "The pawn cannot move like that.", None
                else:
                    return False, "The pawn cannot move like that.", None
            elif(spoty == y - 1 and spotx == x - 1):
                # moving diagonal one space to the left
                if(board[spotx][spoty]):
                    # there is a piece where the pawn is trying to move
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = pawn(True, False)
                    if(spoty == 0):
                        # pawn can be promoted!
                        return True, newBoard, lambda b : pawnUpgrade(b, spotx, spoty)
                    else:
                        return True, newBoard, None
                elif(y == 3 and board[spotx][y]):
                    if(board[spotx][y].letter == "P"):
                        if(board[spotx][y].canPass):
                            # en passant capture confirmed!
                            newBoard[x][y] = None
                            newBoard[spotx][spoty] = pawn(True, False)
                            newBoard[spotx][y] = None
                            return True, newBoard, None
                        else:
                            return False, "You cannot en passant capture that pawn.", None
                    else:
                        return False, "The pawn cannot move like that.", None
                else:
                    return False, "The pawn cannot move like that.", None
            else:
                return False, "The pawn cannot move like that.", None            

        return False, "ERROR: pawn.pieceCalled should have already returned by this point.", None

    def doesCheck(self, board, spotx, spoty, x, y):
        if(self.letter.isupper()):
            # pawn is white
            return (spoty == y + 1 and (spotx == x + 1 or spotx == x - 1))
        else:
            # pawn is black
            return (spoty == y - 1 and (spotx == x + 1 or spotx == x - 1))

    def restore(self):
        self.canPass = False
        return

class knight(piece):
    def __init__(self, isBlack):
        super().__init__("N", "Knight", isBlack)

    def pieceCalled(self, board, spotx, spoty, x, y):
        newBoard = copy.deepcopy(board)
        if(((spotx == x + 2 or spotx == x - 2) and (spoty == y + 1 or spoty == y - 1)) or ((spotx == x + 1 or spotx == x - 1) and (spoty == y + 2 or spoty == y - 2))):
            newBoard[x][y] = None
            newBoard[spotx][spoty] = knight(self.letter.islower())
            return True, newBoard, None
        else:
            return False, "The knight cannot move like that.", None

    def doesCheck(self, board, spotx, spoty, x, y):
        return (((spotx == x + 2 or spotx == x - 2) and (spoty == y + 1 or spoty == y - 1)) or ((spotx == x + 1 or spotx == x - 1) and (spoty == y + 2 or spoty == y-2)))

class bishop(piece):
    def __init__(self, isBlack):
        super().__init__("B", "Bishop", isBlack)

    def pieceCalled(self, board, spotx, spoty, x, y):
        newBoard = copy.deepcopy(board)
        if(abs(spotx-x) == abs(spoty-y)):
            if(spoty > y):
                # going up
                if(spotx > x):
                    # going up right
                    # this next bit of code could be compressed into a hasStuff([column[...] for ... in ...]) if wanted to, but not massively necessary
                    # heck, i'll do it anyway (just for fun)
                    if(hasStuff([column[y+1+count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False, "There are obstructions between the bishop and its target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = bishop(self.letter.islower())
                        return True, newBoard, None
                else:
                    # going up left
                    if(hasStuff([column[spoty-1-count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False, "There are obstructions between the bishop and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = bishop(self.letter.islower())
                        return True, newBoard, None
            else:
                if(spotx > x):
                    # going down right
                    if(hasStuff([column[y-1-count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False, "There are obstructions between the bishop and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = bishop(self.letter.islower())
                        return True, newBoard, None
                else:
                    # going down left
                    if(hasStuff([column[spoty+1+count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False, "There are obstructions between the bishop and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = bishop(self.letter.islower())
                        return True, newBoard, None
        else:
            return False, "The bishop cannot move like that.", None

    def doesCheck(self, board, spotx, spoty, x, y):
        if(abs(spotx-x) == abs(spoty-y)):
            if(spoty > y):
                # going up
                if(spotx > x):
                    # going up right
                    # this next bit of code could be compressed into a hasStuff([column[...] for ... in ...]) if wanted to, but not massively necessary
                    # heck, i'll do it anyway (just for fun)
                    if(hasStuff([column[y+1+count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False
                    else:
                        return True
                else:
                    # going up left
                    if(hasStuff([column[spoty-1-count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False
                    else:
                        return True
            else:
                if(spotx > x):
                    # going down right
                    if(hasStuff([column[y-1-count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False
                    else:
                        return True
                else:
                    # going down left
                    if(hasStuff([column[spoty+1+count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False
                    else:
                        return True
        else:
            return False


class rook(piece):
    def __init__(self, isBlack, fresh):
        super().__init__("R", "Rook", isBlack)
        self.fresh = fresh

    def pieceCalled(self, board, spotx, spoty, x, y):
        # Rook has been called to move to a given spot, but can it do it?
        newBoard = copy.deepcopy(board)
        if(x == spotx or y == spoty): 
            # target is on same row or column as the rook
            if(spotx > x):
                # moving right
                if not hasStuff([i[y] for i in board[x+1:spotx]]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = rook(self.letter.islower(), False)
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the rook and its target", None
            if(spotx < x):
                # moving left
                if not hasStuff([i[y] for i in board[spotx+1:x]]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = rook(self.letter.islower(), False)
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the rook and its target", None           
            if(spoty > y):
                # moving up
                if not hasStuff(board[x][y+1:spoty]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = rook(self.letter.islower(), False)
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the rook and its target", None
            if(spoty < y):
                # moving down
                if not hasStuff(board[x][spoty+1:y]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = rook(self.letter.islower(), False)
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the rook and its target", None
        else:
            return False, "The rook cannot move like that.", None

        return False, "ERROR: rook.pieceCalled should have already returned by this point.", None

    def doesCheck(self, board, spotx, spoty, x, y):
        if(x == spotx or y == spoty): 
            # king is on same row or column as the rook
            if(spotx > x):
                # right
                if not hasStuff([i[y] for i in board[x+1:spotx]]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                   
            if(spotx < x):
                # left
                if not hasStuff([i[y] for i in board[spotx+1:x]]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                    
            if(spoty > y):
                # up
                if not hasStuff(board[x][y+1:spoty]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                   
            if(spoty < y):
                # down
                if not hasStuff(board[x][spoty+1:y]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False
        else:
            return False

        return False # uh oh alert


class queen(piece):
    # the queen is basically just the rook and the bishop stuck together, and the code certainly shows this!

    def __init__(self, isBlack):
        super().__init__("Q", "Queen", isBlack)

    def pieceCalled(self, board, spotx, spoty, x, y):
        # rook stuff
        # ignore any comments that say rook, just pretend they say queen

        # Rook has been called to move to a given spot, but can it do it?
        newBoard = copy.deepcopy(board)
        if(x == spotx or y == spoty): 
            # target is on same row or column as the rook
            if(spotx > x):
                # moving right
                if not hasStuff([i[y] for i in board[x+1:spotx]]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = queen(self.letter.islower())
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the queen and its target", None
            if(spotx < x):
                # moving left
                if not hasStuff([i[y] for i in board[spotx+1:x]]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = queen(self.letter.islower())
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the queen and its target", None           
            if(spoty > y):
                # moving up
                if not hasStuff(board[x][y+1:spoty]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = queen(self.letter.islower())
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the queen and its target", None
            if(spoty < y):
                # moving down
                if not hasStuff(board[x][spoty+1:y]):
                    # nothing between the rook and its target
                    newBoard[x][y] = None
                    newBoard[spotx][spoty] = queen(self.letter.islower())
                    return True, newBoard, None
                else:
                    return False, "There are obstructions between the queen and its target", None
        
        # bishop stuff
        elif(abs(spotx-x) == abs(spoty-y)):
            if(spoty > y):
                # going up
                if(spotx > x):
                    # going up right
                    # this next bit of code could be compressed into a hasStuff([column[...] for ... in ...]) if wanted to, but not massively necessary
                    # heck, i'll do it anyway (just for fun)
                    if(hasStuff([column[y+1+count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False, "There are obstructions between the queen and its target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = queen(self.letter.islower())
                        return True, newBoard, None
                else:
                    # going up left
                    if(hasStuff([column[spoty-1-count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False, "There are obstructions between the queen and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = queen(self.letter.islower())
                        return True, newBoard, None
            else:
                if(spotx > x):
                    # going down right
                    if(hasStuff([column[y-1-count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False, "There are obstructions between the queen and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = queen(self.letter.islower())
                        return True, newBoard, None
                else:
                    # going down left
                    if(hasStuff([column[spoty+1+count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False, "There are obstructions between the queen and the target.", None
                    else:
                        newBoard[x][y] = None
                        newBoard[spotx][spoty] = queen(self.letter.islower())
                        return True, newBoard, None
        else:
            return False, "The queen cannot move like that.", None


        return False, "ERROR: queen.pieceCalled should have already returned by this point.", None

    def doesCheck(self, board, spotx, spoty, x, y):
        # same deal, ignore rook in comments

        if(x == spotx or y == spoty): 
            # king is on same row or column as the rook
            if(spotx > x):
                # right
                if not hasStuff([i[y] for i in board[x+1:spotx]]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                   
            if(spotx < x):
                # left
                if not hasStuff([i[y] for i in board[spotx+1:x]]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                    
            if(spoty > y):
                # up
                if not hasStuff(board[x][y+1:spoty]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False                   
            if(spoty < y):
                # down
                if not hasStuff(board[x][spoty+1:y]):
                    # nothing between the rook and the king
                    return True
                else:
                    return False
        elif(abs(spotx-x) == abs(spoty-y)):
            if(spoty > y):
                # going up
                if(spotx > x):
                    # going up right
                    # this next bit of code could be compressed into a hasStuff([column[...] for ... in ...]) if wanted to, but not massively necessary
                    # heck, i'll do it anyway (just for fun)
                    if(hasStuff([column[y+1+count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False
                    else:
                        return True
                else:
                    # going up left
                    if(hasStuff([column[spoty-1-count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False
                    else:
                        return True
            else:
                if(spotx > x):
                    # going down right
                    if(hasStuff([column[y-1-count] for count, column in enumerate(board[x+1:spotx])])):
                        # blocked
                        return False
                    else:
                        return True
                else:
                    # going down left
                    if(hasStuff([column[spoty+1+count] for count, column in enumerate(board[spotx+1:x])])):
                        # blocked
                        return False
                    else:
                        return True
        else:
            return False

        return False # uh oh alert


class king(piece):
    def __init__(self, isBlack, fresh):
        super().__init__("K", "King", isBlack)
        self.fresh = fresh

    def pieceCalled(self, board, spotx, spoty, x, y):
        # also need to include castling
        newBoard = copy.deepcopy(board)
        if(abs(spotx - x) <= 1 and abs(spoty - y) <= 1):
            # one square away - we can go there
            newBoard[x][y] = None
            # no longer fresh
            newBoard[spotx][spoty] = king(self.letter.islower(), False)
            return True, newBoard, None
        elif(self.fresh == True):
            # castling
            if(spoty == y):
                # same y
                if(spotx == 6):
                    # castling to the right
                    if(board[7][y]):
                        # piece in corner
                        if(board[7][y].letter.upper() == "R"):
                            # it's a rook
                            if(board[7][y].fresh == True):
                                # fresh rook - now check for obstructions
                                # we know it must be on our team because otherwise it would not be fresh!
                                if(not board[5][y] and not board[6][y]):
                                    # no obstructions - time to see if we are castling through or out of check
                                    if(not checkCheck(board, self.letter.islower())):
                                        # not starting in check, but check we're not castling through check
                                        newBoard[x][y] = None
                                        newBoard[x+1][y] = king(self.letter.islower(), False)
                                        if(not checkCheck(newBoard, self.letter.islower())):
                                            # not going through check, we're good!
                                            # we don't need to check whether we end up in check, that gets checked later
                                            newBoard[x+1][y] = None
                                            newBoard[spotx][y] = king(self.letter.islower(), False)
                                            # move rook
                                            newBoard[7][y] = None
                                            newBoard[5][y] = rook(self.letter.islower(), False)
                                            return True, newBoard, None
                                        else:
                                            return False, "You cannot castle through check.", None
                                    else:
                                        return False, "You cannot castle out of check.", None
                                else:
                                    return False, "There are obstructions preventing castling.", None
                            else:
                                return False, "You cannot castle with a rook that has been moved.", None
                        else:
                            return False, "You can only castle with a rook in the corner.", None
                    else:
                        return False, "You cannot castle without a rook in the corner.", None
                elif(spotx == 2):
                    # castling to the left
                    if(board[0][y]):
                        # piece in corner
                        if(board[0][y].letter.upper() == "R"):
                            # it's a rook
                            if(board[0][y].fresh == True):
                                # fresh rook
                                # need to check three spaces
                                if(not board[3][y] and not board[2][y] and not board[1][y]):
                                    # lastly check to make sure we're not castling out of or through check.
                                    if(not checkCheck(board, self.letter.islower())):
                                        # not starting in check, but check we're not castling through check
                                        newBoard[x][y] = None
                                        newBoard[x-1][y] = king(self.letter.islower(), False)
                                        if(not checkCheck(newBoard, self.letter.islower())):
                                            # not going through check, we're good!
                                            # we don't need to check whether we end up in check, that gets checked later
                                            newBoard[x-1][y] = None
                                            newBoard[spotx][y] = king(self.letter.islower(), False)
                                            # rook
                                            newBoard[0][y] = None
                                            newBoard[3][y] = rook(self.letter.islower(), False)
                                            return True, newBoard, None
                                        else:
                                            return False, "You cannot castle through check.", None
                                    else:
                                        return False, "You cannot castle out of check.", None
                                else:
                                    return False, "There are obstructions preventing castling.", None
                            else:
                                return False, "You cannot castle with a rook that has been moved.", None
                        else:
                            return False, "You can only castle with a rook in the corner.", None
                    else:
                        return False, "You cannot castle without a rook in the corner.", None
                else:
                    return False, "The king cannot move like that.", None
            else:
                return False, "The king cannot move like that.", None

        else:
            return False, "The king cannot move like that.", None


        return False, "WIP", None

    def doesCheck(self, board, spotx, spoty, x, y):
        # the king can still check!
        return (abs(spotx - x) <= 1 and abs(spoty - y) <= 1)

# x then y
# startingBoard[letter][number] effectively (kinda)

# Actual starting board
startingBoard = [
        [rook(False, True), pawn(False, False), *[None]*4,
         pawn(True, False), rook(True, True)],  # A
        [knight(False), pawn(False, False), *[None]*4,
         pawn(True, False), knight(True)],  # B
        [bishop(False), pawn(False, False), *[None]*4,
         pawn(True, False), bishop(True)],  # C
        [queen(False), pawn(False, False), *[None]*4,
         pawn(True, False), queen(True)],  # D
        [king(False, True), pawn(False, False), *[None]*4,
         pawn(True, False), king(True, True)],  # E
        [bishop(False), pawn(False, False), *[None]*4,
         pawn(True, False), bishop(True)],  # F
        [knight(False), pawn(False, False), *[None]*4,
         pawn(True, False), knight(True)],  # G
        [rook(False, True), pawn(False, False), *[None]*4,
         pawn(True, False), rook(True, True)]  # H
]

def whatPrint(val):
    if val:
        return val.letter
    else:
        return " "


def printBoard(bState):
    for i in range(7, -1, -2):
        print(str(i+1)+"|", "["+whatPrint(bState[0][i])+"]", " "+whatPrint(bState[1][i])+" ", "["+whatPrint(bState[2][i])+"]", " "+whatPrint(bState[3]
                                                                                                                                             [i])+" ", "["+whatPrint(bState[4][i])+"]", " "+whatPrint(bState[5][i])+" ", "["+whatPrint(bState[6][i])+"]", " "+whatPrint(bState[7][i])+" ")
        print(str(i)+"|", " "+whatPrint(bState[0][i-1])+" ", "["+whatPrint(bState[1][i-1])+"]", " "+whatPrint(bState[2][i-1])+" ", "["+whatPrint(
            bState[3][i-1])+"]", " "+whatPrint(bState[4][i-1])+" ", "["+whatPrint(bState[5][i-1])+"]", " "+whatPrint(bState[6][i-1])+" ", "["+whatPrint(bState[7][i-1])+"]")
    print("-|--------------------------------")
    print(" |  A   B   C   D   E   F   G   H")

def getKing(board, blackKing):
    for x, column in enumerate(board):
        for y, square in enumerate(column):
            if(square):
                if(square.letter.islower() == blackKing and square.letter.upper() == "K"):
                    return x, y

def checkCheck(board, blackKing):
    #get king square
    kingX, kingY = getKing(board, blackKing)

    # loop through every square
    for x, column in enumerate(board):
        for y, square in enumerate(column):
            if square:
                if(square.letter.isupper() == blackKing):
                    # if letter's team is not the team of the endangered king, check for check
                    if(square.doesCheck(board, kingX, kingY, x, y)):
                        # it checks the king, return True
                        return True

    # nothing triggered it, so king is not in check
    return False

def basicValidation(moveString):
    # basic validation first

    # check if move is in correct format
    if(not re.match("[A-H][1-8] [A-H][1-8]", moveString)):
        # invalid format
        return "Invalid format."
    # user inputted correct format, continue

    # check if positions specified are the same
    if(moveString[0:2] == moveString[3:5]):
        # same positions
        return "Origin position cannot be the same as target position."
    # user inputted different positions

    return None

def advValidation(originX, originY, targetX, targetY, board, isBlack):
    # check if a piece exists at origin
    if(not board[originX][originY]):
        # blank origin
        return False, "Origin cannot be a blank square."
    # piece exists at origin square

    # check if the piece at origin is your piece
    if(board[originX][originY].letter.isupper() == isBlack):
        # other team's piece
        return False, "Origin must be one of your pieces."

    # check if there is one of your pieces at the target square
    if(board[targetX][targetY]):
        # piece exists at square
        if(board[targetX][targetY].letter.islower() == isBlack):
            # one of your pieces, can't move of take there!
            return False, "The target square cannot be the location of one of your own pieces."

    # now let's see what the piece has to say
    didWork, pieceOut, runFunc = board[originX][originY].pieceCalled(board, targetX, targetY, originX, originY)

    # check if error was returned
    if(not didWork):
        # error was returned
        return False, pieceOut
    # piece can move or take to that square, board was returned

    # lastly, see if this move ends up their king in check
    # this ensures A. you can't put your king in check yourself by moving your pieces
    # and B. if your opponent puts your king in check, you gotta do something about it and can't just ignore it!

    if(checkCheck(pieceOut, isBlack)):
        # doing this move would leave you or put you in check
        return False, "This move leaves you or puts your king in check."

    # ok, lastly, since this board will DEFINATELY be going into the actual board, we can run any runFunc returned by the piece

    if runFunc:
        return True, runFunc(pieceOut)
    else:
        return True, pieceOut
    

def doMove(moveString, board, isBlack):
    # validation was split in two for a now unused reason
    # they could be spliced back in where they are called in this method if wanted

    basicResult = basicValidation(moveString)

    if basicResult:
        return False, basicResult

    # basic validation complete, now seeing if this is possible in the game scenario

    # get the string's data
    originX = ord(moveString[0])-65  # A -> 0, B -> 1, etc
    originY = int(moveString[1])-1
    targetX = ord(moveString[3])-65  # A -> 1, B -> 2, etc
    targetY = int(moveString[4])-1

    # now for advanced validation, and just pass back the result

    return advValidation(originX, originY, targetX, targetY, board, isBlack)

def isMate(board, isBlack):
    # For every square, if it is one of our pieces, then pieceCalled it with every other empty or enemy square
    for x, column in enumerate(board):
        for y, square in enumerate(column):
            if(square):
                # there is a piece at that square
                if(square.letter.islower() == isBlack):
                    # it is one of your pieces
                    for x1, column1 in enumerate(board):
                        for y1, square1 in enumerate(column1):
                            # for every square on the board
                            if(x != x1 or y != y1):
                                # origin and target are not the same
                                targetGood = True
                                # check that our own piece is not at the target
                                if square1:
                                    if square1.letter.islower() == isBlack:
                                        # our team piece is there
                                        targetGood = False
                                if targetGood:
                                    # target is blank or enemy piece
                                    works, value, runFunc = square.pieceCalled(board, x1, y1, x, y)
                                    # runFunc not needed
                                    del runFunc
                                    if works:
                                        # move has returned successful, but does it leave or put our king in check?
                                        if not checkCheck(value, isBlack):
                                            # nope, it's good
                                            # return False, there is no mate
                                            return False
    # reached the end, and return was not called - we have a mate
    return True

def restoreAll(board, isBlack):
    newBoard = copy.deepcopy(board)
    for x, column in enumerate(newBoard):
        for y, square in enumerate(column):
            if(square):
                if(square.letter.islower() == isBlack):
                    square.restore()
                    newBoard[x][y] = square
    return newBoard

def gameLoop(startingBoard, white, black):
    board = startingBoard
    while True:
        # main game loop

        # restore white pieces
        board = restoreAll(board, False)

        # print board
        print()
        printBoard(board)
        print()

        #need to check for check, checkmate + stalemate
        if(checkCheck(board, False)):
            # in check - check for checkmate
            if(isMate(board, False)):
                # checkmate - black wins!
                print("Checkmate!", black, "wins!") # Checkmate! Robert wins!
                return
            else:
                # not in checkmate, but still in check
                print(white, "is in check!")
                print()
        else:
            # not in check, possible stalemate though
            if(isMate(board, False)):
                # stalemate
                print("Stalemate!")
                return
            # nothing special then

        # start with white
        # Robert, enter your next move:
        move = input(white+", enter your next move: ")
        move = move.upper()
        if(move == "RESIGN"):
            print()
            print(white, "resigned!", black, "wins!")
            return
        elif(move == "EXIT" or move == "QUIT"):
            return
        works, value = doMove(move, board, False)
        if works:
            # move works, enact move on board
            board = value
        else:
            # move is errored, ask user to try again
            while not works: 
                print(value)
                move = input("Please enter a valid move: ")
                move = move.upper()
                if(move == "RESIGN"):
                    print()
                    print(white, "resigned!", black, "wins!")
                    return
                elif(move == "EXIT" or move == "QUIT"):
                    return
                works, value = doMove(move, board, False)
            board = value

        # print new board
        print()
        printBoard(board)
        print()

        # restore black pieces
        board = restoreAll(board, True)

        #need to check for check, checkmate + stalemate
        if(checkCheck(board, True)):
            # in check - check for checkmate
            if(isMate(board, True)):
                # checkmate - white wins!
                print("Checkmate!", white, "wins!")
                return
            else:
                # not in checkmate, but still in check
                print(black, "is in check!")
                print()
        else:
            # not in check, possible stalemate though
            if(isMate(board, True)):
                # stalemate
                print("Stalemate!")
                return
            # nothing special then

        # now black's move
        move = input(black+", enter your next move: ")
        move = move.upper()
        if(move == "RESIGN"):
            print()
            print(black, "resigned!", white, "wins!")
            return
        elif(move == "EXIT" or move == "QUIT"):
            return
        works, value = doMove(move, board, True)
        if works:
            # move works, enact move on board
            board = value
        else:
            # move is errored, ask user to try again
            while not works:
                print(value)
                move = input("Please enter a valid move: ")
                move = move.upper()
                if(move == "RESIGN"):
                    print()
                    print(black, "resigned!", white, "wins!")
                    return
                elif(move == "EXIT" or move == "QUIT"):
                    return
                works, value = doMove(move, board, True)
            board = value

# get names
print("Welcome to TextChess", vName)
print()
whiteName = input("White team, what is your name? ")
blackName = input("Black team, what is your name? ")

while True:
    print()
    input("Press 'Enter' when you are ready to begin. ")
    gameLoop(startingBoard, whiteName, blackName)
    print()
    again = input("Would you like to play again? (yes/no) ").lower()
    while again != "yes" and again != "no":
        print("Invalid input. Please answer 'yes' or 'no'.")
        print()
        again = input("Would you like to play again? (yes/no) ").lower()
    print()
    if again == "yes":
        sameName = input("Would you like to keep the same names? (yes/no) ").lower()
        while sameName != "yes" and sameName != "no":
            print("Invalid input. Please answer 'yes' or 'no'.")
            print()
            sameName = input("Would you like to keep the same names? (yes/no) ").lower()
        if sameName == "no":
            print()
            whiteName = input("White team, what is your name? ")
            blackName = input("Black team, what is your name? ")
    else:
        break

print("Thank you for playing TextChess", vName)
        