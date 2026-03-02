# Как быстро делать спрайты, анимации и карты через меня + MCP (под твой проект)

Дата: 2026-02-25

## Короткий вывод

Для твоего текущего `pygame-ce` платформера лучший практичный стек такой:

1. Спрайты и анимации: `pixel-mcp` как основной, `aseprite-mcp` как запасной.
2. Карты: пока не MCP-first, а `Tiled/LDtk -> JSON/TMX -> конвертация в твой формат`.
3. Аудио/SFX: `ffmpeg-mcp` (локально и детерминированно).
4. Голос/озвучка (опционально): `elevenlabs-mcp`.

Если цель именно "быстро и стабильно", ставь в таком порядке:
`pixel-mcp`, `aseprite-mcp`, `ffmpeg-mcp`.  
Для карт делай упор на нативный экспорт Tiled/LDtk, а не на экспериментальные map MCP.

## Что важно про твой текущий код

Сейчас у тебя:

1. Уровни зашиты в `netrun_platformer/levels.py` как ASCII-сетки (`rows`).
2. Логика карты в `netrun_platformer/world.py` читает символы:
`#` solid, `^` hazard, `p` player, `x` exit, `e` enemy, `t` turret, `d` shard, `b` boss.
3. Текущие "спрайты" в `netrun_platformer/assets.py` рисуются процедурно, без внешних PNG/spritesheet.

Это хорошо для быстрого старта, и это же делает миграцию простой:
можно постепенно заменить процедурные спрайты на PNG-анимации, а ASCII-карты генерировать из Tiled/LDtk.

## MCP, которые у тебя уже полезны прямо сейчас

Из `research.md` и текущей среды:

1. `pycharm`  
Лучший для меня канал правки кода, рефакторинга, проверки ошибок, запуска команд в проекте.

2. `context7`  
Быстрый доступ к актуальной документации библиотек (например, по `pygame-ce`, парсерам карт, утилитам).

3. `playwright`  
Для браузерной автоматизации и быстрых проверок UI/сайтов. Для спрайтов и карт почти не нужен.

4. `openaiDeveloperDocs`  
Нужен только для OpenAI API/SDK задач. Для ассетов игры напрямую не нужен.

5. `svelte`  
Не нужен для твоего pygame runtime.

6. `codex_apps`  
Контейнер для доп. коннекторов, но не ядро твоего asset pipeline.

7. `figma` (есть в текущей среде)  
Полезен, если делаешь UI/макеты в Figma и хочешь перевод в код, но это не главный путь для pixel-art спрайтов/карт.

Отдельно: локально через CLI у тебя пока не добавлены внешние MCP (`codex mcp list` пустой), их нужно прописать вручную.

## MCP из research.md: что брать, что не брать

### Спрайты и анимации

1. `willibrandon/pixel-mcp`  
Лучший fit под pixel workflow: генерация и работа со спрайтами/спрайтшитами.

2. `diivi/aseprite-mcp`  
Сильный бэкап/альтернатива, если нужен более "aseprite-first" контроль и API-подход.

3. Остальные Aseprite MCP с низкой зрелостью  
Можно тестировать, но в production-процесс пока не закладывать.

### Карты

1. `tiled-mcp-server`  
Пока экспериментально. Можно пробовать, но не делать на нем критичный pipeline.

2. `phaserjs/editor-mcp-server`  
Больше про Phaser Editor, не про твой pygame-first стек.

3. Практичный прод-путь сейчас  
`Tiled/LDtk` нативно + экспорт + конвертация в формат игры.

### Звук и озвучка

1. `ffmpeg-mcp` (`egoist` или `video-creator`)  
Лучший базовый выбор для локальной, повторяемой обработки SFX/музыки.

2. `mcp-fal`  
Хорош как облачный AI-генератор медиа (опционально, если нужен AI asset generation и ок с API cost).

3. `elevenlabs-mcp`  
Сильный вариант для голоса/реплик.

4. `kokoro-tts-mcp`  
Альтернатива для TTS-потока, если не хочешь ElevenLabs.

## Что установить в первую очередь

1. `Aseprite` (если еще не стоит).
2. `Tiled` (или `LDtk`, но Tiled проще интегрировать в много пайплайнов).
3. `FFmpeg` (системно в PATH).
4. `Node.js LTS` (для npm/npx MCP).
5. `uv` (для Python MCP).
6. `Go` (если будешь собирать `pixel-mcp` из исходников).

## Быстрый setup MCP (минимальный набор)

Ниже ориентиры команд через `codex mcp add`.

### 1) pixel-mcp (основной для спрайтов)

```powershell
git clone https://github.com/willibrandon/pixel-mcp C:\tools\pixel-mcp
cd C:\tools\pixel-mcp
New-Item -ItemType Directory -Force .\bin | Out-Null
go build -o .\bin\pixel-mcp.exe .\cmd\pixel-mcp
codex mcp add pixel -- C:\tools\pixel-mcp\bin\pixel-mcp.exe
```

