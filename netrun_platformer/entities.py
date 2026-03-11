from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from netrun_platformer.config import (
    BOSS_BULLET_DAMAGE,
    ENEMY_AGGRO_ENTER_RANGE,
    ENEMY_AGGRO_EXIT_RANGE,
    ENEMY_CHASE_MAX_DY,
    ENEMY_CHASE_MEMORY,
    ENEMY_AGGRO_RANGE,
    ENEMY_BASE_SPEED,
    ENEMY_EDGE_FAIL_TURN_TIME,
    ENEMY_EDGE_COMMIT_DY,
    ENEMY_EDGE_DROP_DY,
    ENEMY_EDGE_HOLD_TIME,
    ENEMY_GAP_JUMP_PIXELS,
    ENEMY_JUMP_COOLDOWN,
    ENEMY_JUMP_POWER,
    ENEMY_PATROL_SPEED_FACTOR,
    ENEMY_ROAM_GAP_COOLDOWN,
    ENEMY_STUCK_TIME,
    ENEMY_TURN_COOLDOWN,
    GRAVITY,
    HUNTER_BULLET_DAMAGE,
    HUNTER_AGGRO_RANGE,
    HUNTER_BASE_SPEED,
    HUNTER_FIRE_COOLDOWN_MAX,
    HUNTER_FIRE_COOLDOWN_MIN,
    HUNTER_JUMP_POWER,
    HUNTER_PATROL_SPEED_FACTOR,
    HUNTER_PREFERRED_MAX_X,
    HUNTER_PREFERRED_MIN_X,
    MINEBOT_AGGRO_RANGE,
    MINEBOT_ARM_RANGE_X,
    MINEBOT_ARM_RANGE_Y,
    MINEBOT_FUSE_CHASE_SPEED,
    MINEBOT_FUSE_TIME,
    MINEBOT_JUMP_COOLDOWN,
    MINEBOT_JUMP_POWER,
    MINEBOT_MIN_FUSE_NEAR_TARGET,
    MINEBOT_PATROL_SPEED_FACTOR,
    MINEBOT_SPEED,
    MINEBOT_STUCK_TIME,
    MAX_FALL_SPEED,
    TILE_SIZE,
    HUNTER_SHOOT_RANGE_X,
    HUNTER_SHOOT_RANGE_Y,
    TURRET_BULLET_DAMAGE,
    RELAY_MAX_HP,
)


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


