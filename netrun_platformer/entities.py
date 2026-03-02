from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from netrun_platformer.config import GRAVITY, MAX_FALL_SPEED


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    damage: int
    from_player: bool
    ttl: float = 1.4

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - 2, int(self.y) - 2, 4, 4)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.ttl -= dt


@dataclass
class DataShard:
    x: float
    y: float
    taken: bool = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), 10, 12)


class PhysicsBody:
    def __init__(self, x: float, y: float, w: int, h: int, hp: int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.x_rem = 0.0
        self.y_rem = 0.0
        self.on_ground = False
        self.facing = 1
        self.hp = hp
        self.max_hp = hp

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def move(self, level: "LevelRuntimeProtocol", dt: float) -> None:
        self._move_axis(level, self.vx * dt, "x")
        self._move_axis(level, self.vy * dt, "y")

    def _move_axis(self, level: "LevelRuntimeProtocol", amount: float, axis: str) -> None:
        if axis == "x":
            self.x_rem += amount
            move = math.trunc(self.x_rem)
            self.x_rem -= move
        else:
            self.y_rem += amount
            move = math.trunc(self.y_rem)
            self.y_rem -= move
            self.on_ground = False
            if move == 0:
                # Preserve grounded state while resting on a solid surface.
                self.on_ground = level.rect_hits_solid(self.rect.move(0, 1))
                return

        step = 1 if move > 0 else -1
        while move != 0:
            next_rect = self.rect
            if axis == "x":
                next_rect.x += step
            else:
                next_rect.y += step
            if level.rect_hits_solid(next_rect):
                if axis == "x":
                    self.vx = 0.0
                    self.x_rem = 0.0
                else:
                    if step > 0:
                        self.on_ground = True
                    self.vy = 0.0
                    self.y_rem = 0.0
                return
            if axis == "x":
                self.x += step
            else:
                self.y += step
            move -= step


class Player(PhysicsBody):
    def __init__(self, x: float, y: float, archetype: "ArchetypeProtocol", kind: str) -> None:
        super().__init__(x, y, 14, 16, archetype.max_hp)
        self.kind = kind
        self.stats = archetype
        self.shoot_cd = 0.0
        self.ability_cd = 0.0
        self.ability_timer = 0.0
        self.invuln_timer = 0.0
        self.jump_buffer = 0.0
        self.just_jumped = False

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        controls: dict[str, bool],
        gravity_scale: float = 1.0,
    ) -> None:
        self.just_jumped = False
        self.shoot_cd = max(0.0, self.shoot_cd - dt)
        self.ability_cd = max(0.0, self.ability_cd - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        if self.ability_timer > 0.0:
            self.ability_timer = max(0.0, self.ability_timer - dt)
        if controls["jump"]:
            self.jump_buffer = 0.12

        left = controls["left"]
        right = controls["right"]
        direction = int(right) - int(left)
        if direction != 0:
            self.facing = direction

        if controls["ability"] and self.ability_cd == 0.0:
            self.ability_cd = self.stats.ability_cooldown
            self.ability_timer = self.stats.ability_duration
            if self.kind == "ghost":
                self.invuln_timer = self.stats.ability_duration

        if self.kind == "ghost" and self.ability_timer > 0.0:
            self.vx = self.facing * self.stats.dash_speed
            self.vy = 0.0
        else:
            self.vx = direction * self.stats.speed
            self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)

        if self.jump_buffer > 0.0 and self.on_ground:
            self.vy = -self.stats.jump_power
            self.on_ground = False
            self.jump_buffer = 0.0
            self.just_jumped = True

        self.move(level, dt)

    def shoot(self, target: tuple[float, float] | None = None) -> Bullet | None:
        if self.shoot_cd > 0.0:
            return None
        self.shoot_cd = self.stats.fire_delay
        origin_x = self.x + self.w * 0.5
        origin_y = self.y + self.h * 0.46
        if target is None:
            return Bullet(origin_x + self.facing * 6, origin_y, self.facing * self.stats.bullet_speed, 0.0, self.stats.bullet_damage, True)
        dx = target[0] - origin_x
        dy = target[1] - origin_y
        distance = max(1.0, math.hypot(dx, dy))
        vx = dx / distance * self.stats.bullet_speed
        vy = dy / distance * self.stats.bullet_speed
        if abs(dx) > 1:
            self.facing = 1 if dx > 0 else -1
        return Bullet(origin_x, origin_y, vx, vy, self.stats.bullet_damage, True)

    def hurt(self, damage: int) -> bool:
        if self.invuln_timer > 0.0:
            return False
        adjusted = damage
        if self.kind == "bulwark" and self.ability_timer > 0.0:
            adjusted = int(damage * self.stats.shield_reduction)
        self.hp = max(0, self.hp - max(1, adjusted))
        self.invuln_timer = 0.45
        return True

    def ability_active(self) -> bool:
        return self.ability_timer > 0.0

    def animation(self) -> str:
        if self.ability_timer > 0.0:
            return "ability"
        if not self.on_ground:
            return "jump"
        if abs(self.vx) > 10.0:
            return "run"
        return "idle"


