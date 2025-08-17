import os
os.environ["SDL_VIDEODRIVER"] = "dummy"  # Critical for Render.com
import pygame
import sys
import math
import os
import random
from collections import deque
from pygame import mixer

# Initialize pygame and mixer
pygame.init()
mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 900
BOARD_SIZE = 3
CELL_SIZE = 200
LINE_WIDTH = 8
O_COLOR = (30, 144, 255)  # Dodger Blue
X_COLOR = (220, 20, 60)   # Crimson
LINE_COLOR = (50, 50, 50)  # Dark Gray
BG_COLOR = (245, 245, 245)  # Off-white
TEXT_COLOR = (50, 50, 50)  # Dark Gray
BUTTON_COLOR = (46, 204, 113)  # Emerald Green
REMOVE_COLOR = (241, 196, 15)  # Sunflower Yellow
HOVER_COLOR = (52, 152, 219)  # Peter River Blue

# Load sounds
try:
    click_sound = mixer.Sound('click.wav')
    win_sound = mixer.Sound('win.wav')
    draw_sound = mixer.Sound('draw.wav')
except:
    # Create silent dummy sounds if files not found
    click_sound = mixer.Sound(buffer=bytearray(44))
    win_sound = mixer.Sound(buffer=bytearray(44))
    draw_sound = mixer.Sound(buffer=bytearray(44))

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic-Tac-Toe AI")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 48)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = pygame.math.Vector2(5, 5)
        self.velocity = pygame.math.Vector2(
            (random.random() - 0.5) * 5,
            (random.random() - 0.5) * 5
        )
        self.lifetime = 30
        
    def update(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.lifetime -= 1
        self.size.x = max(0, self.size.x - 0.1)
        self.size.y = max(0, self.size.y - 0.1)
        
    def draw(self, surface):
        alpha = min(255, self.lifetime * 8)
        color = (*self.color[:3], alpha)
        pygame.draw.rect(surface, color, (self.x, self.y, self.size.x, self.size.y))

class TicTacToe:
    def __init__(self):
        self.reset_game()
        self.particles = []
        self.animation_time = 0
        self.win_line = None
    
    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.x_moves = deque()
        self.o_moves = deque()
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.move_to_remove = None
        self.win_line = None
        self.particles = []
    
    def add_particles(self, x, y, color):
        for _ in range(20):
            self.particles.append(Particle(x, y, color))
    
    def make_move(self, row, col):
        if self.game_over or self.board[row][col] is not None:
            return False
            
        click_sound.play()
            
        if self.current_player == 'X':
            self.x_moves.append((row, col))
            if len(self.x_moves) > 3:
                self.move_to_remove = self.x_moves[0]
                pygame.time.delay(300)  # Show removal indicator
                old_row, old_col = self.x_moves.popleft()
                self.board[old_row][old_col] = None
                self.move_to_remove = None
        else:
            self.o_moves.append((row, col))
            if len(self.o_moves) > 3:
                self.move_to_remove = self.o_moves[0]
                pygame.time.delay(300)  # Show removal indicator
                old_row, old_col = self.o_moves.popleft()
                self.board[old_row][old_col] = None
                self.move_to_remove = None
                
        self.board[row][col] = self.current_player
        
        # Add particles for visual effect
        center_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2 + col * CELL_SIZE + CELL_SIZE // 2
        center_y = 120 + row * CELL_SIZE + CELL_SIZE // 2
        color = X_COLOR if self.current_player == 'X' else O_COLOR
        self.add_particles(center_x, center_y, color)
        
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
            win_sound.play()
            
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True
    
    def check_win(self, row, col):
        player = self.board[row][col]
        # Check row
        if all(cell == player for cell in self.board[row]):
            self.win_line = ('row', row)
            return True
        # Check column
        if all(self.board[i][col] == player for i in range(BOARD_SIZE)):
            self.win_line = ('col', col)
            return True
        # Check diagonals
        if row == col and all(self.board[i][i] == player for i in range(BOARD_SIZE)):
            self.win_line = ('diag', 1)
            return True
        if row + col == BOARD_SIZE - 1 and all(self.board[i][BOARD_SIZE-1-i] == player for i in range(BOARD_SIZE)):
            self.win_line = ('diag', 2)
            return True
        return False
    
    def get_ai_move(self):
        """Unbeatable minimax AI"""
        self.ai_thinking = True
        
        # If board is empty, start with center
        if all(cell is None for row in self.board for cell in row):
            return 1, 1
        
        best_score = -math.inf
        best_move = None
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] is None:
                    self.board[r][c] = 'O'
                    score = self.minimax(0, False)
                    self.board[r][c] = None
                    
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        
        self.ai_thinking = False
        return best_move
    
    def minimax(self, depth, is_maximizing):
        result = self.evaluate_board()
        if result is not None:
            return result
        
        if is_maximizing:
            best_score = -math.inf
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.board[r][c] is None:
                        self.board[r][c] = 'O'
                        score = self.minimax(depth + 1, False)
                        self.board[r][c] = None
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.board[r][c] is None:
                        self.board[r][c] = 'X'
                        score = self.minimax(depth + 1, True)
                        self.board[r][c] = None
                        best_score = min(score, best_score)
            return best_score
    
    def evaluate_board(self):
        # Check if O wins
        for r in range(BOARD_SIZE):
            if all(self.board[r][c] == 'O' for c in range(BOARD_SIZE)):
                return 1
            if all(self.board[c][r] == 'O' for c in range(BOARD_SIZE)):
                return 1
        
        if all(self.board[i][i] == 'O' for i in range(BOARD_SIZE)):
            return 1
        if all(self.board[i][BOARD_SIZE-1-i] == 'O' for i in range(BOARD_SIZE)):
            return 1
        
        # Check if X wins
        for r in range(BOARD_SIZE):
            if all(self.board[r][c] == 'X' for c in range(BOARD_SIZE)):
                return -1
            if all(self.board[c][r] == 'X' for c in range(BOARD_SIZE)):
                return -1
        
        if all(self.board[i][i] == 'X' for i in range(BOARD_SIZE)):
            return -1
        if all(self.board[i][BOARD_SIZE-1-i] == 'X' for i in range(BOARD_SIZE)):
            return -1
        
        # Check for tie
        if all(self.board[r][c] is not None for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
            return 0
        
        return None

def draw_button(text, x, y, width, height, color, hover_color, radius=10):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    
    # Check if mouse is hovering
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_rect, border_radius=radius)
    else:
        pygame.draw.rect(screen, color, button_rect, border_radius=radius)
    
    # Add subtle shadow
    shadow_rect = pygame.Rect(x+2, y+2, width, height)
    pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=radius)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

