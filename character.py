import logging
from typing import List, Optional

import pygame

from platform_sprite import Platform


class Character(pygame.sprite.Sprite):
    def __init__(self, size: int, pos: List[int], image_path: str):
        super().__init__()
        self.original_image: pygame.Surface = pygame.image.load(image_path)
        self.original_image = pygame.transform.scale(self.original_image, (size, size))
        self.image: pygame.Surface = self.original_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.facing_right: bool = False
        self.last_platform: Optional[Platform] = (
            None  # Track the last platform jumped from
        )
        self.altitude: float = pos[1]  # Initialize altitude based on initial Y position

    def update(self, x_change: float, y_change: float, platforms: List[Platform]) -> None:
        self.rect.move_ip(x_change, y_change)
        self.altitude -= y_change  # Update altitude, decrease when descending, increase when ascending

        logging.debug(f"Absolute Y changed: {self.altitude}")

        # Update last platform only when the player is on a platform
        self.last_platform = None
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and y_change >= 0:
                self.last_platform = platform
                break

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect)

    def jump(self) -> int:
        self.rect.y -= 1  # Move the player slightly off the platform
        return -15  # Set the initial upward velocity

    def flip_horizontally(self, direction: str) -> None:
        if direction == "right" and not self.facing_right:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.facing_right = True
        elif direction == "left" and self.facing_right:
            self.image = self.original_image
            self.facing_right = False
