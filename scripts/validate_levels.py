from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass

import pygame

from netrun_platformer.config import ARCHETYPES
from netrun_platformer.entities import Player
from netrun_platformer.levels import LEVELS
from netrun_platformer.world import LevelRuntime

DT = 1 / 24
MAX_STEPS = 900
ACTIONS = (
    {"left": False, "right": False, "jump": False, "shoot": False, "ability": False},
    {"left": True, "right": False, "jump": False, "shoot": False, "ability": False},
    {"left": False, "right": True, "jump": False, "shoot": False, "ability": False},
    {"left": False, "right": False, "jump": True, "shoot": False, "ability": False},
    {"left": True, "right": False, "jump": True, "shoot": False, "ability": False},
    {"left": False, "right": True, "jump": True, "shoot": False, "ability": False},
)


@dataclass(frozen=True)
class SimState:
    x: float
    y: float
    vy: float
    on_ground: bool


def make_player(level: LevelRuntime, archetype_key: str, state: SimState) -> Player:
    player = Player(level.player_spawn[0], level.player_spawn[1], ARCHETYPES[archetype_key], archetype_key)
    player.x = state.x
    player.y = state.y
    player.vx = 0.0
    player.vy = state.vy
    player.on_ground = state.on_ground
    player.x_rem = 0.0
    player.y_rem = 0.0
    player.jump_buffer = 0.0
    player.just_jumped = False
    player.shoot_cd = 0.0
    player.ability_cd = 0.0
    player.ability_timer = 0.0
    player.invuln_timer = 0.0
    return player


def key_for(player: Player) -> tuple[int, int, int, bool]:
    return (int(round(player.x / 2.0)), int(round(player.y / 2.0)), int(round(player.vy / 24.0)), player.on_ground)


def build_route_targets(level: LevelRuntime) -> list[tuple[str, pygame.Rect]]:
    targets: list[tuple[str, pygame.Rect]] = [("shard", pygame.Rect(int(x), int(y), 10, 12)) for x, y in
                                              level.shard_spawns]
    for x, y in level.relay_spawns:
        targets.append(("relay", pygame.Rect(int(x) - 20, int(y) - 12, 54, 40)))
    targets.sort(key=lambda item: item[1].centerx)
    targets.append(("exit", level.exit_rect.copy()))
    return targets


def reach_target(
        level: LevelRuntime,
        archetype_key: str,
        start_state: SimState,
        target_rect: pygame.Rect,
) -> tuple[bool, SimState, int, int]:
    queue: deque[tuple[SimState, int]] = deque([(start_state, 0)])
    visited: set[tuple[int, int, int, bool]] = set()
    iterations = 0

    while queue:
        state, steps = queue.popleft()
        player = make_player(level, archetype_key, state)
        state_key = key_for(player)
        if state_key in visited:
            continue
        visited.add(state_key)
        iterations += 1

        if player.rect.colliderect(target_rect):
            return True, SimState(player.x, player.y, player.vy, player.on_ground), steps, iterations
        if steps >= MAX_STEPS // 3:
            continue

        for action in ACTIONS:
            next_player = make_player(level, archetype_key, state)
            next_player.update(DT, level, action, gravity_scale=1.0)
            if next_player.y > level.pixel_height + 24:
                continue
            next_state = SimState(next_player.x, next_player.y, next_player.vy, next_player.on_ground)
            next_key = key_for(next_player)
            if next_key in visited:
                continue
            queue.append((next_state, steps + 1))

    return False, start_state, MAX_STEPS // 3, iterations


def solve_level(level_index: int, archetype_key: str) -> tuple[bool, int, int, str]:
    level = LevelRuntime(LEVELS[level_index])
    route_targets = build_route_targets(level)
    start_y = float(level.player_spawn[1])
    on_ground = level.rect_hits_solid(pygame.Rect(int(level.player_spawn[0]), int(start_y), 14, 16).move(0, 1))
    state = SimState(float(level.player_spawn[0]), start_y, 0.0, on_ground)
    total_steps = 0
    total_iterations = 0

    for label, target_rect in route_targets:
        ok, state, steps, iterations = reach_target(level, archetype_key, state, target_rect)
        total_steps += steps
        total_iterations += iterations
        if not ok:
            return False, total_steps, total_iterations, label
    return True, total_steps, total_iterations, "exit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate level traversal with the weakest archetype.")
    parser.add_argument("--archetype", default="bulwark", choices=sorted(ARCHETYPES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = False
    for index, spec in enumerate(LEVELS):
        ok, steps, iterations, last_target = solve_level(index, args.archetype)
        verdict = "ok" if ok else "fail"
        print(f"{verdict}: {spec.name} [{args.archetype}] steps={steps} explored={iterations} target={last_target}")
        if not ok:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
