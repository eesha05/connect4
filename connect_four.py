import math
import sys
import pygame

ROWS = 6
COLS = 7
CELL_SIZE = 90
RADIUS = CELL_SIZE // 2 - 7
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE
FPS = 60

EMPTY = 0
HUMAN = 1
AI = 2

BACKGROUND = (20, 28, 48)
BOARD_BLUE = (35, 95, 190)
EMPTY_COLOR = (235, 239, 245)
RED = (235, 70, 75)
YELLOW = (255, 205, 60)
WHITE = (255, 255, 255)
DARK = (30, 35, 45)
GREEN = (80, 210, 140)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four AI - Minimax")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28, bold=True)
small_font = pygame.font.SysFont("arial", 19)
title_font = pygame.font.SysFont("arial", 30, bold=True)


def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def valid_location(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY


def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def winning_move(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Positive diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False


def board_full(board):
    return all(board[0][c] != EMPTY for c in range(COLS))


def score_window(window, piece):
    opponent = HUMAN if piece == AI else AI
    score = 0

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 8
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 3

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 10

    return score


def evaluate_board(board, piece):
    score = 0

    
    center_col = [board[r][COLS // 2] for r in range(ROWS)]
    score += center_col.count(piece) * 6

  
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c + i] for i in range(4)]
            score += score_window(window, piece)

    
    for c in range(COLS):
        for r in range(ROWS - 3):
            window = [board[r + i][c] for i in range(4)]
            score += score_window(window, piece)

   
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += score_window(window, piece)

    
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += score_window(window, piece)

    return score


def get_valid_locations(board):
    return [c for c in range(COLS) if valid_location(board, c)]


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = (
        winning_move(board, HUMAN)
        or winning_move(board, AI)
        or len(valid_locations) == 0
    )

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, 10_000)
            if winning_move(board, HUMAN):
                return (None, -10_000)
            return (None, 0)
        return (None, evaluate_board(board, AI))

    
    valid_locations.sort(key=lambda c: abs(c - COLS // 2))

    if maximizing_player:
        value = -math.inf
        best_col = valid_locations[0]

        for col in valid_locations:
            row = get_next_open_row(board, col)
            board[row][col] = AI
            _, new_score = minimax(board, depth - 1, alpha, beta, False)
            board[row][col] = EMPTY

            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best_col, value

    value = math.inf
    best_col = valid_locations[0]

    for col in valid_locations:
        row = get_next_open_row(board, col)
        board[row][col] = HUMAN
        _, new_score = minimax(board, depth - 1, alpha, beta, True)
        board[row][col] = EMPTY

        if new_score < value:
            value = new_score
            best_col = col

        beta = min(beta, value)
        if alpha >= beta:
            break

    return best_col, value


def draw_board(board, message, hover_col=None):
    screen.fill(BACKGROUND)

    title = title_font.render("CONNECT FOUR AI", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    
    if hover_col is not None and message == "Your turn — click a column":
        pygame.draw.circle(
            screen, RED,
            (hover_col * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2 + 8),
            RADIUS
        )

    
    pygame.draw.rect(
        screen, BOARD_BLUE,
        (0, CELL_SIZE, WIDTH, ROWS * CELL_SIZE)
    )

    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE + CELL_SIZE // 2
            y = (r + 1) * CELL_SIZE + CELL_SIZE // 2
            piece = board[r][c]

            color = EMPTY_COLOR
            if piece == HUMAN:
                color = RED
            elif piece == AI:
                color = YELLOW

            pygame.draw.circle(screen, color, (x, y), RADIUS)

    status_color = GREEN if message.startswith("You win") else WHITE
    if message.startswith("AI wins"):
        status_color = YELLOW
    status = small_font.render(message, True, status_color)
    screen.blit(status, (WIDTH // 2 - status.get_width() // 2, HEIGHT - 28))

    pygame.display.flip()


def main():
    board = create_board()
    game_over = False
    human_turn = True
    message = "Your turn — click a column"
    hover_col = None
    search_depth = 4

    draw_board(board, message)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = create_board()
                    game_over = False
                    human_turn = True
                    message = "Your turn — click a column"
                    hover_col = None
                    draw_board(board, message)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEMOTION:
                x, _ = event.pos
                hover_col = max(0, min(COLS - 1, x // CELL_SIZE))
                if not game_over and human_turn:
                    draw_board(board, message, hover_col)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over or not human_turn:
                    continue

                col = event.pos[0] // CELL_SIZE
                if not valid_location(board, col):
                    message = "That column is full — choose another"
                    draw_board(board, message, hover_col)
                    continue

                row = get_next_open_row(board, col)
                drop_piece(board, row, col, HUMAN)

                if winning_move(board, HUMAN):
                    message = "You win! Press R to play again"
                    game_over = True
                elif board_full(board):
                    message = "Draw! Press R to play again"
                    game_over = True
                else:
                    human_turn = False
                    message = "AI is thinking..."
                    draw_board(board, message)

                    ai_col, _ = minimax(
                        board, search_depth,
                        -math.inf, math.inf, True
                    )

                    if ai_col is not None and valid_location(board, ai_col):
                        ai_row = get_next_open_row(board, ai_col)
                        drop_piece(board, ai_row, ai_col, AI)

                    if winning_move(board, AI):
                        message = "AI wins! Press R to play again"
                        game_over = True
                    elif board_full(board):
                        message = "Draw! Press R to play again"
                        game_over = True
                    else:
                        human_turn = True
                        message = "Your turn — click a column"

                draw_board(board, message, hover_col if human_turn else None)


if __name__ == "__main__":
    main()
