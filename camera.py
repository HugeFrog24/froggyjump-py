import pygame

from character import Character
from constants import SCREEN_HEIGHT


class Camera:
    def __init__(self, target: Character):
        self.target: Character = target
        self.offset_y: float = 0
        self.offset_smoothing: float = 0.05

    def update(self) -> None:
        target_offset_y: float = self.target.rect.centery - SCREEN_HEIGHT // 2
        self.offset_y += (target_offset_y - self.offset_y) * self.offset_smoothing

    def apply(self, obj: pygame.Rect) -> pygame.Rect:
        return obj.move(0, -self.offset_y)