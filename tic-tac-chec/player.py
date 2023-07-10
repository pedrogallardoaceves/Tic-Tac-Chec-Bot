"""
Value code for each piece is as follows:
    - pawn = 1 for white, -1 for black
    - bishop =  2 for white, -2 for black
    - knight =  3 for white, -3 for black
    - rook =  4 for white, -4 for black

* It is recommended to store the direction of movement of both your pawn and opponent's pawn.

"""
import copy
import random
import time

class _TTCPlayer:
    # valuesCode is a list containing the value code that you must use to represent your pieces over the board. 
    # The sign of the value code will tell you if you are playing as white or black pieces.
    # The values are in the order: pawn, bishop, knight, rook
    def __init__(self, name):
        self.name = name
        self.pawnDirection = -1
        self.currentTurn = -1

        self.piecesOnBoard = [0] * 5

    def __printBoard(self, board):
        print('-------')
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] >= 0:
                    print(' ', end='')
                print(board[i][j], end='')
            print()
        print('-------')

    def setColor(self, piecesColor):
        self.piecesCode = [0, 1, 2, 3, 4]
        self.piecesCode = [x*piecesColor for x in self.piecesCode]
        self.piecesColor = piecesColor
    
    def __updatePawnDirection(self, board):
        # If the pawn is in the limit of the board, it should reverse
        if self.piecesColor in board[0]:
            self.pawnDirection = 1
        
        # If the pawn is in the start of the board, it should go forward
        if self.piecesColor in board[3]:
            self.pawnDirection = -1
    
    def __sameSign(self, a, b):
        return ((a < 0 and b < 0) or (a > 0  and b > 0))
    
    def __isInsideBoard(self, row, col):
        return (row >= 0 and row < 4 and col >= 0 and col < 4)
    
    # Function to check whether a movement was a movement or not
    # If it was a movement, it also checks if it was a capture or not.
    # For a movement to be classified as a capture, 2 conditions have to occur
    # 1. Only 2 squares changed value
    # 2. One square has to change from used to empty and the other from used to used with different color    
    def __wasPieceMovement(self, oldBoard, newBoard):
        changedSquares = []

        for i in range(4):
            for j in range(4):
                if oldBoard[i][j] != newBoard[i][j]:
                    changedSquares.append((i, j))

        if len(changedSquares) != 2:
            return False, False
        
        def areChangesFromCapture(row1, col1, row2, col2):
            return (newBoard[row1][col1] == 0
                    and oldBoard[row2][col2] != 0 
                    and newBoard[row2][col2] == oldBoard[row1][col1])
        
        def areChangesFromMovement(row1, col1, row2, col2):
            return (newBoard[row1][col1] == 0
                    and newBoard[row2][col2] == oldBoard[row1][col1])
        
        wasMovement = (areChangesFromMovement(changedSquares[0][0], changedSquares[0][1], changedSquares[1][0], changedSquares[1][1]) 
                or areChangesFromMovement(changedSquares[1][0], changedSquares[1][1], changedSquares[0][0], changedSquares[0][1]))
        
        wasCapture = (areChangesFromCapture(changedSquares[0][0], changedSquares[0][1], changedSquares[1][0], changedSquares[1][1]) 
                or areChangesFromCapture(changedSquares[1][0], changedSquares[1][1], changedSquares[0][0], changedSquares[0][1]))

        return (wasMovement, wasCapture)
    
    def __getPawnValidMovements(self, position, board, pawnDirection):
        validMovements = []
        
        row = position[0]
        col = position[1]

        # Move 1 to the front
        newRow = row + pawnDirection
        if self.__isInsideBoard(newRow, col) and board[newRow][col] == 0:
            validMovements.append((newRow, col))

        # Attack to the left
        newCol = col - 1
        if self.__isInsideBoard(newRow, newCol) and board[newRow][newCol] != 0 and not self.__sameSign(board[newRow][newCol], board[row][col]):
            validMovements.append((newRow, newCol))

        # Attack to the right
        newCol = col + 1
        if self.__isInsideBoard(newRow, newCol) and board[newRow][newCol] != 0 and not self.__sameSign(board[newRow][newCol], board[row][col]):
            validMovements.append((newRow, newCol))

        return validMovements
    
    def __getBishopValidMovements(self, position, board):
        validMovements = []

        row = position[0]
        col = position[1]

        # To check whether I already encountered a piece in this diagonal or not
        # 0 -> Up-Left Diagonal
        # 1 -> Up-Right Diagonal
        # 2 -> Down-Left Diagonal
        # 3 -> Down-Right Diagonal
        diagEncounteredPiece = [False] * 4

        # Describe the direction of the movement for the bishop in the same
        # order as described above
        movDirection = [[-1, -1],
                     [-1, 1],
                     [1, -1],
                     [1, 1]]

        # A bishop can move at most 3 squares
        for i in range(1,4):
            # Check 4 directions of movement
            for j in range(4):
                newCol = col + i * movDirection[j][0]
                newRow = row + i * movDirection[j][1]

                # If I haven't found a piece yet in this direction and its inside the board
                if not diagEncounteredPiece[j] and self.__isInsideBoard(newRow, newCol):
                    # If the proposed square its occupied
                    if board[newRow][newCol] != 0:
                        # If the piece that occupies the square its from the opponent, then its a valid movement
                        if not self.__sameSign(board[row][col], board[newRow][newCol]):
                            validMovements.append((newRow, newCol))
                        diagEncounteredPiece[j] = True
                    else: # If not, just append the movement
                        validMovements.append((newRow, newCol))

        return validMovements

    def __getKnightValidMovements(self, position, board):
        validMovements = []

        row = position[0]
        col = position[1]


        # Describe the movements of the knight
        movements = [[-2, 1],
                     [-1, 2],
                     [1, 2],
                     [2, 1],
                     [2, -1],
                     [1, -2],
                     [-1, -2],
                     [-2, -1]]
        
        # Loop through all possible movements
        for move in movements:
            newRow = row + move[0]
            newCol = col + move[1]

            # For the knight we just need to check if the new square is valid and it is not occupied by a piece of the same color
            if self.__isInsideBoard(newRow, newCol) and not self.__sameSign(board[row][col], board[newRow][newCol]):
                validMovements.append((newRow, newCol))

        return validMovements
    
    def __getRookValidMovements(self, position, board):
        validMovements = []

        row = position[0]
        col = position[1]

        # Checks whether or not I have found a piece in this direction
        # 0 - Up
        # 1 - Right
        # 2 - Down
        # 3 - Left
        dirPieceEncountered = [False] * 4

        # Describe the direction of movement for the rook
        # The order is the same as described above
        movDirection = [[-1, 0],
                        [0, 1],
                        [1, 0],
                        [0, -1]]
        
        # The rook can move maximum 3 squares
        for i in range(1, 4):
            # Loop through all possible movements
            for j in range(4):
                newRow = row + i * movDirection[j][0]
                newCol = col + i * movDirection[j][1]

                if not dirPieceEncountered[j] and self.__isInsideBoard(newRow, newCol):
                    if board[newRow][newCol] != 0:
                        if not self.__sameSign(board[newRow][newCol], board[row][col]):
                            validMovements.append((newRow, newCol))
                        dirPieceEncountered[j] = True
                    else:
                        validMovements.append((newRow, newCol))

        return validMovements        

    def __getValidMovements(self, pieceCode, position, board):
        pawnDire=self.pawnDirection
        if abs(pieceCode) == 1:
            return self.__getPawnValidMovements(position, board, pawnDire)
        elif abs(pieceCode) == 2:
            return self.__getBishopValidMovements(position, board)
        elif abs(pieceCode) == 3:
            return self.__getKnightValidMovements(position, board)
        elif abs(pieceCode) == 4:
            return self.__getRookValidMovements(position, board)
        else:
            print("Piece ", pieceCode, " not recognized")
            return []
        


    # Check if the position on the board is a winning position.
    # It checks all the rows, columns and both diagonals looking for 4-pieces in a row.
    def __isWinningPosition(self, board):
        lrDiagSum = 0
        rlDiagSum = 0
        for i in range(4):
            # Check diagonal left-right, up-down
            if self.__sameSign(board[i][i], self.piecesColor):
                lrDiagSum += 1

            # Check diagonal right-left, up-down
            if self.__sameSign(board[i][3-i], self.piecesColor):
                rlDiagSum += 1

            rowSum = 0
            colSum = 0
            # Loop to check all squares in a row or column
            for j in range(4):
                # Check row i
                if self.__sameSign(board[i][j], self.piecesColor):
                    rowSum += 1

                # Check column i
                if self.__sameSign(board[j][i], self.piecesColor):
                    colSum += 1

            # If the sum is 4, we have 4-pieces in a row
            if rowSum == 4 or colSum == 4:
                return True
            
        # If the sum is 4, we have 4-pieces in a row   
        if lrDiagSum == 4 or rlDiagSum == 4:
            return True
        
        return False


    def __moveRandomPiece(self, board):
        #print(self.name, "::moveRandomPiece")
        piece = 0

        while(self.piecesOnBoard[piece] != 1): 
            piece = random.randint(1, 4)
        
        pieceCode = self.piecesCode[piece]
        row = -1
        col = -1

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == pieceCode:
                    row = i
                    col = j

                    i = len(board)
                    break

        validMovements = self.__getValidMovements(pieceCode, (row, col), board)
        if len(validMovements) == 0:
            return board
        
        newRow, newCol = validMovements[random.randint(0, len(validMovements)-1)]

        board[row][col] = 0
        board[newRow][newCol] = pieceCode

        return board


    def _moveWinningPiece (self, board):

        for piece in self.piecesOnBoard:
            pieceCode = piece + 1
            row = -1
            col = -1
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == pieceCode:
                        row = i
                        col = j

                        i = len(board)
                        break
                break
            
            validMovements = self.__getValidMovements(pieceCode, (row, col), board)
            for index, tuple in enumerate(validMovements):
                (newRow, newCol) = validMovements[index]
                newBoard = copy.deepcopy(board)
                newBoard[row][col] = 0
                newBoard[newRow][newCol] = pieceCode
                if self.__isWinningPosition(newBoard)==True:
                    self.__printBoard(newBoard)
                    print("Winning Board")
                    return newBoard

        newBoard = self.__moveRandomPiece(board)
        print("RANDOM MOVEMENT")
        return newBoard
        



    def __updatePiecesOnBoard(self, board):
        self.piecesOnBoard = [0] * 5
        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.__sameSign(board[i][j], self.piecesColor):
                    self.piecesOnBoard[abs(board[i][j])] = 1


    def __putRandomPiece(self, board):
        piece = -1
        while(piece == -1 or self.piecesOnBoard[piece] != 0):
            piece = random.randint(1, 4)

        newRow = random.randint(0, 3)
        newCol = random.randint(0, 3)

        while (board[newRow][newCol] != 0):
            newRow = random.randint(0, 3)
            newCol = random.randint(0, 3)

        board[newRow][newCol] = piece * self.piecesColor

        # If a new pawn is put on the board, we should reset its direction.
        if piece == 1:
            self.pawnDirection = -1

        return board

    
    def _putPieces(self, board):
        newboard = board
        if self.piecesOnBoard[1] == 0:
            if (board[3][0] == 0):
                newboard[3][3] = 1 * self.piecesColor
                return newboard
        elif self.piecesOnBoard[2] == 0:
            if (board[3][1] == 0):
                newboard[3][1] = 2 * self.piecesColor
                return newboard
        elif self.piecesOnBoard[3] == 0:
            if (board[3][2] == 0):
                newboard[3][2] = 3 * self.piecesColor
                return newboard
            
        elif self.piecesOnBoard[4] == 0:
            if (board[3][3]== 0):
                newboard[3][3] = 4 * self.piecesColor
                return newboard
        else:
            newboard = self.__putRandomPiece(newboard)
            return newboard


    def play(self, board):
        start = time.time()
        self.currentTurn += 1
        self.__updatePiecesOnBoard(board)

        originalBoard = copy.deepcopy(board)

        # We put a limit since there can be a really rare case when the only valid movement is a capture
        # And if in that moment it happens that you can no longer make any capture, it will cicle. That's why we put a limit.
        for _ in range(1000):
            if sum(self.piecesOnBoard) <4: # There are less than 4 pieces on board
                #newBoard = self._putPieces(board) #Funcion para iniciar con 4 en linea
                newBoard = self.__putRandomPiece(board)
            else:
                newBoard = self._moveWinningPiece(board) #Funcion para predecir casos en los que se gana de todos los casos posibles que tenemos para mover
                                                            #Da un error al querer actualizar la direccion del peón y un error de querer comparar diferentes tipos de objetos
                #newBoard = self.__moveRandomPiece(board)

            _, wasCapture = self.__wasPieceMovement(originalBoard, newBoard)

            if wasCapture:
                if self.availableCaptures > 0:
                    self.availableCaptures -= 1
                else:
                    board = copy.deepcopy(originalBoard)
                    continue

            if newBoard != originalBoard:
                break
        
        self.__updatePawnDirection(newBoard)
        print("Time taken: ", time.time() - start)
        #print(newBoard, flush=True)

        #return utils.updateSyncBoard(syncBoard, newBoard)

        return newBoard
                    

    def reset(self):
        self.pawnDirection = -1
        self.piecesOnBoard = [0] * 5
        self.currentTurn = -1
        self.availableCaptures = 5