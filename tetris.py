import pygame 
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X = 50
GRID_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

class Tetromino:
    """Represents a Tetris piece (tetromino)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.choice(self.get_all_shapes())
        self.color = random.choice(COLORS)
        self.rotation = 0
    
    def get_all_shapes(self):
        """All possible tetromino shapes"""
        shapes = [
            # I
            [[[1, 1, 1, 1]]],
            # O
            [[[1, 1], [1, 1]]],
            # T
            [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
            # S
            [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
            # Z
            [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
            # J
            [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
            # L
            [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]]
        ]
        return shapes
    
    def get_current_shape(self):
        """Get current rotation of the tetromino"""
        return self.shape[self.rotation % len(self.shape)]
    
    def rotate(self):
        """Rotate tetromino clockwise"""
        self.rotation = (self.rotation + 1) % len(self.shape)

class TetrisBoard:
    """Manages the game board and game logic"""
    
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        
    def spawn_piece(self):
        """Spawn new tetromino"""
        self.current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        # Check game over
        if self.collides(self.current_piece):
            return False
        return True
    
    def collides(self, piece):
        """Check if piece collides with board or walls"""
        shape = piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = piece.x + x
                    board_y = piece.y + y
                    
                    if (board_x < 0 or board_x >= GRID_WIDTH or 
                        board_y >= GRID_HEIGHT or 
                        (board_y >= 0 and self.grid[board_y][board_x])):
                        return True
        return False
    
    def place_piece(self):
        """Place current piece on board"""
        shape = self.current_piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_piece.x + x
                    board_y = self.current_piece.y + y
                    if board_y >= 0:
                        self.grid[board_y][board_x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        if self.collides(self.current_piece):
            return False
        return True
    
    def clear_lines(self):
        """Clear completed lines"""
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0] * GRID_WIDTH)
            self.lines_cleared += 1
        
        # Update score and level
        self.score += len(lines_to_clear) ** 2 * 100 * self.level
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(50, 500 - (self.level - 1) * 30)
    
    def move_piece(self, dx, dy):
        """Move current piece"""
        old_x, old_y = self.current_piece.x, self.current_piece.y
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        if self.collides(self.current_piece):
            self.current_piece.x, self.current_piece.y = old_x, old_y
            return False
        return True
    
    def drop_piece(self):
        """Drop piece one row"""
        return self.move_piece(0, 1)
    
    def update(self, dt):
        """Update game logic"""
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            if not self.drop_piece():
                if not self.place_piece():
                    return False  # Game Over
                self.fall_time = 0
            else:
                self.fall_time = 0
        return True

class TetrisRenderer:
    """Handles all rendering"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw_grid(self, board):
        """Draw game grid"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_X + x * CELL_SIZE,
                    GRID_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, GRAY, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
                
                if board.grid[y][x]:
                    pygame.draw.rect(self.screen, board.grid[y][x], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_piece(self, piece):
        """Draw current piece"""
        if not piece:
            return
        shape = piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GRID_X + (piece.x + x) * CELL_SIZE,
                        GRID_Y + (piece.y + y) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_next_piece(self, board):
        """Draw next piece preview"""
        if not board.next_piece:
            return
        
        text = self.small_font.render("Next:", True, WHITE)
        self.screen.blit(text, (GRID_X + GRID_WIDTH * CELL_SIZE + 20, GRID_Y + 50))
        
        shape = board.next_piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GRID_X + GRID_WIDTH * CELL_SIZE + 25 + x * 25,
                        GRID_Y + 100 + y * 25,
                        20, 20
                    )
                    pygame.draw.rect(self.screen, board.next_piece.color, rect)
    
    def draw_ui(self, board):
        """Draw score, level, lines"""
        score_text = self.font.render(f"Score: {board.score}", True, WHITE)
        level_text = self.font.render(f"Level: {board.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {board.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (GRID_X + GRID_WIDTH * CELL_SIZE + 20, GRID_Y + 250))
        self.screen.blit(level_text, (GRID_X + GRID_WIDTH * CELL_SIZE + 20, GRID_Y + 300))
        self.screen.blit(lines_text, (GRID_X + GRID_WIDTH * CELL_SIZE + 20, GRID_Y + 350))
    
    def draw_all(self, board):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        # Instructions
        instructions = [
            "A/D or Left/Right: Move",
            "S or Down: Drop",
            "W or Up: Rotate",
            "SPACE: Hard Drop",
            "ESC: Quit"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (10, 10 + i * 25))
        
        self.draw_grid(board)
        self.draw_piece(board.current_piece)
        self.draw_next_piece(board)
        self.draw_ui(board)
        
        pygame.display.flip()

class TetrisGame:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.board = TetrisBoard()
        self.renderer = TetrisRenderer(self.screen)
        self.running = True
        self.game_over = False
        
        # Spawn first piece
        self.board.spawn_piece()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.restart()
                    continue
                
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.board.move_piece(-1, 0)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.board.move_piece(1, 0)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.board.drop_piece()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    old_rotation = self.board.current_piece.rotation
                    self.board.current_piece.rotate()
                    if self.board.collides(self.board.current_piece):
                        self.board.current_piece.rotation = old_rotation
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while self.board.drop_piece():
                        self.board.score += 2
    
    def restart(self):
        """Restart game"""
        self.board = TetrisBoard()
        self.board.spawn_piece()
        self.game_over = False
    
    def update(self, dt):
        """Update game"""
        if not self.game_over:
            if not self.board.update(dt):
                self.game_over = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60)
            
            self.handle_events()
            self.update(dt)
            self.renderer.draw_all(self.board)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = TetrisGame()
    game.run()