class Enemy(PhysicsBody):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 14, 16, 56)
        self.direction = random.choice([-1, 1])
        self.speed = 58.0
        self.aggro_range = 280.0
        self.jump_power = 280.0

    def _blocked_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        check_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        return level.is_solid_pixel(check_x, self.y + 2) or level.is_solid_pixel(check_x, self.y + self.h - 2)

    def _floor_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        foot_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        foot_y = self.y + self.h + 1
        return level.is_solid_pixel(foot_x, foot_y)

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: "Player",
        gravity_scale: float = 1.0,
    ) -> None:
        player_center_x = player.x + player.w * 0.5
        my_center_x = self.x + self.w * 0.5
        dx = player_center_x - my_center_x
        if abs(dx) <= self.aggro_range:
            if abs(dx) > 2.0:
                self.direction = 1 if dx > 0 else -1
        if self.on_ground and self._blocked_ahead(level, self.direction):
            self.vy = -self.jump_power
        elif self.on_ground and not self._floor_ahead(level, self.direction):
            self.direction *= -1
        self.vx = self.direction * self.speed
        self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
        prev_x = self.x
        self.move(level, dt)
        if self.on_ground and abs(self.x - prev_x) < 0.05 and self._blocked_ahead(level, self.direction):
            self.direction *= -1
        self.facing = self.direction


class Hunter(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.hp = 68
        self.max_hp = 68
        self.speed = 70.0
        self.aggro_range = 340.0
        self.shot_cd = random.uniform(0.2, 1.0)

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: "Player",
        gravity_scale: float = 1.0,
    ) -> Bullet | None:
        super().update(dt, level, player, gravity_scale=gravity_scale)
        self.shot_cd = max(0.0, self.shot_cd - dt)
        origin_x = self.x + self.w * 0.5
        origin_y = self.y + 5
        target_x = player.x + player.w * 0.5
        target_y = player.y + player.h * 0.5
        dx = target_x - origin_x
        dy = target_y - origin_y
        if abs(dx) > 190 or abs(dy) > 96:
            return None
        if self.shot_cd > 0.0:
            return None
        if not level.has_line_of_sight((origin_x, origin_y), (target_x, target_y)):
            return None
        self.shot_cd = random.uniform(1.0, 1.6)
        length = max(1.0, math.hypot(dx, dy))
        speed = 208.0
        return Bullet(origin_x, origin_y, dx / length * speed, dy / length * speed, 12, False)


