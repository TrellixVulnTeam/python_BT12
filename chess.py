from random import choice
from typing import Any

import pygame
import pygame.freetype  # Import the freetype module.

BLACK = "B"
WHITE = "W"
DIRECTIONS = {WHITE: 1, BLACK: -1}
PAWN_RANK = {WHITE: 1, BLACK: 6}
OPPONENT = {WHITE: BLACK, BLACK: WHITE}
KING = "K"
QUEEN = "Q"
KNIGHT = "N"
ROOK = "R"
BISHOP = "B"
PAWN = "P"
PAWN_PROMOTE_RANK = {WHITE: 7, BLACK: 0}

VALUE = {QUEEN: 8, BISHOP: 7, KNIGHT: 6, ROOK: 5, PAWN: 4}


class Piece:
    def __init__(self, color, piece):
        self.color = color
        self.piece = piece

    def __str__(self):
        return self.color + self.piece

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def can_move(self, coordinate_from, coordinate_to, board):
        return True

    def can_attack(self, coordinate_from, coordinate_to, board):
        return self.can_move(coordinate_from, coordinate_to, board)


def get_sign_diff(start, end):
    if start == end:
        return 0
    if start > end:
        return -1
    return 1


def is_diagonal(start, end):
    rank_delta = abs(start.rank - end.rank)
    file_delta = abs(start.file - end.file)
    return rank_delta == file_delta and not (rank_delta == 0 and file_delta == 0)


def is_horizontal_or_vertical(start, end):
    rank_delta = start.rank - end.rank
    file_delta = start.file - end.file
    return rank_delta == 0 or file_delta == 0 and not (rank_delta == 0 and file_delta == 0)


class King(Piece):
    def __init__(self, color):
        super().__init__(color, KING)

    def can_move(self, coordinate_from, coordinate_to, board):
        rank_delta = abs(coordinate_from.rank - coordinate_to.rank)
        file_delta = abs(coordinate_from.file - coordinate_to.file)
        return (rank_delta == 1 and file_delta == 1) or \
               (rank_delta == 0 and file_delta == 1) or \
               (rank_delta == 1 and file_delta == 0)


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, PAWN)

    def can_move(self, coordinate_from, coordinate_to, board):
        rank_delta = coordinate_to.rank - coordinate_from.rank
        file_delta = coordinate_to.file - coordinate_from.file
        direction = DIRECTIONS[self.color]
        if file_delta == 0:
            if PAWN_RANK[self.color] == coordinate_from.rank:
                all_empty = board.all_empty(coordinate_from, coordinate_to)
                return rank_delta == direction or (all_empty and rank_delta == 2 * direction)
            else:
                return rank_delta == direction
        return False

    def can_attack(self, coordinate_from, coordinate_to, board):
        rank_delta = coordinate_to.rank - coordinate_from.rank
        file_delta = abs(coordinate_to.file - coordinate_from.file)
        direction = DIRECTIONS[self.color]
        return file_delta == 1 and rank_delta == direction


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, ROOK)

    def can_move(self, coordinate_from, coordinate_to, board):
        return is_horizontal_or_vertical(coordinate_from, coordinate_to) and \
               board.all_empty(coordinate_from, coordinate_to)


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, KNIGHT)

    def can_move(self, coordinate_from, coordinate_to, board):
        rank_delta = abs(coordinate_from.rank - coordinate_to.rank)
        file_delta = abs(coordinate_from.file - coordinate_to.file)
        return (rank_delta == 1 and file_delta == 2) or (rank_delta == 2 and file_delta == 1)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, BISHOP)

    def can_move(self, coordinate_from, coordinate_to, board):
        return is_diagonal(coordinate_from, coordinate_to) and \
               board.all_empty(coordinate_from, coordinate_to)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, QUEEN)

    def can_move(self, coordinate_from, coordinate_to, board):
        return (is_horizontal_or_vertical(coordinate_from, coordinate_to) or
                is_diagonal(coordinate_from, coordinate_to)) and \
               board.all_empty(coordinate_from, coordinate_to)


