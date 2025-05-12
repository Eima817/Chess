from abc import ABC, abstractmethod

# Strategy Interface
class MoveStrategy(ABC):
    def findMove(self, gs, validMoves):
        pass

class NegaMaxStrategy(MoveStrategy):
    CHECKMATE = 1000
    STALEMATE = 0
    DEPTH = 2

    def __init__(self):
        self.nextMove = None

    def findMove(self, gs, validMoves):
        self.nextMove = None
        self._negaMax(gs, validMoves, self.DEPTH, 1 if gs.whiteToMove else -1)
        return self.nextMove

    def _negaMax(self, gs, validMoves, depth, turnMultiplier):
        if depth == 0:
            return turnMultiplier * self._scoreBoard(gs)

        maxScore = -self.CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            score = -self._negaMax(gs, gs.getValidMoves(), depth - 1, -turnMultiplier)
            if score > maxScore:
                maxScore = score
                if depth == self.DEPTH:
                    self.nextMove = move
            gs.undoMove()
        return maxScore

    def _scoreBoard(self, gs):
        if gs.checkMate:
            return -self.CHECKMATE if gs.whiteToMove else self.CHECKMATE
        elif gs.staleMate:
            return self.STALEMATE
        return self._scoreMaterial(gs.board)

    def _scoreMaterial(self, board):
        pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
        score = 0
        for row in board:
            for square in row:
                if square[0] == 'w':
                    score += pieceScore[square[1]]
                elif square[0] == 'b':
                    score -= pieceScore[square[1]]
        return score