def draw_game(game):
    screen.fill(BG_COLOR)
    
    # Draw title
    title_text = title_font.render("Ultimate Tic-Tac-Toe", True, (44, 62, 80))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
    
    # Draw author info
    author_text = small_font.render("Created by: Maruf Hasan Bhuiyan", True, (127, 140, 141))
    screen.blit(author_text, (WIDTH//2 - author_text.get_width()//2, 70))
    
    contact_text = small_font.render("Contact: 01853308029", True, (127, 140, 141))
    screen.blit(contact_text, (WIDTH//2 - contact_text.get_width()//2, 95))
    
    # Draw grid with shadow effect
    board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
    board_y = 140
    
    # Grid shadow
    pygame.draw.rect(screen, (200, 200, 200), 
                    (board_x+5, board_y+5, BOARD_SIZE*CELL_SIZE, BOARD_SIZE*CELL_SIZE), 
                    border_radius=10)
    
    # Grid background
    pygame.draw.rect(screen, (255, 255, 255), 
                    (board_x, board_y, BOARD_SIZE*CELL_SIZE, BOARD_SIZE*CELL_SIZE), 
                    border_radius=10)
    
    # Grid lines
    for i in range(1, BOARD_SIZE):
        # Vertical lines
        pygame.draw.line(screen, LINE_COLOR, 
                        (board_x + i*CELL_SIZE, board_y + 5), 
                        (board_x + i*CELL_SIZE, board_y + BOARD_SIZE*CELL_SIZE - 5), 
                        LINE_WIDTH)
        # Horizontal lines
        pygame.draw.line(screen, LINE_COLOR, 
                        (board_x + 5, board_y + i*CELL_SIZE), 
                        (board_x + BOARD_SIZE*CELL_SIZE - 5, board_y + i*CELL_SIZE), 
                        LINE_WIDTH)
    
    # Draw X's and O's with removal indicators
    for (row, col), player in [(move, 'X') for move in game.x_moves] + [(move, 'O') for move in game.o_moves]:
        center_x = board_x + col * CELL_SIZE + CELL_SIZE // 2
        center_y = board_y + row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3
        
        # Highlight the move that will be removed
        if game.move_to_remove and game.move_to_remove == (row, col):
            pygame.draw.circle(screen, REMOVE_COLOR, (center_x, center_y), radius + 8, 4)
        
        if player == 'X':
            # Animated X
            if game.animation_time < 30:
                anim_factor = game.animation_time / 30
                pygame.draw.line(screen, X_COLOR, 
                                (center_x-radius*anim_factor, center_y-radius*anim_factor), 
                                (center_x+radius*anim_factor, center_y+radius*anim_factor), 
                                LINE_WIDTH+2)
                pygame.draw.line(screen, X_COLOR, 
                                (center_x-radius*anim_factor, center_y+radius*anim_factor), 
                                (center_x+radius*anim_factor, center_y-radius*anim_factor), 
                                LINE_WIDTH+2)
            else:
                pygame.draw.line(screen, X_COLOR, 
                                (center_x-radius, center_y-radius), 
                                (center_x+radius, center_y+radius), 
                                LINE_WIDTH+2)
                pygame.draw.line(screen, X_COLOR, 
                                (center_x-radius, center_y+radius), 
                                (center_x+radius, center_y-radius), 
                                LINE_WIDTH+2)
        else:
            # Animated O
            if game.animation_time < 30:
                anim_factor = game.animation_time / 30
                pygame.draw.circle(screen, O_COLOR, (center_x, center_y), radius*anim_factor, LINE_WIDTH+2)
            else:
                pygame.draw.circle(screen, O_COLOR, (center_x, center_y), radius, LINE_WIDTH+2)
        
        # Draw move numbers
        move_num = game.x_moves.index((row, col)) + 1 if player == 'X' else game.o_moves.index((row, col)) + 1
        num_text = small_font.render(str(move_num), True, TEXT_COLOR)
        screen.blit(num_text, (center_x - num_text.get_width()//2, center_y - num_text.get_height()//2))
    
    # Draw win line if game is over
    if game.win_line:
        line_type, index = game.win_line
        if line_type == 'row':
            y = board_y + index * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(screen, (0, 0, 0, 150), 
                            (board_x + 20, y), 
                            (board_x + BOARD_SIZE*CELL_SIZE - 20, y), 
                            LINE_WIDTH+4)
        elif line_type == 'col':
            x = board_x + index * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(screen, (0, 0, 0, 150), 
                            (x, board_y + 20), 
                            (x, board_y + BOARD_SIZE*CELL_SIZE - 20), 
                            LINE_WIDTH+4)
        elif line_type == 'diag' and index == 1:
            pygame.draw.line(screen, (0, 0, 0, 150), 
                            (board_x + 20, board_y + 20), 
                            (board_x + BOARD_SIZE*CELL_SIZE - 20, board_y + BOARD_SIZE*CELL_SIZE - 20), 
                            LINE_WIDTH+4)
        elif line_type == 'diag' and index == 2:
            pygame.draw.line(screen, (0, 0, 0, 150), 
                            (board_x + 20, board_y + BOARD_SIZE*CELL_SIZE - 20), 
                            (board_x + BOARD_SIZE*CELL_SIZE - 20, board_y + 20), 
                            LINE_WIDTH+4)
    
    # Draw particles
    for particle in game.particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.lifetime <= 0:
            game.particles.remove(particle)
    
    # Draw status
    status_y = board_y + BOARD_SIZE*CELL_SIZE + 30
    if game.game_over:
        if game.winner:
            status_text = f"Player {game.winner} wins!"
            # Add celebration particles
            if len(game.particles) < 100 and pygame.time.get_ticks() % 10 == 0:
                for _ in range(5):
                    game.add_particles(
                        random.randint(board_x, board_x + BOARD_SIZE*CELL_SIZE),
                        random.randint(board_y, board_y + BOARD_SIZE*CELL_SIZE),
                        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    )
        else:
            status_text = "It's a tie!"
            draw_sound.play()
    elif game.ai_thinking:
        status_text = "AI is thinking..."
    else:
        status_text = f"Player {game.current_player}'s turn"
    
    text = font.render(status_text, True, (44, 62, 80))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, status_y))
    
    # Draw move removal info
    if len(game.x_moves) == 3 and game.current_player == 'X':
        info_text = "Next X move will remove your oldest move (1)"
    elif len(game.o_moves) == 3 and game.current_player == 'O':
        info_text = "Next O move will remove oldest move (1)"
    else:
        info_text = ""
    
    if info_text:
        info_surf = small_font.render(info_text, True, (192, 57, 43))
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, status_y + 40))
    
    # Draw restart button
    button_rect = draw_button("Restart Game", WIDTH//2 - 100, HEIGHT - 100, 200, 50, BUTTON_COLOR, HOVER_COLOR)
    
    pygame.display.flip()
    return button_rect

def main():
    game = TicTacToe()
    clock = pygame.time.Clock()
    
    # Try to load background music
    try:
        mixer.music.load('background.mp3')
        mixer.music.set_volume(0.3)
        mixer.music.play(-1)  # Loop indefinitely
    except:
        pass
    
    while True:
        button_rect = draw_game(game)
        
        # Update animation time
        if game.animation_time < 30:
            game.animation_time += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = pygame.mouse.get_pos()
                    
                    # Check restart button click
                    if button_rect.collidepoint(x, y):
                        click_sound.play()
                        game.reset_game()
                        continue
                        
                    # Board click
                    board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
                    board_y = 140
                    if (board_x <= x < board_x + BOARD_SIZE*CELL_SIZE and 
                        board_y <= y < board_y + BOARD_SIZE*CELL_SIZE and 
                        not game.game_over and game.current_player == 'X'):
                        col = (x - board_x) // CELL_SIZE
                        row = (y - board_y) // CELL_SIZE
                        if game.make_move(row, col):
                            game.animation_time = 0
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    click_sound.play()
                    game.reset_game()
        
        # AI move
        if not game.game_over and game.current_player == 'O':
            row, col = game.get_ai_move()
            if row is not None:
                pygame.time.delay(300)  # Small delay for natural feel
                if game.make_move(row, col):
                    game.animation_time = 0
        
        clock.tick(60)

if __name__ == "__main__":
    main()