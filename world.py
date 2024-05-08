from typing import List, Tuple
import pygame

from platform_sprite import Platform

class World:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.platforms: List[Platform] = []  # List to store platforms
        self.camera_y: int = 0

    def draw_platforms(self, screen: pygame.Surface, camera_offset: float):
        for platform in self.platforms:
            screen_x, screen_y = platform.rect.x, platform.rect.y - camera_offset
            screen.blit(platform.image, (screen_x, screen_y))

    def to_screen_coords(self, world_x: int, world_y: int) -> Tuple[int, int]:
        screen_x: int = world_x
        screen_y: int = world_y - self.camera_y
        return screen_x, screen_y

    def get_platforms(self) -> List[Platform]:
        return self.platforms

    def add_platform(self, platform: Platform):
        self.platforms.append(platform)

    def set_platforms(self, platforms: List[Platform]):
        self.platforms = platforms

    def delete_platform(self, platform: Platform):
        self.platforms.remove(platform)
        