FILES = "abcdefgh"
RANKS = "12345678"


class Coordinate:
    def __init__(self, rank, file):
        self.rank = rank
        self.file = file

    def __str__(self):
        return FILES[self.file] + RANKS[self.rank]

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    @classmethod
    def at(cls, algebraic):
        rank = int(algebraic[1]) - 1
        file = FILES.find(algebraic[0])
        return cls(rank, file)


def get_coordinates(start, end):
    rank_start = start.rank
    rank_end = end.rank
    file_start = start.file
    file_end = end.file
    rank_sign = get_sign_diff(rank_start, rank_end)
    file_sign = get_sign_diff(file_start, file_end)
    rank_diff = abs(rank_start - rank_end)
    file_diff = abs(file_start - file_end)
    num_squares = max(rank_diff, file_diff) - 1
    rank = rank_start
    file = file_start
    coordinates = []
    for square in range(num_squares):
        rank = rank + rank_sign
        file = file + file_sign
        coordinates.append(Coordinate(rank, file))
    return coordinates


class Board:
    def __init__(self, piece_map=None):
        if piece_map is None:
            self.piece_map = {}
        else:
            self.piece_map = piece_map.copy()

    def __copy__(self):
        board = Board()
        board.piece_map = self.piece_map.copy()
        return board

    def __str__(self):
        result = ""
        for rank in range(7, -1, -1):
            row = ""
            for file in range(8):
                piece = self.get_piece_at(Coordinate(rank, file))
                if piece is None:
                    row = row + "   "
                else:
                    row = row + str(piece) + " "
            result = result + "\n" + row
        return result

    def find_piece(self, piece):
        for coordinate in self.piece_map:
            if piece == self.piece_map[coordinate]:
                return coordinate
        return None

    def king_in_check(self, color):
        coordinate_king = self.find_piece(King(color))
        if coordinate_king is not None:
            for coordinate in self.piece_map:
                piece = self.piece_map[coordinate]
                if piece.color != color:
                    if piece.can_attack(coordinate, coordinate_king, self):
                        return True
        return False

    def put_piece(self, coordinate, piece):
        self.piece_map[coordinate] = piece

    def initialize(self):
        rank = 1
        for file in range(8):
            self.piece_map[Coordinate(rank, file)] = Pawn(WHITE)
        self.piece_map[Coordinate(0, 0)] = Rook(WHITE)
        self.piece_map[Coordinate(0, 7)] = Rook(WHITE)
        self.piece_map[Coordinate(0, 1)] = Knight(WHITE)
        self.piece_map[Coordinate(0, 6)] = Knight(WHITE)
        self.piece_map[Coordinate(0, 2)] = Bishop(WHITE)
        self.piece_map[Coordinate(0, 5)] = Bishop(WHITE)
        self.piece_map[Coordinate(0, 3)] = Queen(WHITE)
        self.piece_map[Coordinate(0, 4)] = King(WHITE)
        rank = 6
        for file in range(8):
            self.piece_map[Coordinate(rank, file)] = Pawn(BLACK)
        self.piece_map[Coordinate(7, 0)] = Rook(BLACK)
        self.piece_map[Coordinate(7, 7)] = Rook(BLACK)
        self.piece_map[Coordinate(7, 1)] = Knight(BLACK)
        self.piece_map[Coordinate(7, 6)] = Knight(BLACK)
        self.piece_map[Coordinate(7, 2)] = Bishop(BLACK)
        self.piece_map[Coordinate(7, 5)] = Bishop(BLACK)
        self.piece_map[Coordinate(7, 3)] = Queen(BLACK)
        self.piece_map[Coordinate(7, 4)] = King(BLACK)

    def all_empty(self, start, end):
        coordinates = get_coordinates(start, end)
        for coordinate in coordinates:
            if self.piece_map.get(coordinate) is not None:
                return False
        return True

    def get_piece_at(self, coordinate):
        return self.piece_map.get(coordinate)

    def get_not_empty(self, color):
        coordinates = []
        for rank in range(8):
            for file in range(8):
                coordinate = Coordinate(rank, file)
                piece = self.piece_map.get(coordinate)
                if piece is not None and piece.color == color:
                    coordinates.append(coordinate)
        return coordinates

    def get_pieces_count(self):
        coordinates = []
        for rank in range(8):
            for file in range(8):
                coordinate = Coordinate(rank, file)
                piece = self.piece_map.get(coordinate)
                if piece is not None:
                    coordinates.append(coordinate)
        return len(coordinates)

    def get_empty(self):
        coordinates = []
        for rank in range(8):
            for file in range(8):
                coordinate = Coordinate(rank, file)
                if self.piece_map.get(coordinate) is None:
                    coordinates.append(coordinate)
        return coordinates

    def move(self, coordinate_from, coordinate_to):
        new_board = self.__copy__()
        piece = new_board.piece_map[coordinate_from]
        piece_to_replace = new_board.piece_map[coordinate_from]
        if piece.piece == PAWN and coordinate_to.rank == PAWN_PROMOTE_RANK[piece.color]:
            piece_to_replace = Queen(piece.color)
        new_board.piece_map[coordinate_to] = piece_to_replace
        new_board.piece_map.pop(coordinate_from)
        return new_board

    def get_moves(self, my_coordinates, blank_coordinates, color):
        moves = []
        for blank_coordinate in blank_coordinates:
            for my_coordinate in my_coordinates:
                my_piece = self.get_piece_at(my_coordinate)
                if my_piece.can_move(my_coordinate, blank_coordinate, self):
                    move = Move(my_coordinate, blank_coordinate, self)
                    if not move.in_check[color]:
                        moves.append(move)
        return moves

    def get_captures(self, my_coordinates, others_coordinates, color):
        moves = []
        for other_coordinate in others_coordinates:
            for my_coordinate in my_coordinates:
                my_piece = self.get_piece_at(my_coordinate)
                if my_piece.can_attack(my_coordinate, other_coordinate, self):
                    move = Move(my_coordinate, other_coordinate, self)
                    if not move.in_check[color]:
                        moves.append(move)
        return moves

    def remove_king(self, others_coordinates):
        for coordinate in others_coordinates:
            if self.get_piece_at(coordinate).piece == KING:
                others_coordinates.remove(coordinate)
                break

    def any_moves(self, color):
        opponent = OPPONENT[color]
        others_coordinates = self.get_not_empty(opponent)
        self.remove_king(others_coordinates)
        empty_coordinates = self.get_empty()
        my_coordinates = self.get_not_empty(color)
        captures = self.get_captures(my_coordinates, others_coordinates, color)
        if len(captures) > 0:
            return True
        non_captures = self.get_moves(my_coordinates, empty_coordinates, color)
        return len(non_captures) > 0


