import pygame
import random
import asyncio
import platform

pygame.init()
WIDTH, HEIGHT = 400, 400
TILE_SIZE = WIDTH // 4
MARGIN = 5
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Mini")
font = pygame.font.SysFont("Arial", 25)
clock = pygame.time.Clock()

#Colors
WHITE = (250, 248, 239)
YELLOW = (255, 255, 0)

THEMES = {
    "ocean": {
        "background": (0, 105, 148),
        "colors": {
            0: (50, 50, 50),
            2: (173, 216, 230),
            4: (135, 206, 235),
            8: (70, 130, 180),
            16: (65, 105, 225),
            32: (0, 191, 225),
            64: (0, 139, 139),
            128: (72, 209, 204),
            256: (0, 206, 209),
            512: (0, 178, 238),
            1024: (0, 154, 205),
            2048: (0, 128, 128)
        }
    },
    "forest": {
        "background" : (34, 139, 34),
        "colors" : {
            0: (50, 50, 50),
            2: (144, 238, 144),
            4: (124, 252, 0),
            8: (107, 142, 35),
            16: (154, 205, 50),
            32: (173, 255, 47),
            64: (85, 107, 47),
            128: (50, 205, 50),
            256: (60, 179, 113),
            512: (46, 139, 87),
            1024: (34, 100, 34),
            2048: (0, 100, 0)
        }
    },
    "space": {
        "background" : (25, 25, 112),
        "colors" : {
            0: (50, 50, 50),
            2: (147, 112, 219),
            4: (138, 43, 226),
            8: (148, 0, 211),
            16: (153, 50, 204),
            32: (186, 85, 211),
            64: (199, 21, 133),
            128: (218, 112, 214),
            256: (216, 191, 216),
            512: (221, 160, 221),
            1024: (238, 130, 238),
            2048: (255, 0, 255)
        }
    }
}

def create_grid():
    return [[0] * 4 for _ in range(4)]

def add_new_tile(grid):
    empty = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        if random.random() < 0.05:
            grid[r][c] = random.choices(["2*", "4*"], weights=[0.9, 0.1]) [0]
        else: 
            grid[r][c] = random.choices([2, 4], weights=[0.9, 0.1])[0]

def draw_grid(grid, theme):
    screen.fill(theme["background"])
    for r in range(4):
        for c in range(4):
            value = grid[r][c]
            is_powerup = isinstance(value, str) and value.endswith("*")
            base_value = int(value[:-1]) if is_powerup else value
            color = theme["colors"].get(base_value, (60, 58, 50))
            x = c * TILE_SIZE + MARGIN
            y = r * TILE_SIZE + MARGIN
            w = TILE_SIZE - 2 * MARGIN
            h = TILE_SIZE - 2 * MARGIN

            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)

            if is_powerup:
                pygame.draw.rect(screen, YELLOW, rect, 4)

            if value and base_value != 0:
                text_color = (0, 0, 0) if base_value < 8 else WHITE
                text = font.render(str(base_value), True, text_color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def draw_score (score, theme):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def compress_and_merge(row):
    new_row = []
    score = 0
    i = 0
    while i < len(row):
        if i + 1 < len(row) and row [i] != 0 and row [i + 1] != 0:
            val1 = row[i]
            val2 = row[i + 1]
            is_powerup1 = isinstance(val1, str) and val1.endswith("*")
            is_powerup2 = isinstance(val2, str) and val2.endswith("*")
            base1 = int(val1[:-1]) if is_powerup1 else val1
            base2 = int(val2[:-1]) if is_powerup2 else val2
            if base1 == base2:
                new_val = base1 * 2
                multiplier = 2 if is_powerup1 or is_powerup2 else 1
                new_row.append(new_val)
                score += new_val * multiplier
                i += 2
            else:
                new_row.append(val1)
                i += 1
        elif row[i] != 0:
            new_row.append(row[i])
            i += 1
        else:
            i += 1
    return new_row + [0] * (4 - len(new_row)), score

def rotate_grid(grid, times):
    for _ in range(times % 4):
        grid = [list(row) for row in zip (*grid[::-1])]
    return grid

def move(grid, direction):
    total_score = 0
    new_grid = [row[:] for row in grid]

    rotations = {"left": 0, "right": 2, "up": 3, "down": 1}
    new_grid = rotate_grid(new_grid, rotations[direction])
    for i in range(4):
        new_grid[i], score = compress_and_merge(new_grid[i])
        total_score += score
    new_grid = rotate_grid(new_grid, 4 - rotations[direction])
    return new_grid, total_score 

def is_game_over(grid):
    for r in range(4):
        for c in range(4):
            if grid[r][c] == 0:
                return False
            val = grid[r][c]
            base = int(val[:-1]) if isinstance(val, str) and val.endswith("*") else val
            if r < 3:
                next_val = grid[r + 1][c]
                next_base = int(next_val[:-1]) if isinstance(next_val, str) and next_val.endswith("*") else next_val
                if base == next_base:
                    return False
            if c < 3:
                next_val = grid[r][c + 1]
                next_base = int(next_val[:-1]) if isinstance(next_val, str) and next_val.endswith("*") else next_val
                if base == next_base:
                    return False
    return True

def has_won(grid):
    for row in grid:
        for val in row:
            base = int(val[:-1]) if isinstance(val, str) and val.endswith("*") else val
            if base == 2048:
                return True
    return False

def handle_input(grid, score):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                old_grid = [row[:] for row in grid]
                direction = {
                    pygame.K_LEFT : "left",
                    pygame.K_RIGHT : "right",
                    pygame.K_UP : "up",
                    pygame.K_DOWN : "down"
                }[event.key]
                grid, gained = move(grid, direction)
                score += gained
                if grid != old_grid:
                    add_new_tile(grid)
            elif event.key == pygame.K_r and (is_game_over(grid) or has_won(grid)):
                return create_grid(), 0, True
    return grid, score, False

async def main():
    current_theme = random.choice(list(THEMES.values()))
    grid = create_grid()
    score = 0
    add_new_tile(grid)
    add_new_tile(grid)

    while True:
        grid, score, reset = handle_input(grid, score)
        if reset:
            current_theme = random.choice(list(THEMES.values()))
            grid = create_grid()
            score = 0
            add_new_tile(grid)
            add_new_tile(grid)

        draw_grid(grid, current_theme)
        draw_score(score, current_theme)

        if has_won(grid):
            text = font.render("You WIn! Press R to restart", True, WHITE)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT//2)))
        elif is_game_over(grid):
            text = font.render("Game Over! Press R to restart", True, WHITE)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT//2)))

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