class MineBot(PhysicsBody):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 12, 12, 34)
        self.direction = random.choice([-1, 1])
        self.speed = 76.0
        self.fuse = 0.0

    def _blocked_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        check_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        return level.is_solid_pixel(check_x, self.y + 2) or level.is_solid_pixel(check_x, self.y + self.h - 2)

    def _floor_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        foot_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        foot_y = self.y + self.h + 1
        return level.is_solid_pixel(foot_x, foot_y)

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: "Player",
        gravity_scale: float = 1.0,
    ) -> bool:
        player_center_x = player.x + player.w * 0.5
        player_center_y = player.y + player.h * 0.5
        my_center_x = self.x + self.w * 0.5
        my_center_y = self.y + self.h * 0.5
        dx = player_center_x - my_center_x
        dy = player_center_y - my_center_y

        if self.fuse > 0.0:
            self.fuse = max(0.0, self.fuse - dt)
            self.vx = 0.0
            self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
            self.move(level, dt)
            return self.fuse == 0.0

        if abs(dx) <= 160 and abs(dy) <= 56 and abs(dx) > 1.5:
            self.direction = 1 if dx > 0 else -1
        if abs(dx) <= 22 and abs(dy) <= 20:
            self.fuse = 0.55
            self.vx = 0.0
            return False

        if self.on_ground and self._blocked_ahead(level, self.direction):
            self.vy = -220.0
        elif self.on_ground and not self._floor_ahead(level, self.direction):
            self.direction *= -1

        self.vx = self.direction * self.speed
        self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
        prev_x = self.x
        self.move(level, dt)
        if self.on_ground and abs(self.x - prev_x) < 0.05 and self._blocked_ahead(level, self.direction):
            self.direction *= -1
        self.facing = self.direction
        return False


class Turret(PhysicsBody):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 14, 16, 72)
        self.cooldown = random.uniform(0.2, 0.8)

    def update(self, dt: float, player: Player, level: "LevelRuntimeProtocol") -> Bullet | None:
        self.cooldown = max(0.0, self.cooldown - dt)
        origin_x = self.x + self.w * 0.5
        origin_y = self.y + 6
        target_x = player.x + player.w * 0.5
        target_y = player.y + player.h * 0.5
        dx = target_x - origin_x
        dy = target_y - origin_y
        if abs(dx) > 210 or abs(dy) > 80:
            return None
        self.facing = 1 if dx >= 0 else -1
        if not level.has_line_of_sight((origin_x, origin_y), (target_x, target_y)):
            return None
        if self.cooldown > 0.0:
            return None
        self.cooldown = 1.25
        speed = 180.0
        length = max(1.0, math.hypot(dx, dy))
        return Bullet(origin_x, origin_y, dx / length * speed, dy / length * speed, 14, False)


class Boss(PhysicsBody):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 24, 24, 420)
        self.shot_cd = 1.1
        self.jump_cd = 2.4

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: Player,
        gravity_scale: float = 1.0,
    ) -> list[Bullet]:
        bullets: list[Bullet] = []
        rage = 1.0 if self.hp > 200 else 1.45
        self.shot_cd = max(0.0, self.shot_cd - dt)
        self.jump_cd = max(0.0, self.jump_cd - dt)

        direction = 1 if player.x > self.x else -1
        self.vx = direction * 56.0 * rage
        self.facing = direction
        self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
        if self.jump_cd == 0.0 and self.on_ground:
            self.vy = -300.0
            self.jump_cd = 2.2 / rage

        self.move(level, dt)

        if self.shot_cd == 0.0:
            origin_x = self.x + self.w * 0.5
            origin_y = self.y + self.h * 0.42
            target_x = player.x + player.w * 0.5
            target_y = player.y + player.h * 0.5
            if not level.has_line_of_sight((origin_x, origin_y), (target_x, target_y)):
                self.shot_cd = 0.24
                return bullets
            self.shot_cd = 0.9 / rage
            towards = math.atan2(target_y - origin_y, target_x - origin_x)
            for spread in (-0.16, 0.0, 0.16):
                angle = towards + spread
                bullets.append(Bullet(origin_x, origin_y, math.cos(angle) * 210.0, math.sin(angle) * 210.0, 18, False))
        return bullets


class ArchetypeProtocol:
    max_hp: int
    speed: float
    jump_power: float
    fire_delay: float
    bullet_damage: int
    bullet_speed: float
    ability_cooldown: float
    ability_duration: float
    dash_speed: float
    shield_reduction: float


class LevelRuntimeProtocol:
    def rect_hits_solid(self, rect: pygame.Rect) -> bool: ...

    def is_solid_pixel(self, px: float, py: float) -> bool: ...

    def has_line_of_sight(self, start: tuple[float, float], end: tuple[float, float]) -> bool: ...