def value_captured(move):
    if move.captured is None:
        return 0
    else:
        return VALUE[move.captured.piece]


class Move:
    def __init__(self, coordinate_from, coordinate_to, board_before):
        self.coordinate_to = coordinate_to
        self.coordinate_from = coordinate_from
        self.board_before = board_before
        self.board_after = board_before.move(coordinate_from, coordinate_to)
        self.in_check = {BLACK: self.board_after.king_in_check(BLACK), WHITE: self.board_after.king_in_check(WHITE)}
        self.captured = self.board_before.get_piece_at(self.coordinate_to)

    def __str__(self):
        capture = ""
        if self.captured is not None:
            capture = "x"
        piece = self.board_before.get_piece_at(self.coordinate_from).piece
        if piece == PAWN:
            piece = ""
        return piece + capture + str(self.coordinate_to)


def get_check_moves(moves, color):
    check_moves = []
    for move in moves:
        if move.in_check[OPPONENT[color]]:
            check_moves.append(move)
    return check_moves


def get_check_mate_moves(check_moves, color):
    check_mate_moves = []
    if len(check_moves) > 1:
        for move in check_moves:
            if not move.board_after.any_moves(OPPONENT[color]):
                check_mate_moves.append(move)
    return check_mate_moves


def get_best_move_captured(moves):
    if len(moves) == 1:
        return moves[0]
    moves.sort(key=value_captured)
    moves.reverse()
    return moves[0]


