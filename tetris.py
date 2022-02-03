import math
import random
from copy import deepcopy

import numpy as np
import pygame

ROTATE_LEFT = np.mat([[0, -1], [1, 0]])
ROTATE_RIGHT = np.mat([[0, 1], [-1, 0]])


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, coordinate):
        return Coordinate(self.x + coordinate.x, self.y + coordinate.y)

    def rotate(self, rotation_matrix):
        xy = np.mat([self.x, self.y]) * rotation_matrix
        return Coordinate(xy.tolist()[0][0], xy.tolist()[0][1])

    def rotate_left(self):
        return self.rotate(ROTATE_LEFT)

    def rotate_right(self):
        return self.rotate(ROTATE_RIGHT)

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def copy(self):
        return Coordinate(self.x, self.y)

    def get_min(self, coord):
        return Coordinate(min(self.x, coord.x), min(self.y, coord.y))

    def get_max(self, coord):
        return Coordinate(max(self.x, coord.x), max(self.y, coord.y))


class Piece:
    def __init__(self, coordinates, x_size, y_size):
        self.coordinates = coordinates
        self.angle = 0
        self.center = Coordinate(0, 0)
        self.world_coordinates = []
        self.update_coordinates(x_size, y_size, [])

    def set_color(self, color):
        self.color = color

    def rotate_left(self, x_size, y_size, pieces):
        self.angle = self.angle - 1
        return self.update_coordinates(x_size, y_size, pieces)

    def rotate_right(self, x_size, y_size, pieces):
        self.angle = self.angle + 1
        return self.update_coordinates(x_size, y_size, pieces)

    def move_to(self, center, x_size, y_size, pieces):
        self.center = center
        return self.update_coordinates(x_size, y_size, pieces)

    def move_by(self, coord, x_size, y_size, pieces):
        self.center.x += coord.x
        self.center.y += coord.y
        return self.update_coordinates(x_size, y_size, pieces)

    def remove_all(self, world_y):
        removed = []
        removed_world = []
        for i in range(len(self.world_coordinates)):
            if self.world_coordinates[i].y == world_y:
                removed.append(self.coordinates[i])
                removed_world.append(self.world_coordinates[i])
        for coordinates in removed:
            self.coordinates.remove(coordinates)
        for coordinates in removed_world:
            self.world_coordinates.remove(coordinates)

    def update_coordinates(self, x_size, y_size, pieces):
        min_coordinate = Coordinate(10000, 10000)
        max_coordinate = Coordinate(-1000, -1000)
        translated_coordinates = []
        if self.angle < 0:
            self.angle += 4
        for i in range(len(self.coordinates)):
            translated_coordinates.append(self.coordinates[i].copy())
        for rotate in range(0, self.angle):
            for i in range(len(translated_coordinates)):
                translated_coordinates[i] = translated_coordinates[i].rotate_right()
        for i in range(len(translated_coordinates)):
            translated_coordinates[i] = translated_coordinates[i].move(self.center)
            min_coordinate = min_coordinate.get_min(translated_coordinates[i])
            max_coordinate = max_coordinate.get_max(translated_coordinates[i])

        xoffset = 0
        if min_coordinate.x < 0:
            xoffset = -min_coordinate.x
        else:
            if max_coordinate.x > x_size - 1:
                xoffset = (x_size - 1) - max_coordinate.x

        yoffset = 0
        if min_coordinate.y < 0:
            yoffset = -min_coordinate.y
        else:
            if max_coordinate.y > y_size - 1:
                yoffset = (y_size - 1) - max_coordinate.y

        self.center.x = self.center.x + xoffset
        self.center.y = self.center.y + yoffset
        for i in range(len(translated_coordinates)):
            translated_coordinates[i] = translated_coordinates[i].move(Coordinate(xoffset, yoffset))

        all_world_coordinates = set()
        for piece in pieces:
            all_world_coordinates = all_world_coordinates.union(set(piece.world_coordinates))
        all_world_coordinates = all_world_coordinates.difference(self.world_coordinates)
        colliding_coordinates = all_world_coordinates.intersection(translated_coordinates)
        if len(colliding_coordinates) == 0:
            if self.world_coordinates == translated_coordinates:
                return False
            self.world_coordinates = translated_coordinates
            return True
        else:
            self.center.x = self.center.x - xoffset
            self.center.y = self.center.y - yoffset
            return False


class Line(Piece):
    def __init__(self, x_size, y_size):
        super().__init__([Coordinate(-1, 0), Coordinate(0, 0), Coordinate(1, 0)], x_size, y_size)


class Tee(Piece):
    def __init__(self, x_size, y_size):
        super().__init__([Coordinate(-1, 0), Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)], x_size, y_size)


