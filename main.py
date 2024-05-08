import argparse
import json
import logging
import random
import sys
from typing import List, Optional

import pygame

from camera import Camera
from character import Character
from constants import (
    FPS,
    GRAVITY,
    LIGHT_BLUE,
    MAX_PLATFORM_DISTANCE,
    MIN_PLATFORM_DISTANCE,
    PLATFORM_HEIGHT,
    PLATFORM_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from high_score_label import HighScoreLabel
from platform_sprite import Platform
from world import World

# Initialize Pygame
pygame.init()

screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock: pygame.time.Clock = pygame.time.Clock()

platforms: List[Platform] = []
high_score: int = 0
player_max_y: int = SCREEN_HEIGHT
passed_platforms: int = 0

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("game.log"), logging.StreamHandler()],
)


def load_localized_strings(language: str) -> dict:
    # Load the default English strings first
    try:
        with open("locales/en.json", encoding="utf-8") as file:
            strings = json.load(file)
    except FileNotFoundError:
        logging.error("Default English localization file not found.")
        strings = {}  # Fallback to an empty dictionary if even the English file is missing

    # If the requested language is English, return immediately
    if language == "en":
        return strings

    # Try to load the requested language strings and update the dictionary
    try:
        with open(f"locales/{language}.json", encoding="utf-8") as file:
            localized_strings = json.load(file)
            strings.update(localized_strings)  # Update with localized strings
    except FileNotFoundError:
        logging.error(f"Localization file not found for language: {language}")
        # No return here, as we fall back to English

    return strings


def draw_platforms(camera: Camera) -> None:
    for platform in platforms:
        platform_rect: pygame.Rect = camera.apply(platform.rect)
        screen.blit(platform.image, platform_rect)


def add_platform(world: World) -> None:
    # Randomly add a new platform
    p_x: int = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)

    # Calculate the vertical distance between platforms based on the constants
    last_platform_y: int = world.platforms[-1].absolute_y if world.platforms else SCREEN_HEIGHT
    vertical_distance: int = random.randint(
        MIN_PLATFORM_DISTANCE, MAX_PLATFORM_DISTANCE
    )
    p_y: int = last_platform_y - vertical_distance

    platform: Platform = Platform(p_x, p_y, PLATFORM_WIDTH, PLATFORM_HEIGHT, absolute_y=p_y)
    world.add_platform(platform)


def game_over_screen(strings: dict) -> None:
    font: pygame.font.Font = pygame.font.Font(None, 36)
    text: pygame.Surface = font.render(
        strings.get("game_over"), True, (255, 0, 0)
    )
    text_rect: pygame.Rect = text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    )
    screen.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)  # Wait for 2 seconds
    pygame.event.clear()  # Clear the event queue


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        test_width = font.size(test_line)[0]
        if test_width > max_width:
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    lines.append(current_line)
    return lines


