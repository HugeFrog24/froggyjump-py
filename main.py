import pygame
import random
import sys
import json
import argparse
import logging

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
LIGHT_BLUE = (135, 206, 250)  # Light blue color for the background
DARK_BROWN = (101, 67, 33)  # Dark brown color for the platforms

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Game variables
gravity = 0.5
jump_height = 10

platform_width = 100
platform_height = 20
platforms = []
high_score = 0
player_max_y = SCREEN_HEIGHT
passed_platforms = 0

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Character(pygame.sprite.Sprite):
    def __init__(self, size, pos, image_path):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        self.original_image = pygame.transform.scale(self.original_image, (size, size))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=pos)
        self.facing_right = False

    def update(self, x_change, y_change):
        self.rect.move_ip(x_change, y_change)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def flip_horizontally(self, direction):
        if direction == "right" and not self.facing_right:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.facing_right = True
        elif direction == "left" and self.facing_right:
            self.image = self.original_image
            self.facing_right = False

def load_localized_strings(language):
    try:
        with open(f"locales/{language}.json", "r", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Localization file not found for language: {language}")
        return {}
    
class Camera:
    def __init__(self, target):
        self.target = target
        self.offset_y = 0
        self.offset_smoothing = 0.05

    def update(self):
        target_offset_y = self.target.rect.centery - SCREEN_HEIGHT // 2
        self.offset_y += (target_offset_y - self.offset_y) * self.offset_smoothing

    def apply(self, obj):
        return obj.move(0, -self.offset_y)

def draw_platforms(camera):
    for platform in platforms:
        platform_rect = camera.apply(platform)
        pygame.draw.rect(screen, DARK_BROWN, platform_rect)

def jump(player):
    player.rect.y -= 1  # Move the player slightly off the platform
    player_y_change = -15  # Set the initial upward velocity
    return player_y_change

def add_platform():
    # Randomly add a new platform
    p_x = random.randint(0, SCREEN_WIDTH - platform_width)
    
    # Calculate the vertical distance between platforms based on a fixed value
    last_platform_y = platforms[-1].y
    vertical_distance = random.randint(80, 120)
    p_y = last_platform_y - vertical_distance
    
    platform_rect = pygame.Rect(p_x, p_y, platform_width, platform_height)
    platforms.append(platform_rect)

def game_over_screen(strings):
    font = pygame.font.Font(None, 36)
    text = font.render(strings.get("game_over", "Game Over"), True, (255, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)  # Wait for 2 seconds

def start_screen(strings):
    font = pygame.font.Font(None, 36)
    title_text = font.render(strings.get("title", "Frog Jump Game"), True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))

    instructions_text = strings.get("instructions", [])
    instructions_rects = []
    for i, text in enumerate(instructions_text):
        instruction = font.render(text, True, (0, 0, 0))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i*40))
        instructions_rects.append(instruction_rect)

    high_score_text = font.render(f"{strings.get('high_score', 'High Score')}: {high_score}", True, (0, 0, 0))
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + len(instructions_text)*40 + 40))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                
        screen.fill(LIGHT_BLUE)
        screen.blit(title_text, title_rect)
        for instruction, instruction_rect in zip(instructions_text, instructions_rects):
            screen.blit(font.render(instruction, True, (0, 0, 0)), instruction_rect)
        screen.blit(high_score_text, high_score_rect)

        screen.fill(LIGHT_BLUE)
        screen.blit(title_text, title_rect)
        for instruction, instruction_rect in zip(instructions_text, instructions_rects):
            screen.blit(font.render(instruction, True, (0, 0, 0)), instruction_rect)

        pygame.display.update()
        clock.tick(FPS)

class HighScoreLabel(pygame.sprite.Sprite):
    def __init__(self, x, y, font, color):
        super().__init__()
        self.font = font
        self.color = color
        self.score = 0
        self.x = x
        self.y = y
        self.update_text()

    def update_text(self):
        self.image = self.font.render(f"High Score: {self.score}", True, self.color)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_score(self, score):
        self.score = score
        self.update_text()

def game(strings):
    global platforms, high_score
    running = True
    score = 0
    passed_platforms = 0
    last_platform_jumped = None  # Initialize last_platform_jumped to None

    # Reset game state
    player = Character(80, [SCREEN_WIDTH//2, SCREEN_HEIGHT - 80], 'frog.png')
    player_x_change = 0
    player_y_change = 0
    platforms = [pygame.Rect(SCREEN_WIDTH//2 - platform_width//2, SCREEN_HEIGHT - platform_height, platform_width, platform_height)]

    camera = Camera(player)  # Create a camera instance

    # Create overlay elements
    font = pygame.font.Font(None, 36)
    high_score_label = HighScoreLabel(10, 10, font, (0, 0, 0))
    overlay_elements = pygame.sprite.Group(high_score_label)

    # Generate initial platforms
    while len(platforms) < 6:  # Adjust the number of initial platforms as needed
        add_platform()

    # Set player's starting position on the second platform
    player.rect.bottomleft = (SCREEN_WIDTH//2, platforms[1].top)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player_x_change = -5
                    player.flip_horizontally("left")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player_x_change = 5
                    player.flip_horizontally("right")
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_a or event.key == pygame.K_d:
                    player_x_change = 0

        screen.fill(LIGHT_BLUE)  # Fill the screen with light blue color

        # Update passed_platforms and high score only when the player jumps on a higher platform
        if last_platform_jumped is not None and player.rect.bottom <= last_platform_jumped.top:
            passed_platforms = max(passed_platforms, platforms.index(last_platform_jumped) + 1)
            score = passed_platforms
            if score > high_score:
                high_score = score
                high_score_label.update_score(high_score)

        # Gravity
        player_y_change += gravity
        player.update(player_x_change, player_y_change)

        # Keep the player within the screen boundaries
        if player.rect.left < 0:
            player.rect.left = 0
        elif player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        # Collision detection
        for platform in platforms:
            if player.rect.colliderect(platform):
                if player_y_change > 0:  # Check if the player is falling
                    player.rect.bottom = platform.top  # Adjust the player's position to be on top of the platform
                    player_y_change = jump(player)  # Make the character jump automatically when they fall onto a platform
                    
                    # Update last_platform_jumped only when jumping on a new higher platform
                    if last_platform_jumped is None or platform.top < last_platform_jumped.top:
                        last_platform_jumped = platform

        # Add new platforms when the player reaches a certain height relative to the camera's offset
        if player.rect.top < camera.offset_y + SCREEN_HEIGHT // 3:
            add_platform()

        # Remove platforms that are no longer visible on the screen
        platforms = [platform for platform in platforms if platform.bottom > camera.offset_y]

        # Update camera
        camera.update()

        # Draw the player and platforms
        player_rect = camera.apply(player.rect)
        screen.blit(player.image, player_rect)
        draw_platforms(camera)

        # Draw overlay elements
        overlay_elements.draw(screen)

        # Game over condition
        if player.rect.top > SCREEN_HEIGHT:
            logging.info("Game over")
            game_over_screen(strings)
            return  # Return to the start screen

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Frog Jump Game')
    parser.add_argument('-l', '--language', default='en', help='Language code (default: en)')
    args = parser.parse_args()

    language = args.language
    strings = load_localized_strings(language)
    while True:
        start_screen(strings)
        game(strings)