### 2) aseprite-mcp (backup/advanced)

```powershell
git clone https://github.com/diivi/aseprite-mcp C:\tools\aseprite-mcp
codex mcp add aseprite --env ASEPRITE_PATH="C:\Program Files\Aseprite\Aseprite.exe" -- uv --directory C:\tools\aseprite-mcp run -m aseprite_mcp
```

### 3) ffmpeg-mcp (SFX pipeline)

```powershell
codex mcp add ffmpeg -- npx -y ffmpeg-mcp
```

### 4) elevenlabs-mcp (опционально, для голоса)

```powershell
codex mcp add elevenlabs --env ELEVENLABS_API_KEY="PUT_KEY_HERE" -- uvx elevenlabs-mcp
```

Лучше хранить ключи в переменных окружения ОС, а не оставлять их в истории терминала.

Проверка:

```powershell
codex mcp list
codex mcp get pixel
codex mcp get aseprite
codex mcp get ffmpeg
```

## Лучший workflow для тебя (практичный и быстрый)

### Шаг 1: Зафиксировать asset-контракт

Перед генерацией договоримся о стандарте:

1. Размер тайла: `16x16`.
2. Размер игрока/врагов: `16x16` или `24x24`.
3. Набор анимаций минимум: `idle`, `run`, `jump`, `hit`, `death`.
4. FPS анимаций: 8-12.
5. Именование кадров:  
`assets/sprites/<actor>/<anim>/<actor>_<anim>_00.png`.

### Шаг 2: Генерация спрайтов через MCP

Ты даешь мне короткий бриф, я через MCP делаю итерации:

1. Генерирую базовый idle.
2. На его базе делаю run/jump/hit.
3. Формирую spritesheet + метаданные (JSON).
4. Я сразу подгоняю под твой рендер и pivot.

Рабочий формат запроса ко мне:

`Сделай ghost 16x16, 4 кадра idle + 6 кадров run, палитра cyan/teal, стиль киберпанк, экспорт в assets/sprites/ghost`

### Шаг 3: Интеграция в твой pygame-код

Я:

1. Добавляю loader кадров из папок/atlas.
2. Подменяю procedural sprites в `assets.py` на file-based frames.
3. Оставляю fallback на procedural, чтобы игра не падала при missing PNG.

### Шаг 4: Карты через Tiled/LDtk + конвертация

Самый надежный путь для твоей архитектуры:

1. Рисуешь карту в Tiled/LDtk.
2. Экспортируешь в JSON/TMX.
3. Я запускаю конвертер в твой `rows`-формат (`# ^ p x e t d b`).
4. Обновляю `levels.py` автоматически.

Это дает быстрый результат без полного переписывания `world.py`.

### Шаг 5: Проверка

1. Локальный запуск:
`uv run python -m netrun_platformer`
2. Smoke:
`uv run python -m netrun_platformer --headless-smoke`
3. Я правлю коллизии/offset/anchor после первого прогону.

## Что я рекомендую как "лучший" pipeline именно для тебя

1. Продакшн-основа:
`pixel-mcp + aseprite-mcp + ffmpeg-mcp + Tiled(JSON)->конвертер`.

2. Почему это лучше:
быстро, локально, воспроизводимо, без жесткой зависимости от сырого map-MCP рынка.

3. Что не делать сейчас:
строить core pipeline целиком на экспериментальном map MCP.

4. Когда подключать облачные MCP:
только когда точно нужен AI-generate для музыки/voice, и ты готов к API cost.

## Готовые команды для меня (копируй как задачи)

1. `Сгенерируй спрайты ghost: idle/run/jump в 16x16, собери atlas + json и подключи в assets.py.`
2. `Сделай карту level_01 в Tiled JSON и сконвертируй в rows для levels.py.`
3. `Добавь pipeline scripts: map_json_to_rows.py и spritesheet_to_frames.py.`
4. `Почини коллизии после замены тайлсета и подгони spawn/exit координаты.`
5. `Собери SFX пакет шаг/выстрел/попадание через ffmpeg-mcp и подключи в SoundBank.`

## Источники (актуализированы при подготовке)

1. `research.md` в этом репозитории.
2. Pixel MCP: https://github.com/willibrandon/pixel-mcp
3. Aseprite MCP: https://github.com/diivi/aseprite-mcp
4. FFmpeg MCP: https://github.com/egoist/ffmpeg-mcp
5. MCP FAL: https://github.com/am0y/mcp-fal
6. ElevenLabs MCP: https://github.com/elevenlabs/elevenlabs-mcp
7. Tiled JSON map format: https://doc.mapeditor.org/en/stable/reference/json-map-format/
8. LDtk docs: https://ldtk.io/docs/
