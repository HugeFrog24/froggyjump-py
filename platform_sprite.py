import logging
from typing import Optional

import pygame

from constants import DARK_BROWN

class Platform(pygame.sprite.Sprite):
    next_id: int = 1  # Class variable to keep track of the next available platform ID

    def __init__(self, x: int, y: int, width: int, height: int, absolute_y: Optional[int] = None):
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((width, height))
        self.image.fill(DARK_BROWN)
        self.rect: pygame.Rect = self.image.get_rect(topleft=(x, y))
        self.absolute_y: int = absolute_y if absolute_y is not None else y  # Store the absolute y position
        self.passed: bool = False  # Track if the platform has been passed
        self.id: int = Platform.next_id  # Assign a unique ID to each platform
        Platform.next_id += 1  # Increment the next available platform ID
        logging.info(
            f"Generating platform with ID {self.id} at absolute position {self.absolute_y}"
        )  # Log the platform generation with absolute position

    def passed_by_player(self, player_last_platform: Optional["Platform"]) -> bool:
        # Check if the player has passed this platform
        if player_last_platform and player_last_platform.rect.top > self.rect.top:
            return True
        return False

    @classmethod
    def reset_id(cls) -> None:
        cls.next_id = 1  # Reset the next available platform ID to 1
