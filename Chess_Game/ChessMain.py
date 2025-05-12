import pygame as p
from Chess_Game import ChessEngine, Ai

from Chess_Game.Ai import NegaMaxStrategy

BOARD_WIDTH = BOARD_HEIGHT = 840  # or 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 # 8 x 8 board
SQ_size = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15 # later for animations
IMAGES = {}

"""
Image loading dictionary, this will be called only once
"""
def load_images():

    piece_scale = int(SQ_size * 0.95)

    pieces = ["wP", "wR", "wN", "wB","wK", "wQ", "bP", "bR","bN","bB","bK", "bQ"]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"),
            (piece_scale, piece_scale))
    #We can access an image by saying 'IMAGES['wP]'


"""
this will be our game driver that will handle user input and updating graphics
"""
def main():

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))  # No border, just the board size
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    moveLogFont = p.font.SysFont("Helvitca", 28, True, False)

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()

    animate = False #flag variable
    moveMade = False #flag variable for when a move is made

    print(gs.board)
    load_images() #only do it once
    sqSelected = () #at first no square selected
    playerClicks = [] # keep track at clicks
    running = True
    gameOver = False

    playerOne = True # if human white = true
    playerTwo = False # same as above but for black

    strategy = NegaMaxStrategy()
    AIMove = strategy.findMove(gs, validMoves)

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0] // SQ_size
                    row = location[1] // SQ_size
                    if sqSelected == (row, col) or col >= 8:  # the user clicked the same square twice or user clicked mouse log
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks

                    else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected) #append for both
                    if len(playerClicks) == 2: #after 2nd click
                         move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                         print(move.getChessNotation())
                         for i in range(len(validMoves)):
                            if move == (validMoves[i]):
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    animate = True
                                    sqSelected = () #reset user clicks
                                    playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]  # only keep the second click

            #key handler
            elif e.type == p.KEYDOWN:

                if e.key == p.K_z:  # undo is on z
                    gs.undoMove()  # undo player move
                    if not humanTurn:
                        gs.undoMove()  # undo AI move too
                    moveMade = True
                    animate = False
                    gameOver = False

                if e.key == p.K_z:  # undo is on z
                    gs.undoMove()  # undo last move (assumed to be player's move or AI)

                    # Recalculate who is supposed to move now
                    humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

                    if not humanTurn:
                        gs.undoMove()  # undo AI's move too

                    moveMade = True
                    animate = False
                    gameOver = False

        if not gameOver and not humanTurn:
            AIMove = strategy.findMove(gs, validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True



        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        drawMoveLog(screen, gs, moveLogFont)

        # Game state check for checkmate or stalemate
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')

        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')


        clock.tick(MAX_FPS)
        p.display.flip()


"""
square highlight
"""
# Highlight square selected and moves for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_size, SQ_size))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_size, r * SQ_size))

            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_size, move.endRow * SQ_size))


"""
Responsible for all the graphics in the current game state
"""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


"""
draw the squares on the board
"""
def drawBoard(screen):
    global colors

    colors = [p.Color("light gray"), p.Color("dark green")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            square = p.Rect(c * SQ_size, r * SQ_size, SQ_size, SQ_size)  # No offset for border
            p.draw.rect(screen, color, square)


""""
will draw the pieces on the board
"""
def drawPieces(screen, board):

    piece_size = int(SQ_size * 0.9)

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                x = c * SQ_size + (SQ_size - piece_size) // 2
                y = r * SQ_size + (SQ_size - piece_size) // 2
                screen.blit(IMAGES[piece], p.Rect(x, y, piece_size, piece_size))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " "
        if i + 1 < len(moveLog):  # make sure black made a move
            moveString += moveLog[i + 1].getChessNotation()
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


"""
Animation
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount
        )
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_size, move.endRow * SQ_size, SQ_size, SQ_size)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_size, r * SQ_size, SQ_size, SQ_size))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)  # Customize font, size, and style
    textObject = font.render(text, 0, p.Color('Black'))  # Render the gray text
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH // 2 - textObject.get_width() // 2,
                                                                BOARD_HEIGHT // 2 - textObject.get_height() // 2)  # Center the text
    screen.blit(textObject, textLocation)  # Draw gray text

    textObject = font.render(text, 0, p.Color('Red'))  # Render black text
    screen.blit(textObject, textLocation.move(2, 2))  # Display black text with slight offset for shadow effect


if __name__ == "__main__":
    main()





