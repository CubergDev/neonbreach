from __future__ import annotations

import pygame

from netrun_platformer.config import LOGICAL_HEIGHT, LOGICAL_WIDTH, TILE_SIZE
from netrun_platformer.levels import LevelSpec


class LevelRuntime:
    def __init__(self, spec: LevelSpec) -> None:
        self.spec = spec
        grid = [list(row) for row in spec.rows]
        self.height = len(grid)
        self.width = len(grid[0])
        self.player_spawn = (12.0, 12.0)
        self.exit_pos = (self.width * TILE_SIZE - TILE_SIZE * 2, self.height * TILE_SIZE - TILE_SIZE * 3)
        self.enemy_spawns: list[tuple[float, float]] = []
        self.turret_spawns: list[tuple[float, float]] = []
        self.shard_spawns: list[tuple[float, float]] = []
        self.boss_spawn: tuple[float, float] | None = None

        for y, row in enumerate(grid):
            for x, char in enumerate(row):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                if char == "p":
                    self.player_spawn = (px + 1, py)
                    row[x] = "."
                elif char == "x":
                    self.exit_pos = (px, py - TILE_SIZE)
                    row[x] = "."
                elif char == "e":
                    self.enemy_spawns.append((px + 1, py))
                    row[x] = "."
                elif char == "t":
                    self.turret_spawns.append((px + 1, py))
                    row[x] = "."
                elif char == "d":
                    self.shard_spawns.append((px + 3, py + 2))
                    row[x] = "."
                elif char == "b":
                    self.boss_spawn = (px, py - 10)
                    row[x] = "."

        self.tiles = ["".join(row) for row in grid]
        self.exit_rect = pygame.Rect(int(self.exit_pos[0]), int(self.exit_pos[1]), TILE_SIZE, TILE_SIZE * 2)
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE

    def tile_at(self, tx: int, ty: int) -> str:
        if ty < 0:
            return "."
        if tx < 0 or ty >= self.height or tx >= self.width:
            return "#"
        return self.tiles[ty][tx]

    def is_solid(self, tx: int, ty: int) -> bool:
        return self.tile_at(tx, ty) == "#"

    def is_hazard(self, tx: int, ty: int) -> bool:
        return self.tile_at(tx, ty) == "^"

    def is_solid_pixel(self, px: float, py: float) -> bool:
        return self.is_solid(int(px // TILE_SIZE), int(py // TILE_SIZE))

    def rect_hits_solid(self, rect: pygame.Rect) -> bool:
        left = rect.left // TILE_SIZE
        right = (rect.right - 1) // TILE_SIZE
        top = rect.top // TILE_SIZE
        bottom = (rect.bottom - 1) // TILE_SIZE
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if self.is_solid(tx, ty):
                    return True
        return False

    def rect_hits_hazard(self, rect: pygame.Rect) -> bool:
        left = rect.left // TILE_SIZE
        right = (rect.right - 1) // TILE_SIZE
        top = rect.top // TILE_SIZE
        bottom = (rect.bottom - 1) // TILE_SIZE
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if self.is_hazard(tx, ty):
                    return True
        return False

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int, pixels: "PixelBankProtocol") -> None:
        start_x = max(0, camera_x // TILE_SIZE)
        end_x = min(self.width, (camera_x + LOGICAL_WIDTH) // TILE_SIZE + 2)
        start_y = max(0, camera_y // TILE_SIZE)
        end_y = min(self.height, (camera_y + LOGICAL_HEIGHT) // TILE_SIZE + 2)
        for ty in range(start_y, end_y):
            row = self.tiles[ty]
            for tx in range(start_x, end_x):
                px = tx * TILE_SIZE - camera_x
                py = ty * TILE_SIZE - camera_y
                tile = row[tx]
                if tile == "#":
                    surface.blit(pixels.tile, (px, py))
                elif tile == "^":
                    surface.blit(pixels.spike, (px, py))


class PixelBankProtocol:
    tile: pygame.Surface
    spike: pygame.Surface

