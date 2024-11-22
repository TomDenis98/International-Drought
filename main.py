import pygame
import numpy as np


class Checkerboard:
    def __init__(self, size=10, square_size=60):
        pygame.init()
        self.size = size
        self.square_size = square_size
        self.screen_width = size * square_size
        self.screen_height = size * square_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Checkerboard")
        self.clock = pygame.time.Clock()

        # Initialize board state and alternating pattern
        self.board_state = np.zeros((size, size), dtype=int)
        self.alternating_array = np.fromfunction(lambda i, j: (i + j) % 2, (size, size), dtype=int)

        # Example: place pieces on alternating dark squares
        self.board_state[1::2, ::2] = 1
        self.board_state[::2, 1::2] = 1

        # Dictionary to store piece positions (initial positions)
        self.piece_positions = {}

        # Initialize pieces for both players
        self.initialize_pieces()

        # Set initial player turn (Player 1 starts)
        self.current_player = 1
        self.selected_piece = None
        self.dragging_piece = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.move_made = False  # Flag to indicate if a move has been made

        self.running = True
        self.main_loop()

    def initialize_pieces(self):
        # Player 1 pieces
        for col in range(self.size):
            for row in range(4):
                if (col + row) % 2 == 1:
                    x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                    player_1_color = (255, 253, 208)  # cream color
                    self.piece_positions[(col, row)] = (x, y, player_1_color)

        # Player 2 pieces
        for col in range(self.size):
            for row in range(6, self.size):
                if (col + row) % 2 == 1:
                    x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                    player_2_color = (139, 69, 19)  # darker caramel color
                    self.piece_positions[(col, row)] = (x, y, player_2_color)

    def draw_board(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.alternating_array[i, j] == 0:
                    color = (245, 222, 179)  # beige
                else:
                    color = (0, 0, 0)  # black

                rect = pygame.Rect(j * self.square_size, i * self.square_size, self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        for pos, (x, y, color) in self.piece_positions.items():
            self.draw_piece(x, y, color)

    def draw_piece(self, x, y, color):
        radius = self.square_size // 2 - 5
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def convert_to_indices(self, x, y):
        col = x // self.square_size
        row = y // self.square_size
        return col, row

    def pieces_move(self, from_pos, to_pos):
        from_col, from_row = from_pos
        to_col, to_row = to_pos

        # Check if the move is diagonal and only one square away
        if abs(to_col - from_col) == 1 and abs(to_row - from_row) == 1:
            # Check if the destination position is within bounds and empty
            if 0 <= to_col < self.size and 0 <= to_row < self.size and (to_col, to_row) not in self.piece_positions:
                # Move the piece to the new position
                self.piece_positions[(to_col, to_row)] = (
                    to_col * self.square_size + self.square_size // 2,
                    to_row * self.square_size + self.square_size // 2,
                    self.piece_positions[from_pos][2]
                )

                # Remove the piece from the old position
                if from_pos in self.piece_positions:
                    self.piece_positions.pop(from_pos)

                self.move_made = True  # Mark that a move has been made
                return True

        # Check if the move is a valid capture
        elif abs(to_col - from_col) == 2 and abs(to_row - from_row) == 2:
            mid_col = (from_col + to_col) // 2
            mid_row = (from_row + to_row) // 2
            if (mid_col, mid_row) in self.piece_positions:
                if self.piece_positions[(mid_col, mid_row)][2] != self.piece_positions[from_pos][2]:
                    if 0 <= to_col < self.size and 0 <= to_row < self.size and (
                    to_col, to_row) not in self.piece_positions:
                        # Move the piece to the new position
                        self.piece_positions[(to_col, to_row)] = (
                            to_col * self.square_size + self.square_size // 2,
                            to_row * self.square_size + self.square_size // 2,
                            self.piece_positions[from_pos][2]
                        )
                        # Remove the captured piece
                        self.piece_positions.pop((mid_col, mid_row))
                        # Remove the piece from the old position
                        self.piece_positions.pop(from_pos)
                        self.move_made = True  # Mark that a move has been made

                        # Check for additional captures (mandatory captures in checkers)
                        if self.can_capture_more((to_col, to_row)):
                            return True  # Return True to keep the same player's turn

                        # If no more captures are possible, switch player turn
                        self.switch_player_turn()
                        return True

        return False

    def can_capture_more(self, from_pos):
        from_col, from_row = from_pos

        # Check all possible capture directions
        capture_directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        for direction in capture_directions:
            to_col = from_col + direction[0]
            to_row = from_row + direction[1]
            mid_col = from_col + direction[0] // 2
            mid_row = from_row + direction[1] // 2

            if 0 <= to_col < self.size and 0 <= to_row < self.size and (to_col, to_row) not in self.piece_positions:
                if (mid_col, mid_row) in self.piece_positions and self.piece_positions[(mid_col, mid_row)][2] != \
                        self.piece_positions[from_pos][2]:
                    return True

        return False

    def handle_mouse_down(self, pos):
        if not self.move_made:  # Only allow selection if no move has been made
            x, y = pos
            col, row = self.convert_to_indices(x, y)
            if (col, row) in self.piece_positions:
                _, _, piece_color = self.piece_positions[(col, row)]
                if (self.current_player == 1 and piece_color == (255, 253, 208)) or \
                        (self.current_player == 2 and piece_color == (139, 69, 19)):
                    self.selected_piece = (col, row)
                    self.dragging_piece = (col, row)
                    self.drag_offset_x = x - col * self.square_size
                    self.drag_offset_y = y - row * self.square_size

    def switch_player_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.move_made = False  # Reset move_made flag for the next player

    def handle_mouse_motion(self, pos):
        if self.dragging_piece is not None:
            x, y = pos
            # Restrict dragging piece to adjacent squares only
            col, row = self.convert_to_indices(x - self.drag_offset_x + self.square_size // 2,
                                               y - self.drag_offset_y + self.square_size // 2)
            if self.is_adjacent(self.dragging_piece, (col, row)):
                if self.alternating_array[row, col] == 1 and (
                        col, row) not in self.piece_positions:  # Ensure it's a black square and unoccupied
                    self.piece_positions[self.dragging_piece] = (col * self.square_size + self.square_size // 2,
                                                                 row * self.square_size + self.square_size // 2,
                                                                 self.piece_positions[self.dragging_piece][2])

    def is_adjacent(self, pos1, pos2):
        col1, row1 = pos1
        col2, row2 = pos2
        # Check if pos2 is directly adjacent to pos1
        return abs(col2 - col1) == 1 and abs(row2 - row1) == 1

    def handle_mouse_up(self, pos):
        if self.dragging_piece is not None:
            x, y = pos
            new_col, new_row = self.convert_to_indices(x - self.drag_offset_x + self.square_size // 2,
                                                       y - self.drag_offset_y + self.square_size // 2)

            # Attempt to move the piece
            if self.pieces_move(self.dragging_piece, (new_col, new_row)):
                if self.move_made:
                    # Switch player turn if a move has been made
                    self.switch_player_turn()

        self.dragging_piece = None
        self.selected_piece = None

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left mouse button
                        self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left mouse button
                        self.handle_mouse_up(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)

            self.screen.fill((0, 128, 0))  # green background
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            self.clock.tick(60)  # Cap at 60 FPS

        pygame.quit()


# Run the checkerboard game using Pygame
checkerboard_game = Checkerboard()