class Right(Piece):
    def __init__(self, x_size, y_size):
        super().__init__([Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)], x_size, y_size)


class Ess(Piece):
    def __init__(self, x_size, y_size):
        super().__init__([Coordinate(0, 0), Coordinate(1, 0), Coordinate(1, 1), Coordinate(0, -1)], x_size, y_size)


COLORS = ["red", "green", "blue", "magenta", "purple", "yellow"]


class PieceSpawner:

    def __init__(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size

    def __iter__(self):
        return self

    def __next__(self):
        which = random.randint(0, 4)
        piece = None
        if which == 0:
            piece = Tee(self.x_size, self.y_size)
        elif which == 1:
            piece = Line(self.x_size, self.y_size)
        elif which == 2:
            piece = Ess(self.x_size, self.y_size)
        else:
            piece = Right(self.x_size, self.y_size)
        piece.set_color(random.choice(COLORS))

        return piece


def get_xs_at_y(y, pieces):
    xs = set()
    for piece in pieces:
        for coordinate in piece.world_coordinates:
            if coordinate.y == y:
                xs = xs.union({coordinate.x})
    return xs


class Board:
    def __init__(self, x_size, y_size, pieces):
        self.x_size = x_size
        self.y_size = y_size
        self.pieces = pieces
        self.spawned_piece = None
        self.spawner = PieceSpawner(x_size, y_size)
        self.game_over = False

    def move_spawned_right(self):
        if self.spawned_piece is not None:
            self.spawned_piece.move_by(Coordinate(1, 0), self.x_size, self.y_size, self.pieces)

    def move_spawned_left(self):
        if self.spawned_piece is not None:
            self.spawned_piece.move_by(Coordinate(-1, 0), self.x_size, self.y_size, self.pieces)

    def rotate_spawned_right(self):
        if self.spawned_piece is not None:
            self.spawned_piece.rotate_right(self.x_size, self.y_size, self.pieces)

    def rotate_spawned_left(self):
        if self.spawned_piece is not None:
            self.spawned_piece.rotate_left(self.x_size, self.y_size, self.pieces)

    def move_once(self):
        if self.game_over:
            return
        current_gen = deepcopy(self.pieces)
        for piece in self.pieces:
            piece.move_by(Coordinate(0, 1), self.x_size, self.y_size, current_gen)
        if self.spawned_piece is not None:
            moved = self.spawned_piece.move_by(Coordinate(0, 1), self.x_size, self.y_size, self.pieces)
            if not moved:
                self.pieces.append(self.spawned_piece)
                if len(get_xs_at_y(0, self.pieces)):
                    self.game_over = True
                else:
                    self.spawned_piece = next(self.spawner)

    def clear_ys(self):
        current_gen = deepcopy(self.pieces)
        for y in range(self.y_size):
            xs = get_xs_at_y(y, current_gen)
            if len(xs) == self.x_size:
                for piece in self.pieces:
                    piece.remove_all(y)

    def start_moves(self):
        self.spawned_piece = next(self.spawner)


def thingy():
    x_size = 9
    y_size = 20
    piece_size = 20
    board = Board(x_size, y_size, [])
    pygame.init()

    screen = pygame.display.set_mode([piece_size * x_size, piece_size * y_size])

    running = True
    last_time = pygame.time.get_ticks()
    board.start_moves()
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    board.move_spawned_left()
                if event.key == pygame.K_RIGHT:
                    board.move_spawned_right()
                if event.key == pygame.K_UP:
                    board.rotate_spawned_right()
                if event.key == pygame.K_DOWN:
                    board.rotate_spawned_left()

            if event.type == pygame.QUIT:
                running = False

        this_time = pygame.time.get_ticks()
        time_divider = 250
        this_seconds = int(this_time / time_divider)
        last_seconds = int(last_time / time_divider)
        need_to_move = this_seconds != last_seconds
        if need_to_move:
            board.move_once()

        last_time = this_time
        # Fill the background with white
        screen.fill((180, 180, 180))

        for piece in board.pieces:
            draw_piece(piece, piece_size, screen)
        if board.spawned_piece is not None:
            draw_piece(board.spawned_piece, piece_size, screen)

        board.clear_ys()

        pygame.display.flip()

    # Done! Time to quit.
    pygame.quit()


def draw_piece(piece, piece_size, screen):
    coordinates = piece.world_coordinates
    color_square = pygame.Color(piece.color)
    for coordinate in coordinates:
        rect = pygame.Rect(coordinate.x * piece_size, coordinate.y * piece_size, piece_size, piece_size)
        pygame.draw.rect(screen,
                         color_square, rect)


if __name__ == '__main__':
    thingy()
