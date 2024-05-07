from typing import Tuple


class World:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.camera_y: int = 0

    def update_camera(self, target_y: int) -> None:
        self.camera_y = target_y - self.height // 2

    def to_screen_coords(self, world_x: int, world_y: int) -> Tuple[int, int]:
        screen_x: int = world_x
        screen_y: int = world_y - self.camera_y
        return screen_x, screen_y