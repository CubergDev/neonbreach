from __future__ import annotations

import math
import random
from array import array
from pathlib import Path

import pygame

from netrun_platformer.config import LOGICAL_HEIGHT, LOGICAL_WIDTH, TILE_SIZE


class PixelBank:
    def __init__(self) -> None:
        self.tile = self._make_tile()
        self.spike = self._make_spike()
        self.exit_locked = self._make_exit((32, 74, 98))
        self.exit_open = self._make_exit((34, 200, 170))
        self.bullet_player = self._square(4, (80, 248, 230))
        self.bullet_enemy = self._square(4, (252, 82, 82))
        self.shard_frames = self._make_shard_frames()
        self.relay = self._build_relay_frames()
        self.player = self._build_player_frames()
        self.enemy = self._build_enemy_frames()
        self.hunter = self._build_hunter_frames()
        self.mine = self._build_mine_frames()
        self.turret = self._build_turret_frames()
        self.boss = self._build_boss_frames()

    @staticmethod
    def _square(size: int, color: tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill(color)
        return surf

    @staticmethod
    def _sprite(pattern: list[str], palette: dict[str, tuple[int, int, int]], scale: int = 2) -> pygame.Surface:
        height = len(pattern)
        width = len(pattern[0])
        surf = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
        for y, row in enumerate(pattern):
            for x, char in enumerate(row):
                if char == ".":
                    continue
                pygame.draw.rect(surf, palette[char], (x * scale, y * scale, scale, scale))
        return surf

    def _make_tile(self) -> pygame.Surface:
        tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        tile.fill((18, 38, 52))
        pygame.draw.rect(tile, (12, 18, 24), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        for px in range(2, TILE_SIZE - 2, 4):
            pygame.draw.line(tile, (28, 74, 92), (px, 2), (px - 2, TILE_SIZE - 2))
        return tile

    def _make_spike(self) -> pygame.Surface:
        spike = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(spike, (36, 22, 26), (0, TILE_SIZE - 4, TILE_SIZE, 4))
        for x in range(0, TILE_SIZE, 4):
            pygame.draw.polygon(spike, (200, 64, 64), [(x, TILE_SIZE - 4), (x + 2, 2), (x + 4, TILE_SIZE - 4)])
        return spike

    def _make_exit(self, color: tuple[int, int, int]) -> pygame.Surface:
        door = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.rect(door, (10, 10, 14), (0, 0, TILE_SIZE, TILE_SIZE * 2))
        pygame.draw.rect(door, color, (2, 2, TILE_SIZE - 4, TILE_SIZE * 2 - 4), 1)
        pygame.draw.rect(door, color, (5, 9, TILE_SIZE - 10, TILE_SIZE + 12), 1)
        return door

    def _make_shard_frames(self) -> list[pygame.Surface]:
        palette = {"1": (90, 248, 230), "2": (26, 134, 120), "3": (210, 255, 250)}
        a = self._sprite(
            [
                "...3....",
                "..131...",
                ".13231..",
                ".122221.",
                ".132231.",
                "..131...",
                "...3....",
                "........",
            ],
            palette,
        )
        b = self._sprite(
            [
                "........",
                "....3...",
                "...131..",
                "..12221.",
                "..13231.",
                "...131..",
                "....3...",
                "........",
            ],
            palette,
        )
        c = self._sprite(
            [
                "........",
                "...33...",
                "..1321..",
                ".132231.",
                ".132231.",
                "..1321..",
                "...33...",
                "........",
            ],
            palette,
        )
        return [a, b, c, b]

    def _build_player_frames(self) -> dict[str, dict[str, list[pygame.Surface]]]:
        ghost_palette = {"1": (130, 250, 244), "2": (50, 172, 166), "3": (16, 50, 60), "4": (210, 255, 252)}
        tank_palette = {"1": (255, 188, 110), "2": (182, 102, 40), "3": (62, 34, 18), "4": (250, 224, 188)}
        ghost_idle = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32144123",
                ".3222223",
                "..3..3..",
                "..4..4..",
            ],
            ghost_palette,
        )
        ghost_run = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32144123",
                ".3222223",
                ".4....4.",
                "4......4",
            ],
            ghost_palette,
        )
        ghost_jump = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32144123",
                ".3222223",
                "..44.44.",
                "........",
            ],
            ghost_palette,
        )
        tank_idle = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32111123",
                "32222223",
                ".3.22.3.",
                ".4....4.",
            ],
            tank_palette,
        )
        tank_run = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32111123",
                "32222223",
                "4..22..4",
                ".4....4.",
            ],
            tank_palette,
        )
        tank_jump = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32111123",
                "32111123",
                "32222223",
                "..4224..",
                "........",
            ],
            tank_palette,
        )
        return {
            "ghost": {"idle": [ghost_idle, ghost_run], "run": [ghost_run, ghost_idle], "jump": [ghost_jump], "ability": [ghost_run]},
            "bulwark": {"idle": [tank_idle, tank_run], "run": [tank_run, tank_idle], "jump": [tank_jump], "ability": [tank_idle]},
        }

    def _build_relay_frames(self) -> list[pygame.Surface]:
        palette = {"1": (110, 244, 236), "2": (28, 122, 138), "3": (16, 32, 44), "4": (238, 255, 252)}
        active = self._sprite(
            [
                "...33...",
                "..3223..",
                ".321123.",
                ".321123.",
                "..3223..",
                "...33...",
                "..3..3..",
                "..3..3..",
                "..3..3..",
                "..3..3..",
            ],
            palette,
        )
        charging = self._sprite(
            [
                "...33...",
                "..3443..",
                ".321123.",
                ".321123.",
                "..3443..",
                "...33...",
                "..3..3..",
                ".3....3.",
                ".3....3.",
                "..3..3..",
            ],
            palette,
        )
        broken = self._sprite(
            [
                "........",
                "...33...",
                "..3..3..",
                ".3....3.",
                "..3..3..",
                "...33...",
                "..2222..",
                ".2.22.2.",
                ".2....2.",
                "........",
            ],
            {"2": (68, 78, 92), "3": (24, 28, 36)},
        )
        return [active, charging, active, broken]

    def _build_enemy_frames(self) -> list[pygame.Surface]:
        palette = {"1": (255, 120, 120), "2": (134, 42, 58), "3": (44, 16, 24), "4": (255, 214, 214)}
        a = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32411423",
                "32111123",
                ".3222223",
                ".3....3.",
                "..3..3..",
                "..3..3..",
            ],
            palette,
        )
        b = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32411423",
                ".3222223",
                ".3....3.",
                ".3....3.",
                "3......3",
            ],
            palette,
        )
        c = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32411423",
                "32111123",
                ".3222223",
                ".3....3.",
                "3..33..3",
                ".3....3.",
            ],
            palette,
        )
        return [a, b, c, b]

    def _build_hunter_frames(self) -> list[pygame.Surface]:
        palette = {"1": (120, 208, 255), "2": (42, 108, 150), "3": (18, 34, 52), "4": (226, 245, 255)}
        a = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32411423",
                "32111123",
                "32222223",
                ".3....3.",
                "..34.43.",
                "..3...3.",
            ],
            palette,
        )
        b = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32411423",
                "32222223",
                ".3....3.",
                ".34...43",
                "..3...3.",
            ],
            palette,
        )
        c = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32411423",
                "32111123",
                "32222223",
                ".3....3.",
                "3..44..3",
                ".3....3.",
            ],
            palette,
        )
        return [a, b, c, b]

    def _build_mine_frames(self) -> list[pygame.Surface]:
        palette = {"1": (255, 170, 96), "2": (152, 84, 52), "3": (44, 28, 20), "4": (255, 232, 210)}
        a = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32144123",
                "32111123",
                ".3222223",
                "..3333..",
                "..3..3..",
                "........",
            ],
            palette,
        )
        b = self._sprite(
            [
                "..3333..",
                ".322223.",
                "32111123",
                "32144123",
                ".3222223",
                "..3333..",
                ".3....3.",
                "........",
            ],
            palette,
        )
        return [a, b]

    def _build_turret_frames(self) -> list[pygame.Surface]:
        palette = {"1": (180, 220, 255), "2": (60, 92, 120), "3": (22, 30, 40), "4": (236, 250, 255)}
        a = self._sprite(
            [
                "........",
                "..3333..",
                ".322223.",
                "32214123",
                ".322223.",
                "..3333..",
                ".3....3.",
                ".333333.",
            ],
            palette,
        )
        b = self._sprite(
            [
                "...33...",
                "..3223..",
                ".322223.",
                "32241123",
                ".322223.",
                "..3333..",
                ".3....3.",
                ".333333.",
            ],
            palette,
        )
        c = self._sprite(
            [
                "...33...",
                "..3223..",
                ".322223.",
                "32211423",
                ".322223.",
                "..3333..",
                ".3....3.",
                ".333333.",
            ],
            palette,
        )
        return [a, b, c, b]

    def _build_boss_frames(self) -> list[pygame.Surface]:
        palette = {"1": (240, 144, 100), "2": (162, 72, 46), "3": (62, 32, 24), "4": (255, 212, 170)}
        a = self._sprite(
            [
                ".333333.",
                "32222223",
                "32411423",
                "32111123",
                "32111123",
                "32222223",
                "3.4..4.3",
                "3......3",
            ],
            palette,
            scale=3,
        )
        b = self._sprite(
            [
                ".333333.",
                "32222223",
                "32111123",
                "32411423",
                "32111123",
                "32222223",
                "34....43",
                ".3....3.",
            ],
            palette,
            scale=3,
        )
        c = self._sprite(
            [
                ".333333.",
                "32222223",
                "32111123",
                "32411423",
                "32111123",
                "32222223",
                "3..44..3",
                ".3....3.",
            ],
            palette,
            scale=3,
        )
        return [a, b, c, b]


