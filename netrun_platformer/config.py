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
ENEMY_BASE_SPEED = 65.0
ENEMY_AGGRO_RANGE = 320.0
ENEMY_AGGRO_ENTER_RANGE = 319.0
ENEMY_AGGRO_EXIT_RANGE = 359.0
ENEMY_CHASE_MEMORY = 0.85
ENEMY_CHASE_MAX_DY = 108.0
ENEMY_JUMP_POWER = 302.0
ENEMY_JUMP_COOLDOWN = 0.46
ENEMY_TURN_COOLDOWN = 0.1
ENEMY_STUCK_TIME = 0.38
ENEMY_GAP_JUMP_PIXELS = 63.0
ENEMY_EDGE_DROP_DY = int(TILE_SIZE * 1.5)
ENEMY_EDGE_COMMIT_DY = int(TILE_SIZE * 0.9)
ENEMY_EDGE_HOLD_TIME = 0.1
ENEMY_EDGE_FAIL_TURN_TIME = 0.3
ENEMY_PATROL_SPEED_FACTOR = 0.72
ENEMY_ROAM_GAP_COOLDOWN = 0.66
HUNTER_BASE_SPEED = 69.0
HUNTER_AGGRO_RANGE = 337.0
HUNTER_JUMP_POWER = 327.0
HUNTER_PATROL_SPEED_FACTOR = 0.82
HUNTER_PREFERRED_MIN_X = 101.0
HUNTER_PREFERRED_MAX_X = 161.0
HUNTER_SHOOT_RANGE_X = 226.0
HUNTER_SHOOT_RANGE_Y = 104.0
HUNTER_FIRE_COOLDOWN_MIN = 0.75
HUNTER_FIRE_COOLDOWN_MAX = 1.07
HUNTER_BULLET_DAMAGE = 9
TURRET_BULLET_DAMAGE = 10
BOSS_BULLET_DAMAGE = 14
MINEBOT_SPEED = 91.0
MINEBOT_AGGRO_RANGE = 261.0
MINEBOT_JUMP_POWER = 266.0
MINEBOT_JUMP_COOLDOWN = 0.25
MINEBOT_STUCK_TIME = 0.26
MINEBOT_PATROL_SPEED_FACTOR = 0.54
MINEBOT_ARM_RANGE_X = 36.0
MINEBOT_ARM_RANGE_Y = 28.0
MINEBOT_FUSE_TIME = 0.44
MINEBOT_FUSE_CHASE_SPEED = 57.0
MINEBOT_MIN_FUSE_NEAR_TARGET = 0.23
MINEBOT_EXPLOSION_INNER_RADIUS = 14.0
MINEBOT_EXPLOSION_RADIUS = 32.0
MINEBOT_EXPLOSION_DAMAGE_MAX = 24
MINEBOT_EXPLOSION_DAMAGE_MIN = 8
MINEBOT_CONTACT_FUSE = 0.42
MINEBOT_STAGGER_FUSE = 0.3
RELAY_MAX_HP = 42
SIGNAL_TIMER_START = 19.0
SIGNAL_TIMER_SHARD_BONUS = 1.5
SIGNAL_TIMER_RELAY_BONUS = 4.0
SIGNAL_TIMER_BASE_DRAIN = 0.55
SIGNAL_TIMER_ACTIVE_RELAY_DRAIN = 0.24
SIGNAL_TIMER_RECOVERY = 0.9
SIGNAL_JAM_CYCLE = 6.0
SIGNAL_JAM_WINDOW = 2.35
SIGNAL_JAM_WINDOW_REDUCTION = 0.55

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