@dataclass
class RelayNode:
    x: float
    y: float
    hp: int = RELAY_MAX_HP
    disabled: bool = False
    pulse: float = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), 14, 20)

    def update(self, dt: float) -> None:
        self.pulse += dt

    def hurt(self, damage: int) -> bool:
        if self.disabled:
            return False
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.disabled = True
        return True


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

    def _blocked_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        check_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        return level.is_solid_pixel(check_x, self.y + 2) or level.is_solid_pixel(check_x, self.y + self.h - 2)

    def _floor_ahead(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        foot_x = self.rect.right + 1 if direction > 0 else self.rect.left - 1
        foot_y = self.y + self.h + 1
        return level.is_solid_pixel(foot_x, foot_y)

    def _ahead_x(self, direction: int, offset: int = 1) -> float:
        return self.rect.right + offset if direction > 0 else self.rect.left - offset

    def _has_headroom_to_jump(self, level: "LevelRuntimeProtocol", direction: int) -> bool:
        sample_y = self.y - 2
        for offset in (3, 7, 11):
            if level.is_solid_pixel(self._ahead_x(direction, offset), sample_y):
                return False
        return True

    def _has_landing_ahead(self, level: "LevelRuntimeProtocol", direction: int, max_forward: int) -> bool:
        step = max(6, TILE_SIZE // 2)
        for forward in range(step, max_forward + step, step):
            sample_x = self._ahead_x(direction, 0) + direction * forward
            for drop in (0, 8, 16, 24, 32, 40, 48):
                if level.is_solid_pixel(sample_x, self.y + self.h + 1 + drop):
                    return True
        return False


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
        self.speed = ENEMY_BASE_SPEED
        self.patrol_speed_factor = ENEMY_PATROL_SPEED_FACTOR
        self.aggro_range = ENEMY_AGGRO_RANGE
        self.jump_power = ENEMY_JUMP_POWER
        self.jump_cd = random.uniform(0.05, ENEMY_JUMP_COOLDOWN)
        self.stuck_timer = 0.0
        self.reposition_timer = 0.0
        self.edge_hold_timer = 0.0
        self.edge_fail_timer = 0.0
        self.turn_cd = 0.0
        self.roam_gap_cd = random.uniform(0.1, ENEMY_ROAM_GAP_COOLDOWN)
        self.chase_memory = 0.0

    def _preferred_direction(
            self,
            level: "LevelRuntimeProtocol",
            player: "Player",
            dx: float,
            dy: float,
    ) -> int | None:
        return None

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: "Player",
        gravity_scale: float = 1.0,
    ) -> None:
        self.jump_cd = max(0.0, self.jump_cd - dt)
        self.reposition_timer = max(0.0, self.reposition_timer - dt)
        self.edge_hold_timer = max(0.0, self.edge_hold_timer - dt)
        self.edge_fail_timer = max(0.0, self.edge_fail_timer - dt)
        self.turn_cd = max(0.0, self.turn_cd - dt)
        self.roam_gap_cd = max(0.0, self.roam_gap_cd - dt)
        self.chase_memory = max(0.0, self.chase_memory - dt)

        player_center_x = player.x + player.w * 0.5
        player_center_y = player.y + player.h * 0.5
        my_center_x = self.x + self.w * 0.5
        my_center_y = self.y + self.h * 0.5
        dx = player_center_x - my_center_x
        dy = player_center_y - my_center_y
        los = level.has_line_of_sight((my_center_x, my_center_y), (player_center_x, player_center_y))
        if abs(dx) <= ENEMY_AGGRO_ENTER_RANGE and abs(dy) <= ENEMY_CHASE_MAX_DY and (los or abs(dy) <= TILE_SIZE):
            self.chase_memory = ENEMY_CHASE_MEMORY
        elif los and abs(dx) <= ENEMY_AGGRO_EXIT_RANGE and abs(dy) <= ENEMY_CHASE_MAX_DY * 1.2:
            self.chase_memory = max(self.chase_memory, ENEMY_CHASE_MEMORY * 0.65)
        elif abs(dx) > ENEMY_AGGRO_EXIT_RANGE * 1.25:
            self.chase_memory = 0.0

        chasing = self.chase_memory > 0.0 and abs(dx) <= self.aggro_range
        hold_position = False

        preferred_direction = self._preferred_direction(level, player, dx, dy)
        if preferred_direction is not None:
            if preferred_direction == 0:
                hold_position = True
                desired_direction = self.direction
            else:
                desired_direction = preferred_direction
        else:
            desired_direction = 1 if dx > 0 else -1

        if chasing and abs(dx) > 2.0 and not hold_position:
            if desired_direction != self.direction:
                if self.turn_cd == 0.0 or not self.on_ground:
                    self.direction = desired_direction
                    self.turn_cd = ENEMY_TURN_COOLDOWN

        blocked = self._blocked_ahead(level, self.direction)
        floor_ahead = self._floor_ahead(level, self.direction)
        player_above = dy < -8.0
        player_ahead = dx * self.direction > 0.0
        near_player = abs(dx) <= TILE_SIZE * 6

        should_jump = False
        if self.on_ground and self.jump_cd == 0.0:
            if blocked and self._has_headroom_to_jump(level, self.direction):
                should_jump = True
            elif (
                    chasing
                    and player_ahead
                    and not floor_ahead
                    and dy < TILE_SIZE * 2
                    and self._has_headroom_to_jump(level, self.direction)
                    and self._has_landing_ahead(level, self.direction, int(ENEMY_GAP_JUMP_PIXELS))
            ):
                should_jump = True
            elif (
                    chasing
                    and player_above
                    and near_player
                    and (blocked or self.reposition_timer == 0.0)
                    and self._has_headroom_to_jump(level, self.direction)
            ):
                should_jump = True

        if should_jump:
            self.vy = -self.jump_power
            self.jump_cd = ENEMY_JUMP_COOLDOWN
            self.reposition_timer = 0.32
            self.edge_hold_timer = 0.0
            self.edge_fail_timer = 0.0
        elif self.on_ground and not floor_ahead:
            safe_drop_or_jump = self._has_landing_ahead(level, self.direction, int(ENEMY_GAP_JUMP_PIXELS))
            if not chasing:
                if safe_drop_or_jump and self.roam_gap_cd == 0.0:
                    self.edge_hold_timer = 0.0
                    self.roam_gap_cd = ENEMY_ROAM_GAP_COOLDOWN
                    self.edge_fail_timer = 0.0
                else:
                    self.direction *= -1
                    self.turn_cd = ENEMY_TURN_COOLDOWN
                    self.edge_fail_timer = 0.0
            else:
                if safe_drop_or_jump and (player_ahead or dy >= ENEMY_EDGE_COMMIT_DY):
                    self.edge_hold_timer = 0.0
                    self.roam_gap_cd = ENEMY_ROAM_GAP_COOLDOWN
                    self.edge_fail_timer = 0.0
                else:
                    self.edge_hold_timer = ENEMY_EDGE_HOLD_TIME
                    self.edge_fail_timer += dt
                    if self.edge_fail_timer >= ENEMY_EDGE_FAIL_TURN_TIME:
                        self.direction *= -1
                        self.turn_cd = ENEMY_TURN_COOLDOWN
                        self.edge_fail_timer = 0.0
                        self.edge_hold_timer = 0.0

        patrol_speed = self.speed * self.patrol_speed_factor
        move_speed = self.speed if chasing else patrol_speed
        self.vx = 0.0 if self.edge_hold_timer > 0.0 or hold_position else self.direction * move_speed
        self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)

        prev_x = self.x
        self.move(level, dt)
        moved = abs(self.x - prev_x)
        if self.on_ground and abs(self.vx) > 0.1 and moved < 0.08:
            self.stuck_timer += dt
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 0.5)

        if self.on_ground and self.stuck_timer >= ENEMY_STUCK_TIME:
            if self.jump_cd == 0.0 and self._has_headroom_to_jump(level, self.direction):
                self.vy = -self.jump_power
                self.jump_cd = ENEMY_JUMP_COOLDOWN
            else:
                self.direction *= -1
                self.turn_cd = ENEMY_TURN_COOLDOWN
            self.stuck_timer = 0.0
            self.reposition_timer = 0.25
            self.edge_hold_timer = 0.0

        self.facing = self.direction


