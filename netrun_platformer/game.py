from __future__ import annotations

import math
import random
from pathlib import Path

import pygame

from netrun_platformer.assets import PixelBank, SoundBank, ensure_splash_image
from netrun_platformer.config import (
    ARCHETYPES,
    COLOR_BLACK,
    COLOR_HUD,
    COLOR_NEON,
    COLOR_WARN,
    COLOR_WHITE,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_SCALE,
    WINDOW_WIDTH,
)
from netrun_platformer.entities import Boss, Bullet, DataShard, Enemy, Hunter, MineBot, Player, Turret
from netrun_platformer.levels import LEVELS
from netrun_platformer.utils import clamp, fmt_time
from netrun_platformer.world import LevelRuntime


class Game:
    def __init__(self, headless: bool = False) -> None:
        self.headless = headless
        self.window = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT) if headless else (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "splash"
        self.selected = "ghost"
        self.splash_timer = 0.0
        self.level_index = 0
        self.level: LevelRuntime | None = None
        self.player: Player | None = None
        self.enemies: list[Enemy] = []
        self.hunters: list[Hunter] = []
        self.turrets: list[Turret] = []
        self.mines: list[MineBot] = []
        self.shards: list[DataShard] = []
        self.boss: Boss | None = None
        self.player_bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []
        self.reinforcement_points: list[tuple[float, float]] = []
        self.score = 0
        self.elapsed = 0.0
        self.fade_alpha = 255.0
        self.level_clear_timer = 0.0
        self.toast = ""
        self.toast_timer = 0.0
        self.brief_timer = 0.0
        self.mechanic_timer = 0.0
        self.mechanic_label = ""
        self.reinforce_cd = 0.0
        self.jam_notice_cd = 0.0
        self.gravity_scale = 1.0
        self.hazard_damage = 14
        self.shoot_locked = False
        self.controls = {"left": False, "right": False, "jump": False, "shoot": False, "ability": False}
        self.jump_held = False
        self.pending_mouse_target: tuple[float, float] | None = None
        self.menu_cards = {
            "ghost": pygame.Rect(24, 70, 132, 66),
            "bulwark": pygame.Rect(164, 70, 132, 66),
        }
        self.menu_start = pygame.Rect(106, 150, 108, 20)

        self.pixels = PixelBank()
        self.sfx = SoundBank()

        # load a local ttf file so this is explicitly non-system font usage.
        self.font_path = Path(pygame.__file__).with_name("freesansbold.ttf")
        self.font_small = pygame.font.Font(self.font_path, 10)
        self.font_medium = pygame.font.Font(self.font_path, 14)
        self.font_big = pygame.font.Font(self.font_path, 20)

        self.splash_path = Path(__file__).resolve().parent / "assets" / "images" / "splash.png"
        ensure_splash_image(self.splash_path)
        self.splash_image = pygame.image.load(self.splash_path).convert()

    def start_run(self) -> None:
        self.score = 0
        self.elapsed = 0.0
        self.level_index = 0
        self.load_level(0)
        self.state = "playing"
        self.fade_alpha = 255.0

    def load_level(self, index: int) -> None:
        self.level_index = index
        self.level = LevelRuntime(LEVELS[index])
        archetype = ARCHETYPES[self.selected]
        self.player = Player(self.level.player_spawn[0], self.level.player_spawn[1], archetype, self.selected)
        self.enemies = [Enemy(x, y) for x, y in self.level.enemy_spawns]
        self.hunters = [Hunter(x, y) for x, y in self.level.hunter_spawns]
        self.turrets = [Turret(x, y) for x, y in self.level.turret_spawns]
        self.mines = [MineBot(x, y) for x, y in self.level.mine_spawns]
        self.shards = [DataShard(x, y) for x, y in self.level.shard_spawns]
        self.boss = Boss(*self.level.boss_spawn) if self.level.boss_spawn else None
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.reinforcement_points = list(self.level.enemy_spawns + self.level.hunter_spawns + self.level.turret_spawns)
        self.level_clear_timer = 0.0
        self.brief_timer = 3.0
        self.toast = self.level.spec.objective
        self.toast_timer = 2.2
        self.mechanic_timer = 0.0
        self.mechanic_label = self.level.spec.mechanic_hint
        self.reinforce_cd = 4.5
        self.jam_notice_cd = 0.0
        self.gravity_scale = 1.0
        self.hazard_damage = 14
        self.shoot_locked = False
        self.fade_alpha = 255.0

    def to_canvas(self, pos: tuple[int, int]) -> tuple[int, int]:
        if self.headless:
            return pos
        return pos[0] // WINDOW_SCALE, pos[1] // WINDOW_SCALE

    def run(self, fps: int, max_frames: int = 0) -> None:
        frames = 0
        while self.running:
            dt = min(1 / 24, self.clock.tick(fps) / 1000.0)
            self.handle_events()
            self.update(dt)
            self.render()
            frames += 1
            if max_frames and frames >= max_frames:
                break

    def handle_events(self) -> None:
        was_playing = self.state == "playing"
        self.controls["jump"] = False
        self.controls["shoot"] = False
        self.controls["ability"] = False
        self.pending_mouse_target = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.button, self.to_canvas(event.pos))

        keys = pygame.key.get_pressed()
        self.controls["left"] = bool(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.controls["right"] = bool(keys[pygame.K_d] or keys[pygame.K_RIGHT])
        jump_down = bool(keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP])
        self.controls["jump"] = was_playing and jump_down and not self.jump_held
        self.jump_held = jump_down
        if keys[pygame.K_f]:
            self.controls["shoot"] = True
        if keys[pygame.K_z] or keys[pygame.K_q] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.controls["ability"] = True

    def _handle_keydown(self, key: int) -> None:
        if self.state == "splash":
            self.state = "menu"
            self.fade_alpha = 255.0
            return
        if self.state == "menu":
            if key == pygame.K_1:
                self.selected = "ghost"
            elif key == pygame.K_2:
                self.selected = "bulwark"
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            return
        if self.state == "playing":
            if key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.controls["jump"] = True
            elif key in (pygame.K_z, pygame.K_q, pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.controls["ability"] = True
            elif key == pygame.K_f:
                self.controls["shoot"] = True
            elif key == pygame.K_ESCAPE:
                self.state = "menu"
                self.fade_alpha = 255.0
            return
        if self.state in ("game_over", "victory"):
            if key == pygame.K_r:
                self.start_run()
            elif key == pygame.K_m:
                self.state = "menu"
                self.fade_alpha = 255.0

    def _handle_click(self, button: int, pos: tuple[int, int]) -> None:
        mx, my = pos
        if self.state == "splash":
            self.state = "menu"
            self.fade_alpha = 255.0
            return
        if self.state == "menu" and button == 1:
            if self.menu_cards["ghost"].collidepoint(mx, my):
                self.selected = "ghost"
            elif self.menu_cards["bulwark"].collidepoint(mx, my):
                self.selected = "bulwark"
            elif self.menu_start.collidepoint(mx, my):
                self.start_run()
            return
        if self.state == "playing" and button == 1:
            self.controls["shoot"] = True
            self.pending_mouse_target = (mx, my)
            return
        if self.state in ("game_over", "victory") and button == 1:
            self.state = "menu"
            self.fade_alpha = 255.0

    def add_score(self, points: int, label: str) -> None:
        self.score += points
        self.toast = f"+{points} {label}"
        self.toast_timer = 1.2

    def exit_ready(self) -> bool:
        shards_done = all(shard.taken for shard in self.shards)
        boss_done = self.boss is None or self.boss.hp <= 0
        return shards_done and boss_done

    def _spawn_reinforcement(self, level: LevelRuntime, player: Player) -> bool:
        active_count = len(self.enemies) + len(self.hunters) + len(self.turrets) + len(self.mines)
        if active_count >= 22:
            return False
        points = self.reinforcement_points
        if not points:
            spawn_x = clamp(player.x + random.choice([-120.0, 120.0]), 6, max(6, level.pixel_width - 24))
            spawn_y = clamp(player.y - 42.0, 6, max(6, level.pixel_height - 24))
        else:
            spawn_x, spawn_y = random.choice(points)
        player_center_x = player.x + player.w * 0.5
        player_center_y = player.y + player.h * 0.5
        if abs(spawn_x - player_center_x) < 28 and abs(spawn_y - player_center_y) < 24:
            spawn_x = clamp(spawn_x + random.choice([-52.0, 52.0]), 6, max(6, level.pixel_width - 24))
        roll = random.random()
        if roll < 0.45:
            self.enemies.append(Enemy(spawn_x, spawn_y))
        elif roll < 0.8:
            self.hunters.append(Hunter(spawn_x, spawn_y))
        else:
            self.mines.append(MineBot(spawn_x, spawn_y))
        return True

    def _update_level_mechanics(self, level: LevelRuntime, player: Player, dt: float) -> None:
        self.mechanic_timer += dt
        self.jam_notice_cd = max(0.0, self.jam_notice_cd - dt)
        self.gravity_scale = 1.0
        self.hazard_damage = 14
        self.shoot_locked = False
        self.mechanic_label = level.spec.mechanic_hint
        mechanic = level.spec.mechanic

        if mechanic == "thermal_surge":
            cycle = self.mechanic_timer % 7.2
            surge_active = cycle >= 4.6
            if surge_active:
                self.hazard_damage = 26
                self.mechanic_label = "thermal surge: traps boosted"
            else:
                self.mechanic_label = f"thermal surge in {4.6 - cycle:0.1f}s"
            return

        if mechanic == "signal_jam":
            cycle = self.mechanic_timer % 6.0
            self.shoot_locked = cycle < 2.1
            self.mechanic_label = "signal jam: uplink blocked" if self.shoot_locked else "signal stable: uplink clear"
            return

        if mechanic == "drone_wave":
            self.reinforce_cd = max(0.0, self.reinforce_cd - dt)
            self.mechanic_label = f"drone wave in {self.reinforce_cd:0.1f}s"
            if self.reinforce_cd == 0.0:
                if self._spawn_reinforcement(level, player):
                    self.toast = "reinforcement drop detected"
                    self.toast_timer = 1.2
                self.reinforce_cd = 6.0 + random.random() * 1.5
            return

        if mechanic == "gravity_flux":
            cycle = self.mechanic_timer % 6.4
            heavy = cycle >= 3.2
            self.gravity_scale = 1.35 if heavy else 0.72
            self.mechanic_label = "gravity flux: heavy pull" if heavy else "gravity flux: low pull"

    def update(self, dt: float) -> None:
        self.fade_alpha = max(0.0, self.fade_alpha - dt * 420.0)
        self.toast_timer = max(0.0, self.toast_timer - dt)

        if self.state == "splash":
            self.splash_timer += dt
            if self.splash_timer > 2.4:
                self.state = "menu"
                self.fade_alpha = 255.0
            return

        if self.state != "playing":
            return

        level = self.level
        player = self.player
        if level is None or player is None:
            return

        self.elapsed += dt
        self.brief_timer = max(0.0, self.brief_timer - dt)
        self._update_level_mechanics(level, player, dt)
        player.update(dt, level, self.controls, gravity_scale=self.gravity_scale)

        if level.rect_hits_hazard(player.rect):
            if player.hurt(self.hazard_damage):
                self.sfx.play("hit")

        if self.controls["ability"] and player.ability_timer == player.stats.ability_duration:
            self.sfx.play("ability")
        if player.just_jumped:
            self.sfx.play("jump")

        if self.controls["shoot"] and self.shoot_locked:
            if self.jam_notice_cd == 0.0:
                self.toast = "signal jam: fire channel blocked"
                self.toast_timer = 0.6
                self.jam_notice_cd = 0.6
        elif self.controls["shoot"]:
            target_world = None
            if self.pending_mouse_target is not None:
                camera = self.camera()
                target_world = (self.pending_mouse_target[0] + camera[0], self.pending_mouse_target[1] + camera[1])
            shot = player.shoot(target_world)
            if shot is not None:
                self.player_bullets.append(shot)
                self.sfx.play("shoot")

        for enemy in self.enemies:
            enemy.update(dt, level, player, gravity_scale=self.gravity_scale)
            if enemy.rect.colliderect(player.rect) and player.hurt(16):
                self.sfx.play("hit")

        for hunter in self.hunters:
            projectile = hunter.update(dt, level, player, gravity_scale=self.gravity_scale)
            if projectile:
                self.enemy_bullets.append(projectile)
            if hunter.rect.colliderect(player.rect) and player.hurt(18):
                self.sfx.play("hit")

        for mine in list(self.mines):
            if mine.rect.colliderect(player.rect) and mine.fuse == 0.0:
                mine.fuse = 0.35
            exploded = mine.update(dt, level, player, gravity_scale=self.gravity_scale)
            if exploded:
                distance = math.hypot(
                    (mine.x + mine.w * 0.5) - (player.x + player.w * 0.5),
                    (mine.y + mine.h * 0.5) - (player.y + player.h * 0.5),
                )
                if distance <= 28 and player.hurt(26):
                    self.sfx.play("hit")
                self.mines.remove(mine)
                self.sfx.play("boss")

        for turret in self.turrets:
            projectile = turret.update(dt, player, level)
            if projectile:
                self.enemy_bullets.append(projectile)

        if self.boss and self.boss.hp > 0:
            if self.boss.rect.colliderect(player.rect) and player.hurt(22):
                self.sfx.play("hit")
            self.enemy_bullets.extend(self.boss.update(dt, level, player, gravity_scale=self.gravity_scale))

        self._update_player_bullets(level, dt)
        self._update_enemy_bullets(level, player, dt)
        self._collect_shards(player)

        if player.hp <= 0:
            self.state = "game_over"
            self.fade_alpha = 255.0
            self.sfx.play("dead")
            return

        if player.rect.colliderect(level.exit_rect) and self.exit_ready():
            self.level_clear_timer += dt
            if self.level_clear_timer > 0.35:
                bonus = max(0, int(850 - self.elapsed * 2.6))
                self.add_score(bonus, "time bonus")
                self.sfx.play("clear")
                if self.level_index + 1 >= len(LEVELS):
                    self.state = "victory"
                    self.fade_alpha = 255.0
                else:
                    self.load_level(self.level_index + 1)
        else:
            self.level_clear_timer = 0.0

    def _update_player_bullets(self, level: LevelRuntime, dt: float) -> None:
        for bullet in list(self.player_bullets):
            bullet.update(dt)
            if bullet.ttl <= 0.0 or level.rect_hits_solid(bullet.rect):
                self.player_bullets.remove(bullet)
                continue

            hit = False
            for enemy in list(self.enemies):
                if bullet.rect.colliderect(enemy.rect):
                    enemy.hp -= bullet.damage
                    hit = True
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        self.add_score(120, "drone")
                    break

            if not hit:
                for turret in list(self.turrets):
                    if bullet.rect.colliderect(turret.rect):
                        turret.hp -= bullet.damage
                        hit = True
                        if turret.hp <= 0:
                            self.turrets.remove(turret)
                            self.add_score(150, "turret")
                        break

            if not hit:
                for hunter in list(self.hunters):
                    if bullet.rect.colliderect(hunter.rect):
                        hunter.hp -= bullet.damage
                        hit = True
                        if hunter.hp <= 0:
                            self.hunters.remove(hunter)
                            self.add_score(180, "hunter")
                        break

            if not hit:
                for mine in list(self.mines):
                    if bullet.rect.colliderect(mine.rect):
                        mine.hp -= bullet.damage
                        hit = True
                        if mine.hp <= 0:
                            self.mines.remove(mine)
                            self.add_score(110, "mine bot")
                        else:
                            mine.fuse = min(mine.fuse if mine.fuse > 0 else 0.4, 0.4)
                        break

            if not hit and self.boss and self.boss.hp > 0 and bullet.rect.colliderect(self.boss.rect):
                self.boss.hp -= bullet.damage
                hit = True
                if self.boss.hp <= 0:
                    self.add_score(1400, "warden king")
                    self.sfx.play("boss")

            if hit:
                self.player_bullets.remove(bullet)
                self.sfx.play("hit")

    def _update_enemy_bullets(self, level: LevelRuntime, player: Player, dt: float) -> None:
        for bullet in list(self.enemy_bullets):
            bullet.update(dt)
            if bullet.ttl <= 0.0 or level.rect_hits_solid(bullet.rect):
                self.enemy_bullets.remove(bullet)
                continue
            if bullet.rect.colliderect(player.rect):
                if player.hurt(bullet.damage):
                    self.sfx.play("hit")
                self.enemy_bullets.remove(bullet)

    def _collect_shards(self, player: Player) -> None:
        for shard in self.shards:
            if not shard.taken and player.rect.colliderect(shard.rect):
                shard.taken = True
                self.add_score(250, "shard")
                self.sfx.play("pickup")

    def camera(self) -> tuple[int, int]:
        if self.level is None or self.player is None:
            return 0, 0
        cam_x = int(self.player.x + self.player.w * 0.5 - LOGICAL_WIDTH * 0.5)
        cam_y = int(self.player.y + self.player.h * 0.5 - LOGICAL_HEIGHT * 0.58)
        cam_x = int(clamp(cam_x, 0, max(0, self.level.pixel_width - LOGICAL_WIDTH)))
        cam_y = int(clamp(cam_y, 0, max(0, self.level.pixel_height - LOGICAL_HEIGHT)))
        return cam_x, cam_y

    def draw_background(self, top: tuple[int, int, int], bottom: tuple[int, int, int], elapsed: float) -> None:
        for y in range(LOGICAL_HEIGHT):
            blend = y / LOGICAL_HEIGHT
            color = (
                int(top[0] * (1 - blend) + bottom[0] * blend),
                int(top[1] * (1 - blend) + bottom[1] * blend),
                int(top[2] * (1 - blend) + bottom[2] * blend),
            )
            pygame.draw.line(self.canvas, color, (0, y), (LOGICAL_WIDTH, y))
        offset = int((elapsed * 20) % 32)
        for x in range(-32, LOGICAL_WIDTH + 32, 32):
            pygame.draw.line(self.canvas, (18, 42, 62), (x + offset, 0), (x + offset - 24, LOGICAL_HEIGHT), 1)

    def draw_text(self, text: str, font: pygame.font.Font, color: tuple[int, int, int], pos: tuple[int, int], align: str = "left") -> None:
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        if align == "center":
            rect.center = pos
        elif align == "right":
            rect.topright = pos
        else:
            rect.topleft = pos
        self.canvas.blit(rendered, rect)

    def draw_actor(
        self,
        image: pygame.Surface,
        x: float,
        y: float,
        camera: tuple[int, int],
        facing: int,
        y_offset: int = 0,
    ) -> None:
        sprite = pygame.transform.flip(image, facing < 0, False)
        self.canvas.blit(sprite, (int(x) - camera[0], int(y) + y_offset - camera[1]))

    def draw_play(self) -> None:
        level = self.level
        player = self.player
        if level is None or player is None:
            return
        camera = self.camera()
        self.draw_background(level.spec.sky_top, level.spec.sky_bottom, self.elapsed)
        level.draw(self.canvas, camera[0], camera[1], self.pixels)

        for shard in self.shards:
            if shard.taken:
                continue
            frame = self.pixels.shard_frames[int(self.elapsed * 8) % len(self.pixels.shard_frames)]
            phase = shard.x * 0.09 + shard.y * 0.07
            offset = int(math.sin(self.elapsed * 4.2 + phase) * 2)
            x = int(shard.x) - camera[0]
            y = int(shard.y) + offset - camera[1]
            pulse = 0.5 + 0.5 * math.sin(self.elapsed * 6.0 + phase)
            glow_radius = 8 + int(pulse * 3)
            glow_alpha = 48 + int(pulse * 82)
            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (74, 240, 226, glow_alpha), (glow_radius, glow_radius), glow_radius)
            self.canvas.blit(
                glow,
                (
                    x + frame.get_width() // 2 - glow_radius,
                    y + frame.get_height() // 2 - glow_radius,
                ),
            )
            self.canvas.blit(frame, (x, y))

        door_sprite = self.pixels.exit_open if self.exit_ready() else self.pixels.exit_locked
        self.canvas.blit(door_sprite, (level.exit_rect.x - camera[0], level.exit_rect.y - camera[1]))

        for enemy in self.enemies:
            phase = enemy.x * 0.06
            frame = self.pixels.enemy[int(self.elapsed * 8 + phase * 3) % len(self.pixels.enemy)]
            bob = int(math.sin(self.elapsed * 5.4 + phase) * 1.8)
            self.draw_actor(frame, enemy.x, enemy.y, camera, enemy.facing, y_offset=bob)

        for hunter in self.hunters:
            phase = hunter.x * 0.05
            frame = self.pixels.hunter[int(self.elapsed * 9 + phase * 4) % len(self.pixels.hunter)]
            bob = int(math.sin(self.elapsed * 6.2 + phase) * 1.4)
            self.draw_actor(frame, hunter.x, hunter.y, camera, hunter.facing, y_offset=bob)

        for mine in self.mines:
            frame = self.pixels.mine[int(self.elapsed * 7) % len(self.pixels.mine)]
            x = int(mine.x) - camera[0]
            y = int(mine.y) - camera[1]
            if mine.fuse > 0.0:
                pulse = 120 + int(abs(math.sin(self.elapsed * 18.0)) * 110)
                glow = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow, (240, 70, 70, pulse), (10, 10), 8)
                self.canvas.blit(glow, (x - 4, y - 4))
            self.canvas.blit(frame, (x, y))

        for turret in self.turrets:
            phase = turret.x * 0.05
            frame = self.pixels.turret[int(self.elapsed * 5 + phase * 2) % len(self.pixels.turret)]
            bob = int(math.sin(self.elapsed * 3.0 + phase) * 1.2)
            self.draw_actor(frame, turret.x, turret.y, camera, turret.facing, y_offset=bob)

        if self.boss and self.boss.hp > 0:
            phase = self.boss.x * 0.02
            frame = self.pixels.boss[int(self.elapsed * 4 + phase) % len(self.pixels.boss)]
            bob = int(math.sin(self.elapsed * 2.2 + phase) * 2.0)
            self.draw_actor(frame, self.boss.x, self.boss.y, camera, self.boss.facing, y_offset=bob)

        for bullet in self.player_bullets:
            self.canvas.blit(self.pixels.bullet_player, (int(bullet.x) - camera[0] - 2, int(bullet.y) - camera[1] - 2))
        for bullet in self.enemy_bullets:
            self.canvas.blit(self.pixels.bullet_enemy, (int(bullet.x) - camera[0] - 2, int(bullet.y) - camera[1] - 2))

        anim = player.animation()
        frames = self.pixels.player[player.kind][anim]
        frame = frames[int(self.elapsed * (8 if anim == "run" else 4)) % len(frames)]
        player_bob = 0 if anim == "jump" else int(math.sin(self.elapsed * 8.5) * 1.0)
        self.draw_actor(frame, player.x, player.y, camera, player.facing, y_offset=player_bob)

        # primitive #1
        hud = pygame.Surface((LOGICAL_WIDTH, 26), pygame.SRCALPHA)
        pygame.draw.rect(hud, COLOR_HUD, (0, 0, LOGICAL_WIDTH, 26))
        # primitive #2
        pygame.draw.line(hud, (28, 66, 84), (0, 25), (LOGICAL_WIDTH, 25), 1)
        self.canvas.blit(hud, (0, 0))

        hp_text = f"hp {player.hp}/{player.max_hp}"
        score_text = f"score {self.score}"
        time_text = f"time {fmt_time(self.elapsed)}"
        shard_count = sum(1 for shard in self.shards if shard.taken)
        shard_text = f"shards {shard_count}/{len(self.shards)}"
        self.draw_text(level.spec.name, self.font_small, COLOR_WHITE, (4, 2))
        self.draw_text(hp_text, self.font_small, COLOR_WHITE, (4, 13))
        self.draw_text(score_text, self.font_small, COLOR_WHITE, (98, 13))
        self.draw_text(time_text, self.font_small, COLOR_WHITE, (170, 13))
        self.draw_text(shard_text, self.font_small, COLOR_WHITE, (244, 13))

        if self.boss and self.boss.hp > 0:
            self.draw_text(f"warden king {self.boss.hp}", self.font_small, COLOR_WARN, (160, 34), align="center")

        if player.kind == "ghost" and player.ability_active():
            ability_text = "phase dash active"
        elif player.kind == "bulwark" and player.ability_active():
            ability_text = "firewall shell active"
        elif player.ability_cd == 0.0:
            ability_text = "ability [z] ready"
        else:
            ability_text = f"ability [z] cd {player.ability_cd:0.1f}s"
        self.draw_text(ability_text, self.font_small, COLOR_NEON, (LOGICAL_WIDTH - 4, 2), align="right")

        if player.kind == "bulwark" and player.ability_active():
            pygame.draw.circle(
                self.canvas,
                (60, 210, 188),
                (int(player.x + player.w * 0.5 - camera[0]), int(player.y + player.h * 0.5 - camera[1])),
                12,
                1,
            )
        if self.mechanic_label:
            self.draw_text(self.mechanic_label, self.font_small, COLOR_NEON, (LOGICAL_WIDTH - 4, 36), align="right")

        if self.brief_timer > 0.0:
            tip = pygame.Surface((LOGICAL_WIDTH - 20, 38), pygame.SRCALPHA)
            pygame.draw.rect(tip, (8, 12, 20, 220), (0, 0, tip.get_width(), tip.get_height()))
            pygame.draw.rect(tip, (50, 110, 140), (0, 0, tip.get_width(), tip.get_height()), 1)
            tip.blit(self.font_small.render(level.spec.objective, True, COLOR_WHITE), (8, 6))
            if level.spec.mechanic_hint:
                tip.blit(self.font_small.render(level.spec.mechanic_hint, True, COLOR_NEON), (8, 20))
            self.canvas.blit(tip, (10, LOGICAL_HEIGHT - 48))

        if self.toast_timer > 0.0 and self.toast:
            self.draw_text(self.toast, self.font_small, COLOR_NEON, (LOGICAL_WIDTH - 6, 30), align="right")

    def draw_menu(self) -> None:
        self.draw_background((6, 16, 28), (14, 30, 48), self.elapsed)
        self.draw_text("neon breach", self.font_big, COLOR_WHITE, (LOGICAL_WIDTH // 2, 20), align="center")
        self.draw_text("story: null sector hijacked the city kernel.", self.font_small, COLOR_WHITE, (LOGICAL_WIDTH // 2, 42), align="center")
        self.draw_text("clear 5 districts and steal the root key.", self.font_small, COLOR_WHITE, (LOGICAL_WIDTH // 2, 54), align="center")

        for key, rect in self.menu_cards.items():
            active = self.selected == key
            border = (58, 220, 188) if active else (46, 78, 96)
            fill = (14, 20, 30) if active else (10, 14, 22)
            pygame.draw.rect(self.canvas, fill, rect)
            pygame.draw.rect(self.canvas, border, rect, 1)
            archetype = ARCHETYPES[key]
            self.draw_text(f"{archetype.codename} ({archetype.label})", self.font_small, COLOR_WHITE, (rect.x + 6, rect.y + 6))
            self.draw_text(f"hp {archetype.max_hp}", self.font_small, COLOR_WHITE, (rect.x + 6, rect.y + 20))
            self.draw_text(f"dmg {archetype.bullet_damage}", self.font_small, COLOR_WHITE, (rect.x + 6, rect.y + 30))
            self.draw_text(archetype.ability_name, self.font_small, COLOR_NEON, (rect.x + 6, rect.y + 44))

        pygame.draw.rect(self.canvas, (16, 28, 44), self.menu_start)
        pygame.draw.rect(self.canvas, (66, 180, 200), self.menu_start, 1)
        self.draw_text("start run", self.font_small, COLOR_WHITE, self.menu_start.center, align="center")
        self.draw_text("1/2 pick, enter start, z ability", self.font_small, COLOR_WHITE, (LOGICAL_WIDTH // 2, 170), align="center")

    def draw_splash(self) -> None:
        self.canvas.blit(self.splash_image, (0, 0))
        title = self.font_big.render("neon breach", True, COLOR_WHITE)
        self.canvas.blit(title, title.get_rect(center=(LOGICAL_WIDTH // 2, 78)))
        subtitle = self.font_small.render("click or press any key to jack in", True, (170, 220, 240))
        self.canvas.blit(subtitle, subtitle.get_rect(center=(LOGICAL_WIDTH // 2, 102)))

    def draw_end(self, title: str, subtitle: str) -> None:
        self.draw_background((8, 8, 16), (14, 16, 26), self.elapsed)
        self.draw_text(title, self.font_big, COLOR_WHITE, (LOGICAL_WIDTH // 2, 56), align="center")
        self.draw_text(subtitle, self.font_small, COLOR_WHITE, (LOGICAL_WIDTH // 2, 82), align="center")
        self.draw_text(f"score {self.score}", self.font_medium, COLOR_NEON, (LOGICAL_WIDTH // 2, 108), align="center")
        self.draw_text(f"time {fmt_time(self.elapsed)}", self.font_medium, COLOR_WHITE, (LOGICAL_WIDTH // 2, 126), align="center")
        self.draw_text("press r to restart or m/click for menu", self.font_small, COLOR_WHITE, (LOGICAL_WIDTH // 2, 154), align="center")

    def render(self) -> None:
        self.canvas.fill(COLOR_BLACK)
        if self.state == "splash":
            self.draw_splash()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_play()
        elif self.state == "game_over":
            self.draw_end("game over", "your signal got burned.")
        elif self.state == "victory":
            self.draw_end("city unlocked", "root key extracted. null sector is offline.")

        if self.fade_alpha > 0.0:
            fade = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(self.fade_alpha)))
            self.canvas.blit(fade, (0, 0))

        if self.headless:
            self.window.blit(self.canvas, (0, 0))
        else:
            scaled = pygame.transform.scale(self.canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.window.blit(scaled, (0, 0))
        pygame.display.flip()