class SoundBank:
    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error:
            return
        self.enabled = True
        self.sounds = {
            "shoot": self._tone(660, 0.08, 0.28, "square", -180),
            "jump": self._tone(300, 0.14, 0.34, "square", 260),
            "hit": self._tone(120, 0.12, 0.33, "noise", -40),
            "pickup": self._tone(780, 0.1, 0.30, "square", 240),
            "ability": self._tone(520, 0.12, 0.28, "sine", 140),
            "clear": self._tone(920, 0.24, 0.24, "square", -300),
            "boss": self._tone(180, 0.22, 0.35, "sine", -20),
            "dead": self._tone(90, 0.24, 0.34, "square", -60),
        }

    def _tone(self, freq: float, duration: float, volume: float, wave: str, sweep: float) -> pygame.mixer.Sound:
        rng = random.Random(42)
        sample_rate = 22050
        sample_count = max(1, int(sample_rate * duration))
        samples = array("h")
        phase = 0.0
        for i in range(sample_count):
            t = i / sample_rate
            current = max(40.0, freq + sweep * t)
            phase += current / sample_rate
            if wave == "square":
                value = 1.0 if phase % 1.0 < 0.5 else -1.0
            elif wave == "noise":
                value = rng.uniform(-1.0, 1.0)
            else:
                value = math.sin(phase * math.tau)
            envelope = max(0.0, 1.0 - t / duration)
            samples.append(int(value * envelope * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name: str) -> None:
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


def ensure_splash_image(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    image = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    for y in range(LOGICAL_HEIGHT):
        tone = 14 + y // 5
        pygame.draw.line(image, (tone // 2, tone + 18, tone + 46), (0, y), (LOGICAL_WIDTH, y))
    for x in range(0, LOGICAL_WIDTH, 16):
        pygame.draw.line(image, (16, 40, 70), (x, 0), (x + 36, LOGICAL_HEIGHT), 1)
    pygame.draw.rect(image, (18, 22, 34), (26, 44, 268, 94))
    pygame.draw.rect(image, (42, 162, 154), (26, 44, 268, 94), 1)
    pygame.image.save(image, path)