class Hunter(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.hp = 68
        self.max_hp = 68
        self.speed = HUNTER_BASE_SPEED
        self.patrol_speed_factor = HUNTER_PATROL_SPEED_FACTOR
        self.aggro_range = HUNTER_AGGRO_RANGE
        self.jump_power = HUNTER_JUMP_POWER
        self.shot_cd = random.uniform(0.2, 0.9)

    def _preferred_direction(
            self,
            level: "LevelRuntimeProtocol",
            player: "Player",
            dx: float,
            dy: float,
    ) -> int | None:
        origin = (self.x + self.w * 0.5, self.y + self.h * 0.42)
        target = (player.x + player.w * 0.5, player.y + player.h * 0.5)
        if not level.has_line_of_sight(origin, target):
            return None
        if abs(dx) < HUNTER_PREFERRED_MIN_X:
            return -1 if dx > 0 else 1
        if abs(dx) > HUNTER_PREFERRED_MAX_X:
            return 1 if dx > 0 else -1
        return 0

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
        if abs(dx) > HUNTER_SHOOT_RANGE_X or abs(dy) > HUNTER_SHOOT_RANGE_Y:
            return None
        if self.shot_cd > 0.0:
            return None
        if not level.has_line_of_sight((origin_x, origin_y), (target_x, target_y)):
            return None
        self.shot_cd = random.uniform(HUNTER_FIRE_COOLDOWN_MIN, HUNTER_FIRE_COOLDOWN_MAX)
        length = max(1.0, math.hypot(dx, dy))
        speed = 208.0
        return Bullet(origin_x, origin_y, dx / length * speed, dy / length * speed, HUNTER_BULLET_DAMAGE, False)


class MineBot(PhysicsBody):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 12, 12, 34)
        self.direction = random.choice([-1, 1])
        self.speed = MINEBOT_SPEED
        self.fuse = 0.0
        self.aggro_range = MINEBOT_AGGRO_RANGE
        self.jump_power = MINEBOT_JUMP_POWER
        self.jump_cd = random.uniform(0.05, MINEBOT_JUMP_COOLDOWN)
        self.stuck_timer = 0.0

    def update(
        self,
        dt: float,
        level: "LevelRuntimeProtocol",
        player: "Player",
        gravity_scale: float = 1.0,
    ) -> bool:
        self.jump_cd = max(0.0, self.jump_cd - dt)
        player_center_x = player.x + player.w * 0.5
        player_center_y = player.y + player.h * 0.5
        my_center_x = self.x + self.w * 0.5
        my_center_y = self.y + self.h * 0.5
        dx = player_center_x - my_center_x
        dy = player_center_y - my_center_y
        los_to_player = level.has_line_of_sight((my_center_x, my_center_y), (player_center_x, player_center_y))

        if self.fuse > 0.0:
            self.fuse = max(0.0, self.fuse - dt)
            if abs(dx) > 1.5:
                self.direction = 1 if dx > 0 else -1
            self.vx = self.direction * MINEBOT_FUSE_CHASE_SPEED
            if self.on_ground and self.jump_cd == 0.0 and self._blocked_ahead(level,
                                                                              self.direction) and self._has_headroom_to_jump(
                    level, self.direction):
                self.vy = -self.jump_power * 0.9
                self.jump_cd = MINEBOT_JUMP_COOLDOWN * 0.8
            elif self.on_ground and not self._floor_ahead(level, self.direction):
                safe_drop = self._has_landing_ahead(level, self.direction, int(ENEMY_GAP_JUMP_PIXELS))
                if not safe_drop and abs(dy) <= ENEMY_EDGE_COMMIT_DY:
                    self.direction *= -1
            self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
            self.move(level, dt)
            if abs(dx) <= MINEBOT_ARM_RANGE_X * 0.6 and abs(dy) <= MINEBOT_ARM_RANGE_Y * 0.75 and los_to_player:
                self.fuse = min(self.fuse, MINEBOT_MIN_FUSE_NEAR_TARGET)
            return self.fuse == 0.0

        chasing = abs(dx) <= self.aggro_range and abs(dy) <= TILE_SIZE * 5
        if chasing and abs(dx) > 1.5:
            self.direction = 1 if dx > 0 else -1
        if abs(dx) <= MINEBOT_ARM_RANGE_X and abs(dy) <= MINEBOT_ARM_RANGE_Y and los_to_player:
            self.fuse = MINEBOT_FUSE_TIME
            self.vx = 0.0
            return False

        if self.on_ground and self.jump_cd == 0.0 and self._blocked_ahead(level,
                                                                          self.direction) and self._has_headroom_to_jump(
                level, self.direction):
            self.vy = -self.jump_power
            self.jump_cd = MINEBOT_JUMP_COOLDOWN
        elif self.on_ground and not self._floor_ahead(level, self.direction):
            player_far_below = dy >= ENEMY_EDGE_DROP_DY
            safe_drop = self._has_landing_ahead(level, self.direction, int(ENEMY_GAP_JUMP_PIXELS))
            if not chasing or (not player_far_below and not safe_drop):
                self.direction *= -1

        move_speed = self.speed if chasing else self.speed * MINEBOT_PATROL_SPEED_FACTOR
        self.vx = self.direction * move_speed
        self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * gravity_scale * dt)
        prev_x = self.x
        self.move(level, dt)
        moved = abs(self.x - prev_x)
        if self.on_ground and abs(self.vx) > 0.1 and moved < 0.06:
            self.stuck_timer += dt
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 0.5)
        if self.on_ground and self.stuck_timer >= MINEBOT_STUCK_TIME:
            if self.jump_cd == 0.0 and self._has_headroom_to_jump(level, self.direction):
                self.vy = -self.jump_power
                self.jump_cd = MINEBOT_JUMP_COOLDOWN
            else:
                self.direction *= -1
            self.stuck_timer = 0.0
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
        return Bullet(origin_x, origin_y, dx / length * speed, dy / length * speed, TURRET_BULLET_DAMAGE, False)


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
                bullets.append(
                    Bullet(origin_x, origin_y, math.cos(angle) * 210.0, math.sin(angle) * 210.0, BOSS_BULLET_DAMAGE,
                           False)
                )
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
