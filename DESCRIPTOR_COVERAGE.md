# Аудит дескрипторов (с конкретными строками и сниппетами)

Источник требований: `Project Descriptors.docx`

## 1. Подключена библиотека pygame
Статус: соблюдается.

Файл/строка: `pyproject.toml:7`

```toml
"pygame-ce>=2.5.6",
```

Объяснение: зависимость `pygame-ce` явно зафиксирована в проекте и поднимается через менеджер зависимостей.

## 2. Выполнена инициализация игры
Статус: соблюдается.

Файл/строка: `netrun_platformer/main.py:24`

```python
pygame.init()
```

Объяснение: вызов `pygame.init()` инициализирует подсистемы pygame перед созданием окна и запуском цикла.

## 3. Установлен размер окна
Статус: соблюдается.

Файл/строки: `netrun_platformer/config.py:5-9`

```python
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
WINDOW_SCALE = 4
WINDOW_WIDTH = LOGICAL_WIDTH * WINDOW_SCALE
WINDOW_HEIGHT = LOGICAL_HEIGHT * WINDOW_SCALE
```

Объяснение: размеры окна рассчитываются централизованно и используются при создании display surface.

## 4. Отображается игровое окно
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:31`, `netrun_platformer/game.py:553`

```python
self.window = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT) if headless else (WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.flip()
```

Объяснение: `set_mode` создаёт окно, `display.flip()` показывает собранный кадр пользователю.

## 5. Загружается изображение
Статус: соблюдается.

Файл/строка: `netrun_platformer/game.py:74`

```python
self.splash_image = pygame.image.load(self.splash_path).convert()
```

Объяснение: сплэш-картинка реально загружается с диска, а не рисуется только в runtime.

## 6. Используется RGB-схема цветов
Статус: соблюдается.

Файл/строки: `netrun_platformer/config.py:15-19`

```python
COLOR_BLACK = (6, 8, 12)
COLOR_WHITE = (236, 240, 255)
COLOR_NEON = (26, 210, 202)
COLOR_WARN = (230, 88, 88)
```

Объяснение: цвета определены через RGB(A)-кортежи и затем применяются в рендеринге.

## 7. Определяются координаты объектов
Статус: соблюдается.

Файл/строки: `netrun_platformer/entities.py:45-60`

```python
self.x = x
self.y = y
...
return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
```

Объяснение: у сущностей есть явные координаты `x/y`, а для физики и коллизий формируется `Rect`.

## 8. Выводится дополнительная поверхность на экран
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:450-454`

```python
hud = pygame.Surface((LOGICAL_WIDTH, 26), pygame.SRCALPHA)
pygame.draw.rect(hud, COLOR_HUD, (0, 0, LOGICAL_WIDTH, 26))
self.canvas.blit(hud, (0, 0))
```

Объяснение: отдельная поверхность HUD создаётся отдельно и потом переносится (`blit`) на основной canvas.

## 9. Реализован splash screen
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:35`, `netrun_platformer/game.py:515-516`

```python
self.state = "splash"
...
self.canvas.blit(self.splash_image, (0, 0))
```

Объяснение: стартовое состояние игры — `splash`, где отображается отдельный экран приветствия.

## 10. Реализован игровой цикл
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:106-113`

```python
while self.running:
    dt = min(1 / 24, self.clock.tick(fps) / 1000.0)
    self.handle_events()
    self.update(dt)
    self.render()
```

Объяснение: классический loop: обработка ввода, апдейт логики и отрисовка в каждом кадре.

## 11. Управление игровым циклом
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:34`, `netrun_platformer/game.py:125-126`

```python
self.running = True
...
if event.type == pygame.QUIT:
    self.running = False
```

Объяснение: цикл контролируется флагом `self.running`, который меняется по системному событию закрытия окна.

## 12. Корректный выход из программы
Статус: соблюдается.

Файл/строки: `netrun_platformer/main.py:33-34`

```python
pygame.quit()
return 0
```

Объяснение: после завершения цикла подсистемы pygame освобождаются через `pygame.quit()`.

## 13. Переходы между кадрами (fade)
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:205`, `netrun_platformer/game.py:543-546`

```python
self.fade_alpha = max(0.0, self.fade_alpha - dt * 420.0)
...
fade.fill((0, 0, 0, int(self.fade_alpha)))
self.canvas.blit(fade, (0, 0))
```

Объяснение: альфа-оверлей плавно уменьшается во времени, создавая визуальный переход.

## 14. Первая графическая примитивная фигура
Статус: соблюдается.

Файл/строка: `netrun_platformer/game.py:451`

```python
pygame.draw.rect(hud, COLOR_HUD, (0, 0, LOGICAL_WIDTH, 26))
```

Объяснение: прямоугольник рисуется примитивом `draw.rect` для панели HUD.

## 15. Вторая графическая примитивная фигура
Статус: соблюдается.

Файл/строка: `netrun_platformer/game.py:453`

```python
pygame.draw.line(hud, (28, 66, 84), (0, 25), (LOGICAL_WIDTH, 25), 1)
```

Объяснение: линия примитивом `draw.line` используется как разделитель на HUD.

## 16. Управление игровым временем
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:109`, `netrun_platformer/game.py:223`, `netrun_platformer/utils.py:8-10`

```python
dt = min(1 / 24, self.clock.tick(fps) / 1000.0)
self.elapsed += dt
return f"{total // 60:02d}:{total % 60:02d}"
```

Объяснение: время кадра считается через `clock.tick`, накапливается в `elapsed` и форматируется для UI.

## 17. Движение объектов
Статус: соблюдается.

Файл/строки: `netrun_platformer/entities.py:144-146`, `netrun_platformer/entities.py:153`

```python
self.vx = direction * self.stats.speed
self.vy = min(MAX_FALL_SPEED, self.vy + GRAVITY * dt)
self.move(level, dt)
```

Объяснение: у игрока меняются скорости по осям, затем применяется движение с физикой и коллизиями.

## 18. Получение параметров объектов
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:456-460`

```python
hp_text = f"hp {player.hp}/{player.max_hp}"
score_text = f"score {self.score}"
time_text = f"time {fmt_time(self.elapsed)}"
shard_text = f"shards {shard_count}/{len(self.shards)}"
```

Объяснение: параметры объектов (HP, очки, время, осколки) считываются из состояния и выводятся в интерфейс.

## 19. Изменение координат объектов
Статус: соблюдается.

Файл/строки: `netrun_platformer/entities.py:27-29`, `netrun_platformer/entities.py:99-101`

```python
self.x += self.vx * dt
self.y += self.vy * dt
...
self.x += step
self.y += step
```

Объяснение: координаты изменяются как в непрерывной (velocity*dt), так и в пошаговой (pixel-step) физике.

## 20. Используется событие мыши
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:129-130`, `netrun_platformer/game.py:186-188`

```python
elif event.type == pygame.MOUSEBUTTONDOWN:
    self._handle_click(event.button, self.to_canvas(event.pos))
...
self.controls["shoot"] = True
self.pending_mouse_target = (mx, my)
```

Объяснение: клик мыши обрабатывается и используется для стрельбы/наведения и навигации по меню.

## 21. Реализовано управление клавиатурой
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:133-139`

```python
self.controls["left"] = bool(keys[pygame.K_a] or keys[pygame.K_LEFT])
self.controls["right"] = bool(keys[pygame.K_d] or keys[pygame.K_RIGHT])
jump_down = bool(keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP])
if keys[pygame.K_f]:
    self.controls["shoot"] = True
```

Объяснение: состояние клавиш напрямую маппится в игровые действия движения, прыжка и стрельбы.

## 22. Проверки взаимодействий объектов
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:294-295`, `netrun_platformer/game.py:329-330`, `netrun_platformer/game.py:336`

```python
if bullet.rect.colliderect(enemy.rect):
    enemy.hp -= bullet.damage
...
if bullet.rect.colliderect(player.rect):
...
if not shard.taken and player.rect.colliderect(shard.rect):
```

Объяснение: взаимодействия реализованы через `colliderect` для пуль, врагов, игрока и предметов.

## 23. Перерисовка объектов с учётом изменений
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:112`, `netrun_platformer/game.py:530-553`

```python
self.render()
...
self.canvas.fill(COLOR_BLACK)
...
pygame.display.flip()
```

Объяснение: в каждом тике выполняется полный рендер кадра и вывод на экран.

## 24. Использование несистемного шрифта
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:67-70`

```python
self.font_path = Path(pygame.__file__).with_name("freesansbold.ttf")
self.font_small = pygame.font.Font(self.font_path, 10)
self.font_medium = pygame.font.Font(self.font_path, 14)
```

Объяснение: шрифт подгружается из TTF-файла, а не через `SysFont`.

## 25. Создание графического текстового объекта
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:364`, `netrun_platformer/game.py:372`

```python
rendered = font.render(text, True, color)
self.canvas.blit(rendered, rect)
```

Объяснение: текст превращается в surface (`render`) и затем рисуется на canvas (`blit`).

## 26. Используются переменные очков
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:47`, `netrun_platformer/game.py:195`

```python
self.score = 0
...
self.score += points
```

Объяснение: счёт хранится в состоянии игры и обновляется при игровых событиях.

## 27. Выводятся очки на экран
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:457`, `netrun_platformer/game.py:463`

```python
score_text = f"score {self.score}"
self.draw_text(score_text, self.font_small, COLOR_WHITE, (98, 13))
```

Объяснение: текущее значение очков явно попадает в HUD каждый кадр.

## 28. Вывод изменений очков и времени
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:196`, `netrun_platformer/game.py:458`, `netrun_platformer/game.py:490`

```python
self.toast = f"+{points} {label}"
time_text = f"time {fmt_time(self.elapsed)}"
self.draw_text(self.toast, self.font_small, COLOR_NEON, (LOGICAL_WIDTH - 6, 30), align="right")
```

Объяснение: изменения очков показываются через всплывающий `toast`, время выводится как динамический таймер.

## 29. Экран Game Over
Статус: соблюдается.

Файл/строки: `netrun_platformer/game.py:266`, `netrun_platformer/game.py:538-539`

```python
self.state = "game_over"
...
elif self.state == "game_over":
    self.draw_end("game over", "your signal got burned.")
```

Объяснение: при смерти игрока состояние переключается на `game_over`, и рисуется отдельный финальный экран.

## 30. Демонстрация работоспособности программы
Статус: соблюдается.

Файл/строки: `netrun_platformer/main.py:20-30`

```python
if args.headless_smoke:
    ...
    game.run(fps=FPS, max_frames=150)
    print("smoke ok")
```

Объяснение: есть автоматизированный smoke-режим, который прогоняет игровой цикл и подтверждает успешный запуск.
