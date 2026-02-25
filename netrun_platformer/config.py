from __future__ import annotations

from dataclasses import dataclass

LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
WINDOW_SCALE = 4
WINDOW_WIDTH = LOGICAL_WIDTH * WINDOW_SCALE
WINDOW_HEIGHT = LOGICAL_HEIGHT * WINDOW_SCALE
TILE_SIZE = 16
GRAVITY = 920.0
MAX_FALL_SPEED = 540.0
FPS = 60

COLOR_BLACK = (6, 8, 12)
COLOR_WHITE = (236, 240, 255)
COLOR_HUD = (8, 12, 18, 204)
COLOR_NEON = (26, 210, 202)
COLOR_WARN = (230, 88, 88)


@dataclass(frozen=True)
class Archetype:
    label: str
    codename: str
    max_hp: int
    speed: float
    jump_power: float
    fire_delay: float
    bullet_damage: int
    bullet_speed: float
    ability_name: str
    ability_cooldown: float
    ability_duration: float
    dash_speed: float = 0.0
    shield_reduction: float = 1.0


ARCHETYPES: dict[str, Archetype] = {
    "ghost": Archetype(
        label="glass cannon",
        codename="ghost",
        max_hp=72,
        speed=148.0,
        jump_power=336.0,
        fire_delay=0.14,
        bullet_damage=26,
        bullet_speed=286.0,
        ability_name="phase dash",
        ability_cooldown=2.2,
        ability_duration=0.22,
        dash_speed=356.0,
    ),
    "bulwark": Archetype(
        label="tank",
        codename="bulwark",
        max_hp=164,
        speed=112.0,
        jump_power=320.0,
        fire_delay=0.24,
        bullet_damage=18,
        bullet_speed=248.0,
        ability_name="firewall shell",
        ability_cooldown=3.4,
        ability_duration=2.1,
        shield_reduction=0.42,
    ),
}

