# project descriptors coverage

source descriptor: `Project Descriptors.docx`

1. includes pygame library: `pyproject.toml` (`pygame-ce`)
2. game initialization: `netrun_platformer/main.py` (`pygame.init()`)
3. sets window size: `netrun_platformer/config.py`
4. displays game window: `netrun_platformer/game.py` (`display.set_mode`, `display.flip`)
5. loads an image: `netrun_platformer/game.py` (`pygame.image.load` splash)
6. uses rgb color scheme: all render modules use rgb tuples
7. determines object coordinates: entities use `x/y`, `rect`, camera offsets
8. brings another surface to screen: HUD surface + tip surface in `draw_play`
9. uses splash screen: `state == "splash"`
10. uses game loop: `Game.run`
11. controls game loop: `self.running`, state machine, fps clock
12. implements correct exit: quit event handling + clean `pygame.quit()`
13. uses frame transitions: fade alpha transition overlay
14. first graphics primitive: `pygame.draw.rect`
15. second graphics primitive: `pygame.draw.line` (also circles/polygons)
16. implements game time management: `self.elapsed`, `clock.tick`, time formatting
17. movement of objects: player/enemy/turret/boss physics updates
18. gets object parameters: hp/position/speed/cooldowns read in logic and ui
19. changes coordinates: physics movement + bullet travel
20. uses mouse event: menu selection and aiming/shoot on click
21. uses keyboard control: movement/jump/shoot/ability/menu
22. interaction checks: collisions (bullets, hazards, enemies, exit, shards)
23. redraws objects with changes: full per-frame rerender
24. non-system font: local ttf loaded via `pygame.font.Font(path_to_ttf, size)`
25. creates graphic text object: all ui labels rendered with font surfaces
26. uses score variables: `self.score`
27. displays points: HUD score text
28. output points/time changes: toast popups + timer in HUD
29. game over screen: `state == "game_over"`
30. demonstrates program works: interactive run + `--headless-smoke`

