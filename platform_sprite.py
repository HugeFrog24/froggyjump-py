from typing import Optional
import pygame

from constants import DARK_BROWN


class Platform(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((width, height))
        self.image.fill(DARK_BROWN)
        self.rect: pygame.Rect = self.image.get_rect(topleft=(x, y))
        self.passed: bool = False  # Track if the platform has been passed

    def passed_by_player(self, player_last_platform: Optional['Platform']) -> bool:
        # Check if the player has passed this platform
        if player_last_platform and player_last_platform.rect.top > self.rect.top:
            return True
        return False
