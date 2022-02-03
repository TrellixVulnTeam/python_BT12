from unittest import TestCase
from chess import Piece, BLACK, WHITE, Coordinate, Board, Pawn, Bishop, Queen, Rook, Knight, King, QUEEN, PAWN, Game


class TestPiece(TestCase):
    def test_move(self):
        piece = Piece(BLACK, "XXX")
        self.assertTrue(piece.can_move(Coordinate(0, 0), Coordinate(1, 1), Board()))

    def test_board(self):
        self.assertTrue(Board().all_empty(Coordinate(0, 0), Coordinate(7, 7)))

    def test_pawn(self):
        pawn = Pawn(BLACK)
        self.assertFalse(pawn.can_move(Coordinate(0, 0), Coordinate(1, 0), Board()))
        self.assertTrue(pawn.can_move(Coordinate(1, 0), Coordinate(0, 0), Board()))
        pawn = Pawn(WHITE)
        self.assertTrue(pawn.can_move(Coordinate(0, 0), Coordinate(1, 0), Board()))
        self.assertFalse(pawn.can_move(Coordinate(1, 0), Coordinate(0, 0), Board()))
        self.assertFalse(pawn.can_attack(Coordinate(0, 0), Coordinate(1, 0), Board()))
        self.assertTrue(pawn.can_attack(Coordinate(0, 0), Coordinate(1, 1), Board()))
        self.assertTrue(pawn.can_move(Coordinate(1, 0), Coordinate(3, 0), Board()))
        self.assertFalse(pawn.can_move(Coordinate(1, 0), Coordinate(4, 0), Board()))
        board = Board()
        board.initialize()
        board = board.move(Coordinate(0, 0), Coordinate(2, 0))
        self.assertTrue(board.get_piece_at(Coordinate(2, 0)).piece == "R")
        self.assertFalse(pawn.can_move(Coordinate(1, 0), Coordinate(3, 0), board))

    def test_pawn_capture(self):
        pawn = Pawn(WHITE)
        self.assertTrue(pawn.can_attack(Coordinate(1, 1), Coordinate(2, 2), Board()))
        self.assertTrue(pawn.can_attack(Coordinate(1, 1), Coordinate(2, 0), Board()))
        self.assertFalse(pawn.can_attack(Coordinate(0, 0), Coordinate(2, 1), Board()))

    def test_bishop(self):
        bishop = Bishop(BLACK)
        board = Board()
        self.assertTrue(bishop.can_move(Coordinate(0, 0), Coordinate(3, 3), board))
        self.assertFalse(bishop.can_move(Coordinate(0, 0), Coordinate(2, 3), board))
        self.assertTrue(bishop.can_move(Coordinate(3, 3), Coordinate(0, 0), board))
        board.initialize()
        self.assertFalse(bishop.can_move(Coordinate(0, 0), Coordinate(2, 2), board))

    def test_queen(self):
        queen = Queen(BLACK)
        board = Board()
        self.assertTrue(queen.can_move(Coordinate(0, 0), Coordinate(3, 3), board))
        self.assertFalse(queen.can_move(Coordinate(0, 0), Coordinate(2, 3), board))
        self.assertTrue(queen.can_move(Coordinate(3, 3), Coordinate(0, 0), board))
        self.assertTrue(queen.can_move(Coordinate(0, 0), Coordinate(3, 0), board))
        self.assertFalse(queen.can_move(Coordinate(0, 0), Coordinate(2, 3), board))
        self.assertTrue(queen.can_move(Coordinate(3, 0), Coordinate(0, 0), board))
        board.initialize()
        self.assertFalse(queen.can_move(Coordinate(0, 0), Coordinate(2, 2), board))
        self.assertFalse(queen.can_move(Coordinate(0, 0), Coordinate(2, 0), board))

    def test_rook(self):
        rook = Rook(BLACK)
        board = Board()
        self.assertFalse(rook.can_move(Coordinate(0, 0), Coordinate(2, 3), board))
        self.assertTrue(rook.can_move(Coordinate(0, 0), Coordinate(1, 0), board))
        self.assertTrue(rook.can_move(Coordinate(3, 0), Coordinate(0, 0), board))
        self.assertTrue(rook.can_move(Coordinate(0, 0), Coordinate(0, 3), board))
        self.assertTrue(rook.can_move(Coordinate(0, 3), Coordinate(0, 0), board))
        board.initialize()
        self.assertFalse(rook.can_move(Coordinate(0, 0), Coordinate(2, 0), board))

    def test_knight(self):
        knight = Knight(BLACK)
        board = Board()
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(2, 1), board))  # -1,-2
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(2, 5), board))  # -1 +2
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(4, 1), board))  # +1 -2
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(4, 5), board))  # +1 +2
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(1, 2), board))  # -2, -1
        self.assertTrue(knight.can_move(Coordinate(3, 3), Coordinate(1, 4), board))  # -2 +1

        board.initialize()
        self.assertTrue(knight.can_move(Coordinate(0, 0), Coordinate(2, 1), board))

    def test_find(self):
        board = Board()
        board.put_piece(Coordinate(0, 0), Rook(WHITE))
        board.put_piece(Coordinate(1, 0), King(BLACK))
        coordinate = board.find_piece(King(BLACK))
        self.assertTrue(coordinate == Coordinate(1, 0))

    def test_check(self):
        board = Board()
        board.put_piece(Coordinate(0, 0), Rook(WHITE))
        board.put_piece(Coordinate(7, 0), King(BLACK))
        self.assertTrue(board.king_in_check(BLACK))
        board.put_piece(Coordinate(0, 0), Bishop(WHITE))
        self.assertFalse(board.king_in_check(BLACK))
        board.put_piece(Coordinate(0, 0), Queen(WHITE))
        self.assertTrue(board.king_in_check(BLACK))
        board.put_piece(Coordinate(5, 0), Pawn(WHITE))
        self.assertFalse(board.king_in_check(BLACK))

    def test_move(self):
        board = Board()
        board.initialize()
        new_board = board.move(Coordinate(0, 0), Coordinate(2, 0))
        self.assertTrue(board.get_piece_at(Coordinate(0, 0)) is not None)
        self.assertTrue(new_board.get_piece_at(Coordinate(0, 0)) is None)

        board.initialize()
        board.put_piece(Coordinate(6, 0), Piece(WHITE, PAWN))
        new_board = board.move(Coordinate(6, 0), Coordinate(7, 0))
        self.assertTrue(new_board.get_piece_at(Coordinate(7, 0)) == Piece(WHITE, QUEEN))

    def test_game(self):
        piece_map = {Coordinate.at("d4"): Pawn(WHITE),
                     Coordinate.at("e6"): King(BLACK),
                     Coordinate.at("a1"): Pawn(WHITE),
                     Coordinate.at("b2"): Queen(BLACK)}
        board = Board(piece_map)
        game = Game(board)
        move = game.next_move(WHITE)
        self.assertTrue(move is not None)
        self.assertTrue(move.in_check[BLACK])

    def test_game_capture(self):
        piece_map = {Coordinate.at("d4"): Pawn(WHITE),
                     Coordinate.at("e6"): Rook(BLACK),
                     Coordinate.at("a1"): Pawn(WHITE),
                     Coordinate.at("b2"): Queen(BLACK)}
        board = Board(piece_map)
        game = Game(board)
        move = game.next_move(WHITE)
        self.assertTrue(move is not None)
        self.assertTrue(move.board_after.get_piece_at(Coordinate.at("b2")) == Pawn(WHITE))

    def test_game_check_mate(self):
        piece_map = {Coordinate.at("f8"): King(BLACK),
                     Coordinate.at("e8"): Rook(BLACK),
                     Coordinate.at("g7"): Pawn(BLACK),
                     Coordinate.at("f6"): Pawn(BLACK),
                     Coordinate.at("d5"): Bishop(WHITE),
                     Coordinate.at("f4"): Knight(WHITE),
                     Coordinate.at("g4"): Pawn(WHITE)}
        board = Board(piece_map)
        game = Game(board)
        move = game.next_move(WHITE)
        self.assertTrue(move is not None)
        self.assertTrue(str(move) == "Ng6")
        self.assertTrue(game.next_move(BLACK) is None)

    def test_game_check_mate2(self):
        piece_map = {Coordinate.at("h7"): King(BLACK),
                     Coordinate.at("g8"): Rook(BLACK),
                     Coordinate.at("f7"): Pawn(BLACK),
                     Coordinate.at("d4"): Rook(WHITE),
                     Coordinate.at("e5"): Knight(WHITE),
                     Coordinate.at("f6"): Pawn(WHITE)}

        board = Board(piece_map)
        game = Game(board)
        move = game.next_move(WHITE)
        self.assertTrue(move is not None)
        self.assertTrue(str(move) == "Rh4")
        self.assertTrue(game.next_move(BLACK) is None)
