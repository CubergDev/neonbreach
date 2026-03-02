# neon breach

hacker-ish 2d platformer built with `pygame-ce`, inspired by arcade cyberpunk action.

## story
null sector hijacked the city kernel and locked every district behind military-grade firewalls.  
you play as **kade zero**, an ex-netrunner on a one-run mission: break 5 districts, kill the defense ai, and steal the root key to free the network.

## playable characters
- `ghost` (glass cannon): low hp, high dps, **phase dash** (short invulnerable burst).
- `bulwark` (tank): high hp, lower dps, **firewall shell** (temporary damage reduction aura).

## level mechanics
- level 1: stable grid (baseline run to learn controls)
- level 2: **thermal surge** (hazard tiles periodically overclock)
- level 3: **signal jam** (short windows where shooting uplink is blocked)
- level 4: **drone wave** (reinforcement enemies keep dropping in)
- level 5: **gravity flux** (alternating low/high gravity in the citadel)

## interactive enemies
- `drone` (`e`): chases and jumps over obstacles
- `hunter` (`h`): mobile shooter with line-of-sight checks
- `mine bot` (`m`): crawler that arms and explodes near the player
- `turret` (`t`): stationary sentry with aimed projectiles
- `warden king` (`b`): final boss with spread fire and jump pressure

## level flow
- level 1: packet district
- level 2: trace refinery
- level 3: dead channel
- level 4: kernel sprawl
- level 5: root citadel (final boss: warden king)

collect all data shards in each level and then reach the exit gate.

## controls
- move: `a/d` or `left/right`
- jump: `space` / `w` / `up`
- shoot: `f` or mouse left-click
- ability: `z` (also `q` / `left shift`)
- menu from run: `esc`
- restart from end screen: `r`

## run with uv
```bash
uv sync
uv run python -m netrun_platformer
```

optional headless smoke test:
```bash
uv run python -m netrun_platformer --headless-smoke
```
