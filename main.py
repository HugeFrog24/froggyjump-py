import argparse
import json
import logging
import random
import sys
from typing import List, Optional, Tuple

import pygame

from camera import Camera
from character import Character
from constants import (FPS, GRAVITY, LIGHT_BLUE, PLATFORM_HEIGHT,
                       PLATFORM_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH)
from platform_sprite import Platform

# Initialize Pygame
pygame.init()

screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock: pygame.time.Clock = pygame.time.Clock()

platforms: List[Platform] = []
high_score: int = 0
player_max_y: int = SCREEN_HEIGHT
passed_platforms: int = 0

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_localized_strings(language: str) -> dict:
    try:
        with open(f"locales/{language}.json", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Localization file not found for language: {language}")
        return {}


def draw_platforms(camera: Camera) -> None:
    for platform in platforms:
        platform_rect: pygame.Rect = camera.apply(platform.rect)
        screen.blit(platform.image, platform_rect)


def jump(player: Character) -> int:
    player.rect.y -= 1  # Move the player slightly off the platform
    player_y_change: int = -15  # Set the initial upward velocity
    return player_y_change


def add_platform() -> None:
    # Randomly add a new platform
    p_x: int = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)

    # Calculate the vertical distance between platforms based on a fixed value
    last_platform_y: int = platforms[-1].rect.y
    vertical_distance: int = random.randint(150, 200)
    p_y: int = last_platform_y - vertical_distance

    platform: Platform = Platform(p_x, p_y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    platforms.append(platform)


def game_over_screen(strings: dict) -> None:
    font: pygame.font.Font = pygame.font.Font(None, 36)
    text: pygame.Surface = font.render(strings.get("game_over", "Game Over"), True, (255, 0, 0))
    text_rect: pygame.Rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)  # Wait for 2 seconds


def start_screen(strings: dict) -> None:
    font: pygame.font.Font = pygame.font.Font(None, 36)
    title_text: pygame.Surface = font.render(strings.get("title", "Frog Jump Game"), True, (0, 0, 0))
    title_rect: pygame.Rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    instructions_text: List[str] = strings.get("instructions", [])
    instructions_rects: List[pygame.Rect] = []
    for i, text in enumerate(instructions_text):
        instruction: pygame.Surface = font.render(text, True, (0, 0, 0))
        instruction_rect: pygame.Rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40))
        instructions_rects.append(instruction_rect)

    high_score_text: pygame.Surface = font.render(f"{strings.get('high_score', 'High Score')}: {high_score}", True, (0, 0, 0))
    high_score_rect: pygame.Rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + len(instructions_text) * 40 + 40))

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
        high_score_text = font.render(f"{strings.get('high_score', 'High Score')}: {high_score}", True, (0, 0, 0))  # Update high score text
        screen.blit(high_score_text, high_score_rect)

        pygame.display.update()
        clock.tick(FPS)


class HighScoreLabel(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int], high_score_text: str):
        super().__init__()
        self.font: pygame.font.Font = font
        self.color: Tuple[int, int, int] = color
        self.score: int = 0
        self.high_score_text: str = high_score_text
        self.x: int = x
        self.y: int = y
        self.update_text()

    def update_text(self) -> None:
        self.image: pygame.Surface = self.font.render(f"{self.high_score_text}: {self.score}", True, self.color)
        self.rect: pygame.Rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_score(self, score: int) -> None:
        self.score = score
        self.update_text()
        logging.info(f"New high score: {high_score}")


def game(strings: dict) -> None:
    global platforms, high_score
    running: bool = True
    score: int = 0
    passed_platforms: int = 0
    last_platform_jumped: Optional[Platform] = None  # Initialize last_platform_jumped to None

    # Reset game state
    player: Character = Character(80, [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80], 'frog.png')
    player_x_change: int = 0
    player_y_change: int = 0
    platforms = [Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, SCREEN_HEIGHT - PLATFORM_HEIGHT, PLATFORM_WIDTH, PLATFORM_HEIGHT)]

    camera: Camera = Camera(player)  # Create a camera instance

    # Create overlay elements
    font: pygame.font.Font = pygame.font.Font(None, 36)
    high_score_label: HighScoreLabel = HighScoreLabel(10, 10, font, (0, 0, 0), strings.get('high_score', 'High Score'))
    overlay_elements: pygame.sprite.Group = pygame.sprite.Group(high_score_label)

    # Generate initial platforms
    while len(platforms) < 6:  # Adjust the number of initial platforms as needed
        add_platform()

    # Set player's starting position on the second platform
    player.rect.bottomleft = (SCREEN_WIDTH // 2, platforms[1].rect.top)

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

        # Update passed_platforms and high score only when the player jumps on a new higher platform
        if last_platform_jumped is not None and player.rect.bottom <= last_platform_jumped.rect.top:
            highest_platform: Platform = max(platforms, key=lambda platform: platform.rect.top)
            if last_platform_jumped.rect.top < highest_platform.rect.top and not last_platform_jumped.passed:
                passed_platforms += 1
                last_platform_jumped.passed = True
                logging.info("You have passed a platform")
                score = passed_platforms
                if score > high_score:
                    high_score = score
                    high_score_label.update_score(high_score)

        # Gravity
        player_y_change += GRAVITY
        player.update(player_x_change, player_y_change, platforms)

        # Keep the player within the screen boundaries
        if player.rect.left < 0:
            player.rect.left = 0
        elif player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        # Collision detection
        for platform in platforms:
            if player.rect.colliderect(platform.rect):
                if player_y_change > 0:  # Check if the player is falling
                    player.rect.bottom = platform.rect.top  # Adjust the player's position to be on top of the platform
                    player_y_change = jump(player)  # Make the character jump automatically when they fall onto a platform

                    # Update last_platform_jumped only when jumping on a new higher platform
                    if last_platform_jumped is None or platform.rect.top < last_platform_jumped.rect.top:
                        last_platform_jumped = platform

        # Add new platforms when the player reaches a certain height relative to the camera's offset
        if player.rect.top < camera.offset_y + SCREEN_HEIGHT // 3:
            add_platform()

        # Remove platforms that are no longer visible on the screen
        platforms = [platform for platform in platforms if platform.rect.top < camera.offset_y + SCREEN_HEIGHT]

        # Update camera
        camera.update()

        # Draw the player and platforms
        player_rect: pygame.Rect = camera.apply(player.rect)
        screen.blit(player.image, player_rect)
        draw_platforms(camera)

        # Draw overlay elements
        overlay_elements.draw(screen)

        # Game over condition
        if player.rect.top > camera.offset_y + SCREEN_HEIGHT:
            logging.info("Game over")
            game_over_screen(strings)
            return  # Return to the start screen

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Frog Jump Game')
    parser.add_argument('-l', '--language', default='en', help='Language code (default: en)')
    args: argparse.Namespace = parser.parse_args()

    language: str = args.language
    strings: dict = load_localized_strings(language)
    while True:
        start_screen(strings)
        game(strings)
