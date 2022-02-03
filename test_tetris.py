from copy import copy, deepcopy
from unittest import TestCase
from tetris import Line, Coordinate, Board, Ess, Tee


class TestTetris(TestCase):

    def test_piece(self):
        line = Line(3, 5)
        ess = Ess(3, 5)
        line.move_to(Coordinate(1, 1), 3, 5, [line, ess])
        ess.move_to(Coordinate(2, 2), 3, 4, [line, ess])
        board = Board(3, 5, [line, ess])
        board.clear_ys()
        self.assertEqual(len(line.coordinates), 0)
        self.assertEqual(len(ess.coordinates), 4)

    def test_pieces(self):
        tee = Tee(3, 5)
        tee.move_to(Coordinate(1, 1), 3, 5, [])
        board = Board(3, 5, [tee])
        board.clear_ys()
        self.assertEqual(len(tee.coordinates), 1)

    def test_spawn(self):
        board = Board(3, 5, [])
        board.start_moves()
        self.assertEqual(len(board.pieces), 0)
        self.assertTrue(board.spawned_piece is not None)


class Thingy:
    def __init__(self, z, x):
        self.z = z
        self.x = x

    def __copy__(self):
        return Thingy(3, 4)

    def __str__(self):
        return str(self.z) + " " + str(self.x)