def start_screen(strings: dict) -> None:
    title_font: pygame.font.Font = pygame.font.Font(None, 48)
    title_text: pygame.Surface = title_font.render(
        strings.get("title"), True, (0, 0, 0)
    )
    title_rect: pygame.Rect = title_text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    )

    instructions_font: pygame.font.Font = pygame.font.Font(None, 24)
    instructions_text: List[str] = strings.get("instructions")
    instructions_rects: List[pygame.Rect] = []

    project_note_font: pygame.font.Font = pygame.font.Font(None, 18)
    project_note_text: str = strings.get("project_note")
    project_note_lines: List[str] = wrap_text(
        project_note_text, project_note_font, SCREEN_WIDTH - 40
    )
    project_note_rects: List[pygame.Rect] = []

    # Calculate the available vertical space for instructions
    available_space = (
        SCREEN_HEIGHT // 2 - title_rect.bottom - 40
    )  # Subtract additional space for high score label
    line_spacing = 10  # Adjust the line spacing as needed

    # Wrap instructions onto multiple lines if necessary
    wrapped_instructions = []
    for instruction in instructions_text:
        words = instruction.split(" ")
        line = ""
        for word in words:
            test_line = line + word + " "
            test_width = instructions_font.size(test_line)[0]
            if test_width > SCREEN_WIDTH - 40:
                wrapped_instructions.append(line)
                line = word + " "
            else:
                line = test_line
        wrapped_instructions.append(line)

    # Display all the wrapped instructions
    displayed_instructions = wrapped_instructions

    # Calculate the vertical position of instructions
    instructions_y = title_rect.bottom + 20  # Adjust the spacing as needed
    for instruction in displayed_instructions:
        instruction_surface = instructions_font.render(instruction, True, (0, 0, 0))
        instruction_rect = instruction_surface.get_rect(
            center=(SCREEN_WIDTH // 2, instructions_y)
        )
        instructions_rects.append(instruction_rect)
        instructions_y += instructions_font.get_height() + line_spacing

    start_prompt = instructions_font.render(
        strings.get("start_prompt"),
        True,
        (0, 0, 0),
    )
    start_prompt_rect = start_prompt.get_rect(
        center=(SCREEN_WIDTH // 2, instructions_y + 40)
    )

    high_score_font: pygame.font.Font = pygame.font.Font(None, 36)
    high_score_text: pygame.Surface = high_score_font.render(
        f"{strings.get('high_score')}: {high_score}", True, (0, 0, 0)
    )
    high_score_rect: pygame.Rect = high_score_text.get_rect(
        center=(SCREEN_WIDTH // 2, instructions_y + 80)
    )  # Adjust the spacing as needed

    project_note_y = high_score_rect.bottom + 40  # Adjust the spacing as needed
    for line in project_note_lines:
        project_note_surface = project_note_font.render(line, True, (0, 0, 0))
        project_note_rect = project_note_surface.get_rect(
            center=(SCREEN_WIDTH // 2, project_note_y)
        )
        project_note_rects.append(project_note_rect)
        project_note_y += (
            project_note_font.get_height() + 5
        )  # Adjust the line spacing as needed

    pygame.event.clear()  # Clear the event queue before entering the loop

    waiting_for_spacebar = True
    while waiting_for_spacebar:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Quit event received. Application shutting down.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    logging.info("Spacebar pressed. Starting new game session.")
                    waiting_for_spacebar = False
                    break

        screen.fill(LIGHT_BLUE)
        screen.blit(title_text, title_rect)
        for instruction, instruction_rect in zip(
            displayed_instructions, instructions_rects
        ):
            screen.blit(
                instructions_font.render(instruction, True, (0, 0, 0)), instruction_rect
            )
        screen.blit(start_prompt, start_prompt_rect)
        high_score_text = high_score_font.render(
            f"{strings.get('high_score')}: {high_score}", True, (0, 0, 0)
        )  # Update high score text
        screen.blit(high_score_text, high_score_rect)
        for line, project_note_rect in zip(project_note_lines, project_note_rects):
            screen.blit(
                project_note_font.render(line, True, (0, 0, 0)), project_note_rect
            )

        pygame.display.update()
        clock.tick(FPS)


def game(strings: dict, high_score: int) -> int:
    global platforms
    running: bool = True
    score: int = 0
    passed_platforms: int = 0
    last_platform_jumped: Optional[Platform] = (
        None  # Initialize last_platform_jumped to None
    )

    logging.info("Game session started.")

    # Reset game state
    player: Character = Character(
        80, [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80], "frog.png"
    )
    player_x_change: float = 0
    player_y_change: float = 0
    platforms = [
        Platform(
            SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2,
            SCREEN_HEIGHT - PLATFORM_HEIGHT,
            PLATFORM_WIDTH,
            PLATFORM_HEIGHT,
        )
    ]
    Platform.reset_id()  # Reset platform IDs when starting a new game

    camera: Camera = Camera(player)  # Create a camera instance
    world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Create overlay elements
    font: pygame.font.Font = pygame.font.Font(None, 36)
    score_label: HighScoreLabel = HighScoreLabel(
        10,
        10,
        font,
        (0, 0, 0),
        strings.get("score"),
        strings.get("high_score"),
    )
    overlay_elements: pygame.sprite.Group = pygame.sprite.Group(score_label)

    # Generate initial platforms
    while len(world.platforms) < 6:  # Adjust the number of initial platforms as needed
        add_platform(world)

    # Set player's starting position on the second platform
    player.rect.bottomleft = (SCREEN_WIDTH // 2, world.platforms[1].rect.top)

    while running:
        # Game over condition
        if player.rect.top > camera.offset_y + SCREEN_HEIGHT:
            logging.info("Game over")
            game_over_screen(strings)
            return high_score  # Return the updated high score when the game is over

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Quit event received. Application shutting down.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player_x_change = -5
                    player.flip_horizontally("left")
                    logging.info("Left key pressed.")
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player_x_change = 5
                    player.flip_horizontally("right")
                    logging.info("Right key pressed.")
            if event.type == pygame.KEYUP:
                if (
                    event.key == pygame.K_LEFT
                    or event.key == pygame.K_RIGHT
                    or event.key == pygame.K_a
                    or event.key == pygame.K_d
                ):
                    player_x_change = 0
                    logging.info("Left/Right key released.")

        screen.fill(LIGHT_BLUE)  # Fill the screen with light blue color

        # Update passed_platforms and high score only when the player jumps on a new higher platform
        if (
            last_platform_jumped is not None
            and player.rect.bottom <= last_platform_jumped.rect.top
        ):
            highest_platform: Platform = max(
                platforms, key=lambda platform: platform.rect.top
            )
            if (
                last_platform_jumped.rect.top < highest_platform.rect.top
                and not last_platform_jumped.passed
            ):
                passed_platforms += 1
                last_platform_jumped.passed = True
                logging.info(
                    f"You have passed platform with ID {last_platform_jumped.id}"
                )  # Log the passed platform ID
                score = passed_platforms
                if score > high_score:
                    high_score = score
                score_label.update_score(score, high_score)

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
                    player.rect.bottom = (
                        platform.rect.top
                    )  # Adjust the player's position to be on top of the platform
                    player_y_change = player.jump()  # Make the character jump automatically when they fall onto a platform

                    # Update last_platform_jumped only when jumping on a new higher platform
                    if last_platform_jumped is None or platform.rect.top < last_platform_jumped.rect.top:
                        last_platform_jumped = platform

        # Add new platforms when the player reaches a certain height relative to the camera's offset
        if player.rect.top < camera.offset_y + SCREEN_HEIGHT // 3:
            add_platform(world)

        # Remove platforms that are no longer visible on the screen
        platforms = [
            platform
            for platform in platforms
            if platform.rect.top < camera.offset_y + SCREEN_HEIGHT
        ]

        # Update camera
        camera.update()

        # Draw the player and platforms
        player_rect: pygame.Rect = camera.apply(player.rect)
        screen.blit(player.image, player_rect)
        world.draw_platforms(screen, camera.offset_y)

        # Draw overlay elements
        overlay_elements.draw(screen)

        pygame.display.update()
        clock.tick(FPS)

    return high_score  # Ensure high_score is returned if the loop exits


if __name__ == "__main__":
    logging.info("Application launched.")
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Frog Jump Game"
    )
    parser.add_argument(
        "-l", "--language", default="en", help="Language code (default: en)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase logging level to DEBUG"
    )
    args: argparse.Namespace = parser.parse_args()

    # Set logging level based on the verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    language: str = args.language
    strings: dict = load_localized_strings(language)
    while True:
        start_screen(strings)
        high_score = game(strings, high_score)  # Store the updated high score
