from __future__ import annotations

import argparse
import os

import pygame

from netrun_platformer.config import FPS
from netrun_platformer.game import Game


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="neon breach pygame-ce platformer")
    parser.add_argument("--headless-smoke", action="store_true", help="run a short non-interactive smoke test")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.headless_smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    pygame.init()
    try:
        pygame.display.set_caption("neon breach")
        game = Game(headless=args.headless_smoke)
        if args.headless_smoke:
            game.start_run()
            game.run(fps=FPS, max_frames=150)
            print("smoke ok")
        else:
            game.run(fps=FPS)
    finally:
        pygame.quit()
    return 0
