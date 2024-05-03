import logging
import pygame
from typing import Tuple
from constants import LIGHT_BLUE

class HighScoreLabel(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int], score_text: str, high_score_text: str):
        super().__init__()
        self.font: pygame.font.Font = font
        self.color: Tuple[int, int, int] = color
        self.score: int = 0
        self.high_score: int = 0
        self.score_text: str = score_text
        self.high_score_text: str = high_score_text
        self.x: int = x
        self.y: int = y
        self.update_text()

    def update_text(self) -> None:
        score_text: pygame.Surface = self.font.render(f"{self.score_text}: {self.score}", True, self.color)
        high_score_text: pygame.Surface = self.font.render(f"{self.high_score_text}: {self.high_score}", True, self.color)
        self.image: pygame.Surface = pygame.Surface((max(score_text.get_width(), high_score_text.get_width()), score_text.get_height() + high_score_text.get_height()))
        self.image.fill(LIGHT_BLUE)
        self.image.blit(score_text, (0, 0))
        self.image.blit(high_score_text, (0, score_text.get_height()))
        self.rect: pygame.Rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_score(self, score: int, high_score: int) -> None:
        self.score = score
        self.high_score = high_score
        self.update_text()
        logging.info(f"Current score: {score}, High score: {high_score}.")