def get_best_move_non_captured(moves):
    return choice(moves)


class Game:
    def __init__(self, board=None):
        if board is None:
            self.board = Board()
            self.board.initialize()
        else:
            self.board = board.__copy__()

    def next_move(self, color):
        opponent = OPPONENT[color]
        others_coordinates = self.board.get_not_empty(opponent)
        self.board.remove_king(others_coordinates)
        empty_coordinates = self.board.get_empty()
        my_coordinates = self.board.get_not_empty(color)
        captures = self.board.get_captures(my_coordinates, others_coordinates, color)
        non_captures = self.board.get_moves(my_coordinates, empty_coordinates, color)
        check_moves = get_check_moves(captures + non_captures, color)
        check_mate_moves = get_check_mate_moves(check_moves, color)
        move = None
        if len(check_mate_moves) > 0:
            move = check_mate_moves[0]
        if move is None and len(check_moves) > 0:
            move = check_moves[0]
        if move is None and len(captures) > 0:
            move = get_best_move_captured(captures)
        if move is None and len(non_captures) > 0:
            move = get_best_move_non_captured(non_captures)
        if move is not None:
            self.board = self.board.move(move.coordinate_from, move.coordinate_to)
        return move

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def pieces_left(self):
        pass


def play_game():
    game = Game()
    color = WHITE
    moves = []
    for i in range(300):
        move = game.next_move(color)
        if move is None:
            print("no move found")
            break
        if game.pieces_left() == 2:
            print("Only kings left")
            break
        moves.append(move)
        color = OPPONENT[color]
        print(str(i)+": "+str(move))
        print(str(game.board))
        print("-------------------------------------")
    print("game over")
    return moves


# Simple pygame program

# Import and initialize the pygame library


def thingy():
    moves = play_game()
    pygame.init()
    piece_size = 80
    # Set up the drawing window
    screen = pygame.display.set_mode([piece_size * 8, piece_size * 8])
    pygame.font.init()
    font = pygame.font.Font('freesansbold.ttf', 32)

    pieces = [KING, QUEEN, ROOK, KNIGHT, PAWN, QUEEN, BISHOP]
    blacks = {}
    whites = {}

    for piece in pieces:
        text = font.render(piece, True, pygame.Color(0, 0, 0), None)
        blacks[piece] = text
        text = font.render(piece, True, pygame.Color(255, 255, 255), None)
        whites[piece] = text
    # Run until the user asks to quit
    move_index = 0
    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_index = max(0, move_index - 1)
                if event.key == pygame.K_RIGHT:
                    move_index = min(len(moves) - 1, move_index + 1)
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with white
        screen.fill((180, 180, 180))

        # Draw a solid blue circle in the center
        square = 0
        board = moves[move_index].board_before
        for rank in range(0, 8):
            for file in range(0, 8):
                color_square = None
                coordinate = Coordinate(7 - rank, file)
                piece = board.get_piece_at(coordinate)
                if move_index != 0:
                    if piece != moves[move_index - 1].board_before.get_piece_at(coordinate):
                        color_square = pygame.Color(0, 127, 0)
                if color_square is None and (square % 2 == 1):
                    color_square = pygame.Color(60, 60, 60)

                if color_square is not None:
                    pygame.draw.rect(screen,
                                     color_square,
                                     pygame.Rect(file * piece_size, rank * piece_size, piece_size, piece_size))
                if piece is not None:
                    rect = whites[piece.piece].get_rect()
                    width_offset = (piece_size - rect.width) / 2
                    height_offset = (piece_size - rect.height) / 2
                    location = (file * piece_size + width_offset, rank * piece_size + height_offset)
                    if piece.color == WHITE:
                        screen.blit(whites[piece.piece], location)
                    else:
                        screen.blit(blacks[piece.piece], location)
                square = square + 1
            square = square + 1

        # Flip the display
        pygame.display.flip()

    # Done! Time to quit.
    pygame.quit()


if __name__ == '__main__':
    thingy()
